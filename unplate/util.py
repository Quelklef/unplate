def has_sublist(superlist, sublist):
  """
  Does a list contain another list within it?
  Not very efficient.
  If 'eq' is given, this will be used to compare items.
  """
  return any(
    superlist[i : i + len(sublist)] == sublist
    for i in range(len(superlist) - len(sublist) + 1)
  )


def replace_sublist(li, target, replacement):
  """
  Replace a sublist with another sublist.
  Not very effcient.
  If 'eq' is given, this will be used to compare items.
  """
  result = []
  i = 0
  while i < len(li):
    if li[i : i + len(target)] == target:
      i += len(target)
      result.extend(replacement)
    else:
      result.append(li[i])
      i += 1
  return result


def prefix_is(list, prefix):
  return list[:len(prefix)] == prefix


def starts_with(string, substring, *, start: int):
  """
  Functionally equivalent to
    string[start:].startswith(substring)
  but faster
  """
  return string[start : start + len(substring)] == substring
