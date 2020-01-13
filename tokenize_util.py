import tokenize as tk
import itertools as it
import io

def tokenize_string(string):
    # generate tokens
  fake_io = io.StringIO(string)
  tokens = list(tk.generate_tokens(fake_io.readline))

  return tokens


def tokenize_fragment(string):
  """ Tokenize a string and remove the EOF and ALL newline tokens """
  tokens = tokenize_string(string)

  # remove EOF
  assert tokens[-1].type == tk.ENDMARKER
  tokens = tokens[:-1]

  # remove newlines
  is_newline = lambda token: token.type == tk.NEWLINE
  tokens = list(it.filterfalse(is_newline, tokens))

  return tokens


def tokenize_one(string):
  """ Tokenize a string into one token """
  tokens = tokenize_fragment(string)
  assert len(tokens) == 1
  return tokens[0]


def detach_token(token):
  """ Remove a token's positional information """
  return tk.TokenInfo(
    type   = token.type,
    string = token.string,
    start  = None,
    end    = None,
    line   = None,
  )

