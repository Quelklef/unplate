import inspect
import itertools as it
import textwrap
import ast
from typing import *

# == Copy/pasted itertools recipes == #

def flatten(xss):
  """ Flatten one level of nesting """
  return it.chain.from_iterable(xss)

# == #

class Options:
  def __init__(self):

    # Template bounds
    self.template_left = '['
    self.template_right = ']'

    # Interpolation characters
    self.interpolation_left = '{'
    self.interpolation_right = '}'

    # Character for escaping interpolation characters
    # The escape character itself need not be escaped
    self.escape_char = '\\'

options = Options()

# == #

class ParsingError(ValueError):
  def __init__(self, idx, message):
    self.message = message
    self.idx = idx
    self.source = None

  def __str__(self):
    row, col = char_to_rowcol(self.source, self.idx)
    return f"At ({row}, {col}): {self.message}"


def char_to_rowcol(string: str, target_idx: int):
  """ Convert a string index to a (row, column) pair """
  row = 0
  col = 0
  for char, idx in string:
    if idx == target_idx:
      return (row, col)
    elif char == '\n':
      row += 1
      col = 0
    else:
      col += 1


def transform_source(source_code_loc):
  """
  Main entry point of unplate.

  Transforms some Python source code with interpolated Unplate expression
  into native Python source code.

  Call EXACTLY like this:
    exec(unplate.transform_source(__file__))
  """

  with open(source_code_loc) as f:
    source_code = f.read()

  try:
    transformed = expand_unplate(source_code)
  except ParsingError as e:
    e.source = source_code
    raise e

  # Remove the top-level Unplate call
  transformed = transformed.replace('exec(unplate.transform_source(__file__))', '')

  print('TRANSFORMED:', transformed)
  print("END TRANSFORMED")

  # Assert that there are no syntax errors
  ast.parse(transformed)

  # Don't run the original code after the caller's exec() call
  transformed += "\n\nquit()"

  return transformed


def expand_unplate(code, idx=0):
  """ Given Python + Unplate, expand Unplate into native Python """

  # First, chunk the code into alternating Python source code
  # and Unplate templates, starting with Python source.
  chunks = chunk_code(code, idx)

  # Then, expand the Unplate templates
  expanded = []
  for i, chunk in enumerate(chunks):
    if i % 2 == 0:
      # Python source
      idx += len(chunk)
      expanded.append(chunk)
    else:
      # Unplate template
      idx += len(chunk)
      expanded.append(expand_template(chunk, idx))

  # Finally, combine them and return
  return ''.join(expanded)


def chunk_code(code, idx):
  """ Chunk code into alternating Python source and Unplate templates.
  Guarantees that the sequence starts with Python source, even if that
  source is just an empty string. """

  in_chunk = False
  def boundary(i):
    nonlocal in_chunk

    if i < len(code) - 1 and code[i] + code[i+1] == '#[':
      if in_chunk:
        raise ParsingError(idx + i, "Cannot open a template when already in a template.")
      else:
        in_chunk = True
        return True

    elif i > 2 and code[i-2] + code[i-1] == '#]':
      if in_chunk:
        in_chunk = False
        return True
      else:
        raise ParsingError(idx + i, "Cannot close a template when not in a template.")

    return False

  return chunk(code, boundary)


def chunk(string: str, boundary: Callable[[str], bool]) -> Sequence[str]:

  # One after the index of the final char in the previous chunk
  l = 0

  chunks = []

  for idx in range(len(string)):
    if boundary(idx):
      chunks.append(string[l:idx])
      l = idx

  chunks.append(string[l:])

  return chunks


def expand_template(template: str, idx: int = 0):
  """ Expand an Unplate template source into Python source """
  lines = template.split('\n')

  assert len(lines) > 0, "Cannot expand empty Unplate template."

  # Remove '#[' and '#]'
  lines = lines[1:-1]

  def unwrap(line):
    """ Unwrap an Unplate source line into its content """
    stripped = line.lstrip()
    assert stripped.startswith('# ')
    return stripped[len('# '):]

  unplate_code = '\n'.join(map(unwrap, lines))
  python_code = f'+ unplate.compile("""{unplate_code}""", locals()) '
  return python_code

def compile(template: str, context: Dict[str, Any]):
  """ Compile a template with the given context. """

  # For now, just use a naive algorithm

  # Chunks of string to be .join()'d in the end
  result_chunks = []

  # One after the index of the final char in the previous chunk
  l = 0

  # Are we in an interpolated expression?
  in_expression = False

  template_len = len(template)

  char_idx = -1
  while True:
    char_idx += 1
    if char_idx == template_len: break

    char = template[char_idx]
    next_char = template[char_idx + 1] if char_idx < template_len - 1 else None

    # =

    if char == options.escape_char:
      if next_char == options.interpolation_left:
        # Escaped open interpolation
        result_chunks.append(template[l:char_idx] + options.interpolation_left)
        char_idx += 1
        l = char_idx + 1

      if next_char == options.interpolation_right:
        # Escaped close interpolation
        result_chunks.append(template[l:char_idx] + options.interpolation_right)
        char_idx += 1
        l = char_idx + 1

    elif char == options.interpolation_left:
      # Unesacped open interpolation
      in_expression = True
      result_chunks.append(template[l:char_idx])
      l = char_idx + 1

    elif char == options.interpolation_right:
      # Unescaped close interpolation
      if not in_expression:
        raise ParsingError(char_idx, f"Interpolation closing marker '{options.close_interpolation}' illegal here we were not in an interpolated expression.")
      # Switch states
      in_expression = False

      # Get the captured expression
      expression = template[l:char_idx]

      # Evaluate it and append it
      value = eval(expression, context)
      result_chunks.append(value)

    elif next_char == None:
      # At the end of the string
      final_chunk = template[l:]
      result_chunks.append(final_chunk)

    else:
      pass


  # Calculate the final string from the chunks
  result = ''.join(map(str, result_chunks))
  return result
