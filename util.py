def next_n(it, n):
  """ Repeat next() n times """
  for _ in range(n):
    next(it)


def remove_line(string, line_idx):
  lines = string.split('\n')
  lines.pop(line_idx)
  return '\n'.join(lines)


def find(it, pred):
  """ Return index of first item satisfying predicate """
  for i, x in enumerate(it):
    if pred(x):
      return i
  raise ValueError("No matching value found.")

