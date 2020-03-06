import pytest
import unplate

def test__complain_on_missing_space_after_hash():

  code = """
  templ = unplate.template(
    # space
    #no space
    # space
  )
  """

  with pytest.raises(unplate.UnplateSyntaxError):
    unplate.compile_anon(code)


def test__complain_on_missing_space_after_prompt():

  code = """
  [unplate.begin(template)]
  # >>> 'space'
  # >>>'no space'
  # >>> 'space'
  [unplate.end]
  """

  with pytest.raises(unplate.UnplateSyntaxError):
    unplate.compile_anon(code)


def test__complain_on_non_isolated_dedent():

  code = """
  [unplate.begin(template)]
  # >>> for x in l:
    # >>> pass
  # <<< I should not be here
  [unplate.end]
  """

  with pytest.raises(unplate.UnplateSyntaxError):
    unplate.compile_anon(code)


def test__expr_interpolation():

  code = """#newline
s = "interpolated"
t = unplate.template(
  # {{ s }}
)
assert t == s + '\\n'
  """

  exec(unplate.compile_anon(code))


def test__stmt_interpolation():

  code = """#newline
[unplate.begin(template)]
# first line
# >>> for i in range(3):
  # >>> j = i + 1
  # {{ j }}
# <<<
# last line
[unplate.end]

expected = '''first line
1
2
3
last line
'''

assert template == expected, repr(template)
"""

  exec(unplate.compile_anon(code))


def test__string_templates():

  code = """#newline
[unplate.begin(template)] @ '''
first line
last line
''' [unplate.end]

assert template == 'first line\\nlast line\\n', repr(template)
"""

  exec(unplate.compile_anon(code))
