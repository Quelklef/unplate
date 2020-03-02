import unplate.compile as unplate_compile
import unplate.tokenize_util as tku
import unplate.util

# export UnplateSyntaxError
UnplateSyntaxError = unplate_compile.UnplateSyntaxError

def template(*args, **kwargs):
  raise Exception("Something's gone wrong. You should never actually invoke unplate.template().")


"""

Top-level Unplate API.

>>> import unplate
>>> if unplate.true:
>>>   exec(unplate.compile(__file__), globals(), locals())
>>> else:
>>>   template = unplate.template(
>>>     # Here's my template
>>>   )

unplate.true always evaluates to True.

This enters the first block and means that the
second block (the else: block) is never run.
The call to unplate.compile reads the file source
code, compiles the unplate templates, and
returns native Python source. This is then
executed by the call to exec().
Additionally, the return value of unplate.compile
has all instances of "unplate.true" replaced
with False in order to prevent infinite recursion.

"""


true = True


def compile(file_loc):

  with open(file_loc, 'r') as f:
    code = f.read()

  return compile_code(code, file_loc=file_loc)


def compile_anon(code):
  return compile_code(code, file_loc='<anonymous>')


def compile_code(code, *, file_loc):

  tokens = tku.tokenize_string(code)
  compiled_tokens = unplate_compile.compile_top(tokens, file_loc=file_loc)

  # Remove the wrapper
  unplate_wrapper = tku.tokenize_expr('unplate.true')
  true_token = tku.tokenize_one('False')
  compiled_tokens = util.replace_sublist(compiled_tokens, unplate_wrapper, [true_token])

  compiled_code = tku.untokenize(compiled_tokens)
  return compiled_code

