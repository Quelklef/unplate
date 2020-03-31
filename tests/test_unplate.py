import pytest
import unplate

import unplate.tokenize_util as tku

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


def test__string_templates_indented():

  code = """#newline

if True:
  [unplate.begin(template)] @ '''
  no indent
    one indent
  no indent
  ''' [unplate.end]

  assert template == 'no indent\\n  one indent\\nno indent\\n', repr(template)
"""

  exec(unplate.compile_anon(code))


def test__multiple_indent():

  code = """#newline

if True:
  if True:
    if True:

      [unplate.begin(template)] @ '''
      a
        b
      >>> x = 3
        {{ x }}
      c
      ''' [unplate.end]

      assert template == 'a\\n  b\\n  3\\nc\\n', repr(template)
"""

  exec(unplate.compile_anon(code))


def test__indented_blank_lines():

  code = '''#newline
if cond:
  [unplate.begin(template)] @ """

  """ [unplate.end]
'''

  unplate.compile_anon(code)


def test__unbalanced_indentation():

  code = """#newline
[unplate.begin(template)] @ '''

>>> oops_no_colon
  >>> stmt
<<<

''' [unplate.end]
"""

  with pytest.raises(unplate.UnplateSyntaxError):
    unplate.compile_anon(code)


def test__custom_interpolation():

  options = unplate.options.Options()
  options.interpolation_open = '<PYTHON>'
  options.interpolation_close = '</PYTHON>'

  code = """#newline
x = 3
template = unplate.template(
  # three is <PYTHON> x </PYTHON> is three
)
assert template == 'three is 3 is three\\n', template
"""

  exec(unplate.compile_anon(code, options))


def test__sigils():

  code = """#newline
[unplate.begin(template)] @ r'''
I have a sigil
''' [unplate.end]

assert template == 'I have a sigil\\n', template
"""

  exec(unplate.compile_anon(code))


def test__bug_0001():

  code = '''
if cond:
  [unplate.begin(template)] @ """
  >>> if cond:
        >>> if cond:
          {{ expr }}
        <<<
        {{ expr }}
  <<<
  """ [unplate.end]
'''

  tku.tokenize_string(unplate.compile_anon(code))


def test_builder_misspelling():

  code = '''
[unplate.template(my_template)] @ """
I'm not correct.
Template builders begin with `unplate.begin`,
not `unplate.template`.
""" [unplate.end]
'''

  with pytest.raises(AttributeError):
    exec(unplate.compile_anon(code))
