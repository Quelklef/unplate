import tokenize as tk
import itertools as it
import io


def tokenize_fragment(string):
  """ Tokenize a string and remove the EOF and ALL newline tokens """

  # generate tokens
  fake_io = io.StringIO(string)
  tokens = list(tk.generate_tokens(fake_io.readline))

  # remove EOF
  assert tokens[-1].type == tk.ENDMARKER
  tokens = tokens[:-1]

  # remove newlines
  is_newline = lambda token: token.type == tk.NEWLINE
  tokens = list(it.filterfalse(is_newline, tokens))

  return tokens


def detach_token(token):
  """ Remove a token's positional information """
  return tk.TokenInfo(
    type   = token.type,
    string = token.string,
    start  = None,
    end    = None,
    line   = None,
  )


def next_n(it, n):
  """ Repeat next() n times """
  for _ in range(n):
    next(it)


class Options:
  def __init__(self):

    # Tokens for opening a template
    # TODO: it would be nice if the user could set,
    #       say, options.template_code = "unplate.template(TEMPLATE)"
    #       and it would auto-generate these two attributes.
    template_call_tokens = tokenize_fragment('unplate.template(\nTEMPLATE\n)')
    self.open_tokens = template_call_tokens[:-3]
    self.close_tokens = template_call_tokens[-2:]

    # Interpolation characters
    self.interpolation_left = '{'
    self.interpolation_right = '}'

    # Character for escaping interpolation characters
    # The escape character itself need not be escaped
    self.escape_char = '\\'

options = Options()


class ParsingError(ValueError):
  def __init__(self, start_loc, end_loc, message):
    self.message = message
    self.start_loc = start_loc
    self.end_loc = end_loc

  def __str__(self):
    row_0, col_0 = self.start_loc
    row_f, col_f = self.end_loc
    return f"At ({row_0}, {col_0}) through ({row_f}, {col_f}): {self.message}"


def magic(source_code_loc):
  """
  Main entry point of unplate.

  Transforms some Python source code with interpolated Unplate expression
  into native Python source code.

  Call EXACTLY like this:
    exec(unplate.transform_source(__file__))
  """

  with open(source_code_loc) as file:
    tokens = list(tk.generate_tokens(file.readline))
  transformed = list(transform_tokens(tokens))
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


def transform_tokens(tokens, idx=0):
  """ Given an iterator of Python tokes that represent Python + Unplate code,
  compile the Unplate code and yield results.
  Results will be a mix of unmodified tokens and raw Python code as strings. """

  # List of tokens in current template
  template_tokens = []

  # Are we in a template?
  in_template = False

  def prefix_is(prefix):
    """ Do the upcoming tokens match the given prefix in content? """
    # Match the length of upcoming
    upcoming = tokens[token_idx:token_idx+len(prefix)]
    # Detach tokens in both
    upcoming = map(detach_token, upcoming)
    prefix = map(detach_token, prefix)
    # Check if equal
    return list(upcoming) == list(prefix)

  token_enum = enumerate(tokens)
  for token_idx, token in token_enum:

    if prefix_is(options.open_tokens):
      # Found a template opener

      if in_template:
        start = tokens[token_idx].start
        end = tokens[token_idx + len(options.open_tokens) - 1].end
        raise ParsingError(start, end, "Cannot open a template when already in a template.")

      else:
        # Skip over the opening sequence
        next_n(token_enum, len(options.open_tokens) - 1)
        # Set state to in template
        template_tokens.clear()
        in_template = True

    elif in_template and prefix_is(options.close_tokens):
      # Found a template closer

      # Calculate and yield results
      yield from expand_template(template_tokens)
      # Skip over closing sequence
      next_n(token_enum, len(options.close_tokens) - 1)
      # Set state to out of template
      in_template = False

    elif in_template:
      template_tokens.append(token)

    else:
      # A token that has nothing to do with Unplate
      yield token


def expand_template(tokens):
  """
  Expand Umplate source tokens into Python source tokens.
  The source tokens will be "detached", meaning that they will
  have None for their start, end, and line attributes.
  """

  def parse_token(token):

    if token.type == tk.COMMENT:
      if not token.string.startswith('# '):
        raise ParsingError(token.start, token.end, "Unplate mandates spaces after template commends.")
      return token.string[2:]

    else:
      # e.g. NEWLINE
      return token.string

  # Get the template string
  contents = ''.join(map(parse_token, tokens))

  # TODO: repr() might not be strong enough

  # Repr-out to Python source but preserve newlines and drop opening and closing quotes
  contents_python = repr(contents).replace('\\n', '\n')[1:-1]
  # Generate the tokens for target Python code
  python_code = f' unplate.compile("""\n{contents_python}\n"""[1:-1], locals()) '
  return tokenize_fragment(python_code)


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
        poisiton = char_to_rowcol(template, char_idx)
        raise ParsingError(position, position, f"Interpolation closing marker '{options.close_interpolation}' illegal here since we were not in an interpolated expression.")

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


def template(*args, **kwargs):
  raise Exception("Something's gone wrong. You should never actually invoke unplate.template().")
