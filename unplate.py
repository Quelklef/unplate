import inspect
import itertools as it
import textwrap
import tokenize as tk
import io

def flatten(xss):
  """ Flatten one level of nesting """
  return it.chain.from_iterable(xss)


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

  @property
  def template_open(self):
    return f'#{self.template_left}'

  @property
  def template_close(self):
    return f'#{self.template_right}'

options = Options()


class ParsingError(ValueError):
  def __init__(self, start_loc, end_loc, message):
    self.message = message
    self.start_loc = start_loc
    self.end_loc = end_loc

  def __str__(self):
    row, col = self.start_loc
    return f"At ({row}, {col}): {self.message}"


def magic(source_code_loc):
  """
  Main entry point of unplate.

  Transforms some Python source code with interpolated Unplate expression
  into native Python source code.

  Call EXACTLY like this:
    exec(unplate.transform_source(__file__))
  """

  with open(source_code_loc) as file:
    tokens = tk.generate_tokens(file.readline)
    transformed = transform_tokens(tokens)
    result_code = tk.untokenize( (tok.type, tok.string) for tok in transformed )

  # Remove the top-level Unplate call
  # Weird-ass spacing is courtesy of untokenize
  unplate_call = 'exec (unplate .magic (__file__ ))'
  assert unplate_call in result_code, "Something fucky is about"
  result_code = result_code.replace(unplate_call, '')

  # Don't run the original code after the caller's exec() call
  # TODO: What if this gets commented out, e.g. by a multiline string?
  result_code += "\n\nquit()"

  return result_code


def transform_tokens(token_it, idx=0):
  """ Given an iterator of Python tokes that represent Python + Unplate code,
  compile the Unplate code and yield results.
  Results will be a mix of unmodified tokens and raw Python code as strings. """

  # List of tokens in current template
  template_tokens = []

  # Are we in a template?
  in_template = False

  for token in token_it:

    if token.type == tk.COMMENT and token.string.startswith(options.template_open):
      # Found a template opener
      if in_template:
        raise ParsingError(token.start, token.end, "Cannot open a template when already in a template.")
      else:
        template_tokens.clear()
        in_template = True

    elif token.type == tk.COMMENT and token.string.startswith(options.template_close):
      # Found a template closer
      if not in_template:
        raise ParsingError(token.start, token.end, "Cannot close a template when not in a template.")
      else:
        yield from expand_template(template_tokens)
        in_template = False

    elif in_template:
      template_tokens.append(token)

    else:
      # A token that has nothing to do with Unplate
      yield token


def expand_template(tokens):
  """
  Expand Umplate source tokens into Python source tokens.
  The source tokens will be "isolated", meaning that they will
  have None for their start, end, and line attributes.
  """

  # Discard the open and closing tokens
  tokens = tokens[1:-1]

  def parse_token(token):
    if token.type != tk.COMMENT:
      # e.g. newline tokens
      return token.string

    if not token.string.startswith('# '):
      raise ParsingError(token.start, token.end, "Unplate mandates spaces after template commends.")
    return token.string[2:]

  # Get the template string
  contents = ''.join(map(parse_token, tokens))

  # TODO: repr() might not be strong enough

  # Repr-out to Python source but preserve newlines and drop opening and closing quotes
  contents_python = repr(contents).replace('\\n', '\n')[1:-1]
  # Generate the tokens for target Python code
  python_code = f' + unplate.compile("""\n{contents_python}\n"""[1:-1], locals()) '
  fake_io = io.StringIO(python_code)
  generated_tokens = tk.generate_tokens(fake_io.readline)
  return generated_tokens


def compile(template, context):
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
        raise ParsingError(char_to_rowcol(template, char_idx), None, f"Interpolation closing marker '{options.close_interpolation}' illegal here since we were not in an interpolated expression.")

      # Switch states
      in_expression = False

      # Get the captured expression
      expression = template[l:char_idx]
      l = char_idx + 1

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
