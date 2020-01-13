import tokenize as tk

from tokenize_util import tokenize_fragment, detach_token, tokenize_string
from options import options
import util

"""

Code relating to transforming Python + Unplate source code
into native Python source code.

"""

class ParsingError(ValueError):
  def __init__(self, start_loc, end_loc, message):
    self.message = message
    self.start_loc = start_loc
    self.end_loc = end_loc

  def __str__(self):
    row_0, col_0 = self.start_loc
    row_f, col_f = self.end_loc
    return f"At ({row_0}, {col_0}) through ({row_f}, {col_f}): {self.message}"


def transform_code(code):
  """ Transform Python + Unplate source into native Python source """
  tokens = tokenize_string(code)
  transformed = list(transform_tokens(tokens))
  result_code = tk.untokenize( (tok.type, tok.string) for tok in transformed )
  return result_code


def is_template_comment(token):
  """ Is the token a comment that is part of an Unplate template? """
  return token.type == tk.COMMENT and token.string.startswith('#' + options.prefix)


def transform_tokens(tokens):
  """ Given an Python tokens that represent Python + Unplate code,
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
        raise ParsingError(start, end,
          "Cannot open a template when already in a template.")

      else:
        # Skip over the opening sequence
        util.next_n(token_enum, len(options.open_tokens) - 1)
        # Set state to in template
        template_tokens.clear()
        in_template = True

    elif in_template and prefix_is(options.close_tokens):
      # Found a template closer

      # Calculate and yield results
      yield from expand_template(template_tokens)
      # Skip over closing sequence
      util.next_n(token_enum, len(options.close_tokens) - 1)
      # Set state to out of template
      in_template = False

    elif in_template:
      template_tokens.append(token)

    elif is_template_comment(token):
      # Found a template comment outside of a templte
      if not options.allow_template_comment_outside_template:
        raise ParsingError(token.start, token.end,
          f"Template comments (comments starting with '#{options.prefix}') are not allowed outside of templates.")

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
      if not is_template_comment(token):
        raise ParsingError(token.start, token.end,
          f"Comments denoting templates must be prefixed with '#{options.prefix}'.")

      return token.string[len('#' + options.prefix):]

    else:
      # e.g. NEWLINE
      return token.string

  # Get the template string
  contents = ''.join(map(parse_token, tokens))

  # Repr-out to Python source but preserve newlines and drop opening and closing quotes
  contents_python = repr(contents).replace('\\n', '\n')[1:-1]
  # Generate the tokens for target Python code
  python_code = f' unplate.compile("""\n{contents_python}\n"""[1:-1], locals()) '
  return tokenize_fragment(python_code)
