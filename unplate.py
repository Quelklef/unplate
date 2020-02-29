import compile as unplate_compile
import tokenize_util as tku
import util


def template(*args, **kwargs):
  raise Exception("Something's gone wrong. You should never actually invoke unplate.template().")


"""

Top-level Unplate API.

>>> import unplate
>>> if unplate.true:
>>>   exec(unplate.compile(__file__))
>>> else:
>>>   template = unplate.template(
>>>     # Here's my template
>>>   )

First, the main exec() call is run, executing
the compiled code with processed templates.

Then, the program continues. The `if unplate.wrapper:`
block is encountered. However, `unplate.wrapper` is
always False, so this code never runs.

In this manner, we avoid the problem of running
code twice: once during the main exec() call,
and then once after that exec() call finishes.

This means that any code not within the `if` block
will be executed twice!

"""


true = True

def compile(file_loc):

  tokens = tku.tokenize_file(file_loc)

  compiled_tokens = unplate_compile.compile_top(tokens, file_loc=file_loc)

  # Remove the wrapper
  unplate_wrapper = tku.tokenize_expr('unplate.true')
  assert util.has_sublist(compiled_tokens, unplate_wrapper)
  true_token = tku.tokenize_one('False')
  compiled_tokens = util.replace_sublist(compiled_tokens, unplate_wrapper, [true_token])

  compiled_code = tku.untokenize(compiled_tokens)
  return compiled_code

