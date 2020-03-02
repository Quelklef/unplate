import tokenize as tk
import itertools as it
import unplate.tokenize_util as tku
import unplate.parameters as parameters
import unplate.util as util

"""

Code relating to compiling Python + Unplate source code into native Python source code.

"""


class UnplateSyntaxError(SyntaxError):
  def __init__(self, file_loc, lineno, offset, text, message):
    super().__init__(message)

    # Inherited attributes
    self.file_loc = file_loc  # actually called .filename in SyntaxError
    self.lineno   = lineno
    self.offset   = offset
    self.text     = text

  @property
  def filename(self):
    # SyntaxError expects a .filename, not a .file_loc
    return self.file_loc

  @staticmethod
  def from_token(token, message, *, file_loc=None):
    """ Make an UnplateSyntaxError using the information from a token """

    # Much of the time, the filename won't be given and will
    # be injected higher up in the call stack than the error creation

    return UnplateSyntaxError(
      file_loc = file_loc,
      lineno   = token.start[0],
      offset   = token.start[1],
      text     = token.string,
      message  = message,
    )


def compile_top(tokens, *, file_loc):
  """
  Top-level compilation function.
  Transform Python + Unplate source tokens into native Python source tokens.
  """

  try:
    compiled, rest = compile_tokens(tokens)
  except UnplateSyntaxError as err:
    err.file_loc = file_loc
    raise err

  if rest:
    raise UnplateSyntaxError.from_token(rest[0], file_loc=file_loc,
      message="Unacceptable leftover tokens.")

  return compiled


def read_template_body(tokens):
  """
  Consume one or more contiguous comments, or a single string.
  Find the containd text.
  """

  if tokens[0].type == tk.STRING:
    return tokens[0].string, tokens[1:]

  comment_block = list(it.takewhile(
    lambda tok: tok.type in [tk.NL, tk.COMMENT],
    tokens
  ))

  comments = [tok for tok in comment_block if tok.type is tk.COMMENT]

  for comment in comments:
    if not comment.string.startswith('# '):
      raise UnplateSyntaxError.from_token(comments[0], "Spaces are mandated after '#' in templates.")

  # [2:] to strip leading space
  lines = [comment.string[2:] for comment in comments]
  rest_tokens = tokens[len(comment_block):]
  return lines, rest_tokens


def repr_template_content(string):
  """
  repr-out a string but preserve newlines.
  Intended for use injecting the content of a template back
  into the python source.
  """
  inner = repr(string).replace('\\n', '\n')[1:-1]
  # TODO: not sure where to place the "make this an f-string" bit of code
  return f'f"""{inner}"""'


def consume_prefix(tokens, literal):
  if not util.prefix_is(tokens, literal):
    expected = tku.untokenize(literal)
    actual = tku.untokenize(tokens[:len(literal)])
    raise UnplateSyntaxError.from_token(tokens[0], f"Expected: {repr(expected)} but got {repr(actual)}")
  return tokens[len(literal):]


def compile_template_literal(tokens):
  tokens = consume_prefix(tokens, parameters.template_literal_open)
  lines, tokens = read_template_body(tokens)
  tokens = consume_prefix(tokens, parameters.template_literal_close)

  content = ''.join(line + '\n' for line in lines)
  compiled = tku.tokenize_expr(repr_template_content(content))

  # Pad compiled code to preserve line numbers
  pad = tku.tokenize_expr('(\n)')
  compiled = pad[:2] + compiled + pad[2:]

  return compiled, tokens


def compile_template_builder(tokens, indents):
  """
  Consume and compile a template builder construct ala

    [unplate.begin(template_name)]
    # One line
    # Two line
    # >>> for color in ['red', 'blue']:
      # >>> capitalized = color.upper()
      # {color} line
    # <<<
    [unplate.end]

  Requires the indent stack.
  """

  indents = indents[:]

  compiled = []

  tokens = consume_prefix(tokens, parameters.template_builder_open_left)
  # get the name of the result template
  template_name = tokens.pop(0).string
  tokens = consume_prefix(tokens, parameters.template_builder_open_right)

  init_statement = tku.tokenize_stmt(f"{template_name} = []\n")
  compiled.extend(init_statement)

  # Consume trailing newline
  while tokens[0].type == tk.NEWLINE:
    tokens.pop(0)

  body_token = tokens[0]
  lines, tokens = read_template_body(tokens)

  indent_depth = 0
  for line in lines:

    # interpolated python code
    if line.strip().startswith('>>>'):

      if not line.strip().startswith('>>> '):
        raise UnplateSyntaxError.from_token(body_token, "A space is required after '>>>'")

      python_code = line[len('>>> '):]
      compiled.extend(tku.tokenize_stmt(python_code))
      compiled.append(tku.dtok.new(tk.NEWLINE, '\n'))

      needs_indent = line.strip().endswith(':')
      if needs_indent:
        whitespace = ''.join(indents) + ' '
        indents.append(whitespace)
        compiled.append(tku.dtok.new(tk.INDENT, whitespace))

    elif line.strip().startswith('<<<'):

      if line.strip() != '<<<':
        raise UnplateSyntaxError.from_token(body_token, "Nothing is allowed on a line with '<<<'")

      compiled.append(tku.dtok.new(tk.NEWLINE, '\n'))
      compiled.append(tku.dtok.new(tk.DEDENT, ''))
      indents.pop(-1)

    else:
      content = tku.tokenize_expr(repr_template_content(line + '\n'))
      # not entirely sure why the following line needs a trailing \n
      pattern = tku.tokenize_stmt(f'{template_name}.append(VALUE)\n')
      prefix, suffix = tku.split_pattern(pattern, 'VALUE')
      statement = prefix + content + suffix
      compiled.extend(statement)

  # consume the template closing syntax
  tokens = consume_prefix(tokens, parameters.template_builder_close)

  closing_statement = tku.tokenize_stmt(f"{template_name} = ''.join({template_name})")
  compiled.extend(closing_statement)

  return compiled, tokens


def compile_tokens(tokens):
  """
  Given Python tokens that represent Python + Unplate code, compile the Unplate code and return results.
  Results will be a mix of unmodified tokens and raw Python code (as strings).
  """

  compiled = []

  # Keep track of the indentation
  # Each time an indent is reached, push the indentation
  # text (i.e. the actual whitespace) onto this stack
  # Each time a dedent is reached, pop the most recent value
  # off of the stack
  indents = []

  while tokens:
    token = tokens[0]

    if util.prefix_is(tokens, parameters.template_literal_open):
      compiled_toks, tokens = compile_template_literal(tokens)
      compiled.extend(compiled_toks)

    elif util.prefix_is(tokens, parameters.template_builder_open_left):
      compiled_toks, tokens = compile_template_builder(tokens, indents)
      compiled.extend(compiled_toks)

    if token.type == tk.INDENT:
      indents.append(token.string)
      compiled.append(tokens.pop(0))

    elif token.type == tk.DEDENT:
      indents.pop(-1)
      compiled.append(tokens.pop(0))

    else:
      compiled.append(tokens.pop(0))

  return compiled, tokens

