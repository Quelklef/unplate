import tokenize as tk
import itertools as it
import operator
import io


def tokenize_string(string):
  fake_io = io.StringIO(string)
  tokens = list(tk.generate_tokens(fake_io.readline))
  return tokens


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


def detach_token(token):
  """ Remove a token's positional information """
  return tk.TokenInfo(
    type   = token.type,
    string = token.string,
    start  = None,
    end    = None,
    line   = None,
  )


def content_eq(tokenA, tokenB):
  return detach_token(tokenA) == detach_token(tokenB)


def list_eq(li1, li2, eq=operator.eq):
  return len(li1) == len(li2) and all( eq(li1[i], li2[i]) for i in range(len(li1)) )


def has_sublist(superlist, sublist, eq=operator.eq):
  """
  Does a list contain another list within it?
  Not very efficient.
  If 'eq' is given, this will be used to compare items.
  """
  return any(
    list_eq(superlist[i : i + len(sublist)], sublist, eq=eq)
    for i in range(len(superlist) - len(sublist) + 1)
  )


def replace_sublist(li, target, replacement, eq=operator.eq):
  """
  Replace a sublist with another sublist.
  Not very effcient.
  If 'eq' is given, this will be used to compare items.
  """
  result = []
  i = 0
  while i < len(li):
    if list_eq(li[i : i + len(target)], target, eq=eq):
      i += len(target)
      result.extend(replacement)
    else:
      result.append(li[i])
      i += 1
  return result


def remove_sublist(li1, li2, eq=operator.eq):
  """
  Remove all contiguous instances of one array from another.
  Not very efficient.
  If 'eq' is given, this will be used to compare items.
  """
  return replace_sublist(li1, li2, [], eq=eq)


def prefix_is(tokens, prefix):
  """ Do the upcoming tokens match the given prefix in content? """
  # Match the length of upcoming
  upcoming = tokens[:len(prefix)]
  # Detach tokens in both
  upcoming = map(detach_token, upcoming)
  prefix = map(detach_token, prefix)
  # Check if equal
  return list(upcoming) == list(prefix)


def split_pattern(pattern_toks, marker):
  """
  Take a pattern and a marker, which are both snippets of Python code.
  Tokenize both and return the pattern split around the marker.
  Detaches all returned tokens.

  For instance:
    split_pattern(tokenize_expr("list[IDX]"), "IDX")
  will return a tuple (prefix, suffix) where
    prefix is the tokens for "list["
    suffix is the tokens for "]"
  """
  pattern_toks = list(map(detach_token, pattern_toks))
  marker_tok = detach_token(tokenize_one(marker))
  marker_idx = pattern_toks.index(marker_tok)
  return pattern_toks[:marker_idx], pattern_toks[marker_idx+1:]
