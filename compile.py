import tokenize as tk
import tokenize_util as tku
import parameters
import itertools as it
import util

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


def is_template_comment(token):
  """ Is the token a comment that is part of an Unplate template? """

  prefixes = [parameters.interpolation_prefix, parameters.verbatim_prefix]

  return token.type == tk.COMMENT and any(
    token.string.startswith('#' + prefix)
    for prefix in prefixes
  )


def read_template_comments(tokens):
  """
  Consume one or more contiguous template comments and finds the the body code as a string.
  So for tokens representing

    #$ line one
    #$ line two

  finds the string "line one\nline two\n"

  Returns a 3-tuple (content, prefix, tokens) where
    content: is the contained string "line one\nline two\n"
    prefix: is the comment prefix, e.g. '$'
    tokens: are the remaining tokens

  """
  template_comments_and_newlines = list(it.takewhile(
    lambda tok: tok.type == tk.NL or is_template_comment(tok),
    tokens
  ))

  # remove newlines
  template_comments = [
    token for token in template_comments_and_newlines
    if token.type == tk.COMMENT
  ]

  if not template_comments:
    raise UnplateSyntaxError.from_token(tokens[0],
      "Expected a template comment but found none.")

  # Ensure that all the comments have the same prefix
  # TODO: assumes that prefixes are two characters
  expected_prefix = template_comments[0].string[1:3]
  for comment in template_comments:
    prefix = comment.string[1:3]
    if prefix != expected_prefix:
      raise UnplateSyntaxError.from_token(comment,
        f"Expected prefix '{expected_prefix}' since that's what preceded, but got prefix '{prefix}'")

  # Stich together contents
  # TODO: assumes that prefixes are two characters
  texts = [comment.string[3:] for comment in template_comments]
  result = ''.join(text + '\n' for text in texts)

  rest_tokens = tokens[len(template_comments_and_newlines):]
  return result, expected_prefix, rest_tokens


def consume_prefix(tokens, literal):
  if not util.prefix_is(tokens, literal):
    expected = tku.untokenize(literal)
    actual = tku.untokenize(tokens[:len(literal)])
    raise UnplateSyntaxError.from_token(tokens[0], f"Expected: {repr(expected)} but got {repr(actual)}")
  return tokens[len(literal):]


def compile_template_comments(tokens):
  content, prefix, tokens = read_template_comments(tokens)

  # repr-out to Python source but preserve newlines and strip quotes
  content_python = repr(content).replace('\\n', '\n')[1:-1]

  # Generate the python code
  if prefix == parameters.interpolation_prefix:
    compiled_code = f'f"""{content_python}"""'
  elif prefix == parameters.verbatim_prefix:
    compiled_code = f'"""{content_python}"""'
  else:
    raise RuntimeError(f"Programmer forgot a case: '{prefix}'")

  compiled = tku.tokenize_expr(compiled_code)
  return compiled, tokens


def compile_template_literal(tokens):
  tokens = consume_prefix(tokens, parameters.template_literal_open)
  compiled, tokens = compile_template_comments(tokens)
  tokens = consume_prefix(tokens, parameters.template_literal_close)
  # Pad compiled code to preserve line numbers
  pad = tku.tokenize_expr('(\n)')
  compiled = pad[:2] + compiled + pad[2:]
  return compiled, tokens


def compile_template_builder(tokens):

  compiled = []

  tokens = consume_prefix(tokens, parameters.template_builder_open_left)
  # get the name of the result template
  variable_name = tokens.pop(0).string
  tokens = consume_prefix(tokens, parameters.template_builder_open_right)

  init_statement = tku.tokenize_stmt(f"{variable_name} = []\n")
  compiled.extend(init_statement)

  while tokens:

    # template comments now get compiled into statements adding onto the builder
    if is_template_comment(tokens[0]):
      compiled_toks, tokens = compile_template_comments(tokens)

      # not entirely sure why the following line needs a trailing \n
      pattern = tku.tokenize_stmt(f'{variable_name}.append(VALUE)\n')
      prefix, suffix = tku.split_pattern(pattern, 'VALUE')
      statement = prefix + compiled_toks + suffix
      compiled.extend(statement)

    if util.prefix_is(tokens, parameters.template_builder_close):
      tokens = consume_prefix(tokens, parameters.template_builder_close)
      break

    else:
      compiled.append(tokens.pop(0))

  closing_statement = tku.tokenize_stmt(f"{variable_name} = ''.join({variable_name})")
  compiled.extend(closing_statement)

  return compiled, tokens


def compile_tokens(tokens):
  """
  Given Python tokens that represent Python + Unplate code, compile the Unplate code and return results.
  Results will be a mix of unmodified tokens and raw Python code (as strings).
  """

  compiled = []

  while tokens:

    if util.prefix_is(tokens, parameters.template_literal_open):
      compiled_toks, tokens = compile_template_literal(tokens)
      compiled.extend(compiled_toks)

    elif util.prefix_is(tokens, parameters.template_builder_open_left):
      compiled_toks, tokens = compile_template_builder(tokens)
      compiled.extend(compiled_toks)

    elif is_template_comment(tokens[0]):
      # Found a template comment outside of a template
      raise UnplateSyntaxError.from_token(tokens[0], file_loc,
        f"This line appears to contain a comment intended to be within an Unplate template, but the line is outside of any templates.")

    else:
      compiled.append(tokens.pop(0))

  return compiled, tokens

