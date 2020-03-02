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
    # {x}
  # <<< I should not be here
  [unplate.end]
  """

  with pytest.raises(unplate.UnplateSyntaxError):
    unplate.compile_anon(code)
