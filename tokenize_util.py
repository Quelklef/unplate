import tokenize as tk
import itertools as it
import operator
import io


class dtok(tk.TokenInfo):
  """
  Represents a "detached" token, which is just
  like a regular token but doesn't care about its
  positional information.

  This entire module uses dtoks instead of
  tokenize.TokenInfo instances.
  """

  def __eq__(self, other):

    if self.type != other.type:
      return False

    # Types for which the content should be compared
    contentful = [
      tk.NAME,
      tk.NUMBER,
      tk.STRING,
      # not 100% sure about these other ones
      #tk.TYPE_COMMENT,
      tk.ERRORTOKEN,
      tk.N_TOKENS,
      tk.NT_OFFSET,
      tk.ENCODING,
    ]

    if self.type in contentful:
      return self.string == other.string
    else:
      return True

  def __str__(self):
    return f"{self.type}({repr(self.string)})"

  def __repr__(self):
    return f"dtok.new({tk.tok_name[self.type]}, {repr(self.string)})"

  @staticmethod
  def new(type, string):
    """
    Construct a dtoken.
    This method exists because __init__ cannot effectively be
    overrid when subclassing a NamedTuple (as far as I know)
    """
    return dtok(type, string, None, None, None)

  @staticmethod
  def from_token(token):
    return dtok(
      token.type,
      token.string,
      token.start,
      token.end,
      token.line,
    )


def tokenize_string(string):
  fake_io = io.StringIO(string)
  tokens = list(tk.generate_tokens(fake_io.readline))
  dtoks = [dtok.from_token(tok) for tok in tokens]
  return dtoks


def tokenize_stmt(string):
  """ Tokenize a string, removing trailing EOF token. """
  tokens = tokenize_string(string)

  assert tokens[-1].type == tk.ENDMARKER
  tokens = tokens[:-1]

  return tokens

def tokenize_expr(string):
  """ Tokenize a string, removing trailing NEWLINE and EOF tokens. """
  tokens = tokenize_string(string)

  assert tokens[-1].type == tk.ENDMARKER
  tokens = tokens[:-1]

  assert tokens[-1].type == tk.NEWLINE
  tokens = tokens[:-1]

  return tokens


def tokenize_one(string):
  """ Tokenize a single token """
  tokens = tokenize_expr(string)
  assert len(tokens) == 1, tokens
  return tokens[0]


def tokenize_file(file_loc):
  """ Tokenize a file """
  with open(file_loc, 'r') as f:
    code = f.read()
  return tokenize_string(code)


def untokenize(tokens):
  return tk.untokenize( (tok.type, tok.string) for tok in tokens )


def split_pattern(pattern_toks, marker):
  """
  Take a pattern and a marker.
  The pattern should be a list of dtoks and the marker should be
  a small bit of Python code (usually a variable name).
  Tokenize both and return the pattern split around the marker.

  For instance:
    split_pattern(tokenize_expr("list[IDX]"), "IDX")
  will return a tuple (prefix, suffix) where
    prefix is the tokens for "list["
    suffix is the tokens for "]"
  """
  marker_tok = tokenize_one(marker)
  marker_idx = pattern_toks.index(marker_tok)
  return pattern_toks[:marker_idx], pattern_toks[marker_idx+1:]
