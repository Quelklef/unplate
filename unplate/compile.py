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


def read_template_body(tokens, indents):
  """
  Consume one or more contiguous comments, or a single string.
  Find the contained text.

  In the case of comments, require and consume a leading space
  from the beginning of each comment (e.g.: "# content" -> "content")

  In the case of a string, assert that there are leading and
  trailing lines are empty (whitspace-only), and remove them.
  Additonally, un-indent the contents according to the indent stack.
  """

  if tokens[0].type == tk.STRING:
    code = tokens[0].string

    is_multiline_string = len(set(code[:3])) == 1
    if is_multiline_string:
      content = code[3:-3]
    else:
      content = code[1:-1]

    lines = content.split('\n')

    if lines[0].strip() != '':
      raise UnplateSyntaxError.from_token(tokens[0],
        "A template using a Python string literal must begin with a newline.")

    if lines[-1].strip() != '':
      raise UnplateSyntaxError.from_token(tokens[0],
        "A template using a Python string literal must end with a newline.")

    # remove leading blank line
    lines.pop(0)
    # remove trailing blank line
    lines.pop(-1)

    # dedent
    dedented = []
    indent = indents[-1] if indents else ''
    for line in lines:

      # We make a special exception for lines that are only whitespace.
      # We want to allow blank lines to be part of an indended block. However,
      # we don't want to consider all whitespace-only lines as blank lines,
      # in case there is e.g. an embedded multiline string.
      # The compromise is to allow all whitespace-only lines, but 'subtract'
      # the current indent from them, down to a minimum of no indentation.
      if line.strip() == '':
        dedented_line = line[len(indent):]
        dedented.append(dedented_line)

      # normal case:
      # assert then strip indentation
      else:
        if not line.startswith(indent):
          raise UnplateSyntaxError.from_token(tokens[0],
            f"A template using a Python string literal must be indented according to the surrounding block.")
        dedented.append(line[len(indent):])

    return dedented, tokens[1:]

  else:
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


def repr_with_newlines(string):
  """
  return the string, passed through repr(), but with
  newlines intact.

  Thus the string "new\nline" becomes not "new\\nline" but instead
  a string with a literal newline in it: '''new
line'''
  """

  # single-line string
  if '\n' not in string:
    return repr(string)

  # multiline string
  else:
    reprd = repr(string)

    # either ' or ", depending on how repr() decides to handle escapes
    quote_type = reprd[0]

    newlines_returned = reprd.replace('\\n', '\n')
    multiline_quotes = quote_type * 2 + newlines_returned + quote_type * 2
    return multiline_quotes


def compile_content(string):
  """
  Given a string which is the literal content of a template,
  return the Python code for the runtime interpretation of that string.
  For instance, given

    "<h1>{{ title }}</h1>"

  returns (something like)

    "<h1>" + str(title) + "</h1>"

  If the given string contains newlines, these will be preserved in the
  returned code. Thus

    '''first line {{ interpolated }}
    second line'''

  is mapped to (something like)

    "'first line' + str(interpolated) + '''
    second line'''"

  """

  # resultant `exprs` will be a sequence of python expressions which
  # are to be concatenated in the end
  # For example, exprs may be ['"<h1>"', 'str(title)', '"</h1>"']
  exprs = []

  # are we in a string or in an interpolated expression?
  in_expr = False

  # index of the beginning of the current chunk
  # a chunk is either a section of the string which
  # is either literal string or interpolated code
  chunk_start = 0

  def end_chunk():
    chunk = string[chunk_start:i]

    if in_expr:
      code = f"str({chunk})"
    else:
      code = repr_with_newlines(chunk)

    exprs.append(code)

  i = -1
  while True:
    i += 1
    if i >= len(string):
      break

    char = string[i]
    next_char = string[i + 1] if i + 1 < len(string) else None

    if (char, next_char) == ('{', '{'):
      end_chunk()

      # skip over braces
      i += 2
      chunk_start = i

      in_expr = True

    elif in_expr and (char, next_char) == ('}', '}'):
      end_chunk()

      # skip over braces
      i += 2
      chunk_start = i

      in_expr = False

  end_chunk()

  # now we have a bunch of expressions
  # at runtime, they'll need to be joined together
  # we'll do that with ''.join()
  list_expr = '[' + ', '.join(exprs) + ']'
  code = f"''.join({list_expr})"

  return code


def consume_prefix(tokens, literal):
  if not util.prefix_is(tokens, literal):
    expected = tku.untokenize(literal)
    actual = tku.untokenize(tokens[:len(literal)])
    raise UnplateSyntaxError.from_token(tokens[0], f"Expected: {repr(expected)} but got {repr(actual)}")
  return tokens[len(literal):]


def compile_template_literal(tokens, indents):
  tokens = consume_prefix(tokens, parameters.template_literal_open)
  lines, tokens = read_template_body(tokens, indents)
  tokens = consume_prefix(tokens, parameters.template_literal_close)

  content = ''.join(line + '\n' for line in lines)
  compiled = tku.tokenize_expr(compile_content(content))

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
      # {{ color }} line
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

  # consume @ if present
  if tokens[0] == tku.dtok.new(tk.OP, '@'):
    tokens.pop(0)

  init_statement = tku.tokenize_stmt(f"{template_name} = []\n")
  compiled.extend(init_statement)

  # Consume leading newline
  while tokens[0].type == tk.NEWLINE:
    tokens.pop(0)

  body_token = tokens[0]
  lines, tokens = read_template_body(tokens, indents)

  # keep track of how many times we've indended in interpolated code
  interpolated_indent_depth = 0

  for line in lines:

    # interpolated python code
    if line.lstrip().startswith('>>>'):

      if not line.lstrip().startswith('>>> '):
        raise UnplateSyntaxError.from_token(body_token, "A space is required after '>>>'")

      python_code = line.lstrip()[len('>>> '):]
      compiled.extend(tku.tokenize_stmt(python_code))
      compiled.append(tku.dtok.new(tk.NEWLINE, '\n'))

      needs_indent = line.strip().endswith(':')
      if needs_indent:
        current_indent = indents[-1] if indents else ''
        bumped = current_indent + '  '
        indents.append(bumped)
        interpolated_indent_depth += 1
        compiled.append(tku.dtok.new(tk.INDENT, bumped))

    elif line.lstrip().startswith('<<<'):

      if line.strip() != '<<<':
        raise UnplateSyntaxError.from_token(body_token, "Nothing is allowed on a line with '<<<'")

      if interpolated_indent_depth == 0:
        raise UnplateSyntaxError.from_token(body_token, "Too many dedents.")

      compiled.append(tku.dtok.new(tk.NEWLINE, '\n'))
      compiled.append(tku.dtok.new(tk.DEDENT, ''))
      indents.pop(-1)
      interpolated_indent_depth -= 1

    else:
      content = tku.tokenize_expr(compile_content(line) + " + '\\n'")
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
      compiled_toks, tokens = compile_template_literal(tokens, indents)
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

