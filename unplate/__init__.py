import unplate.compile as unplate_compile
import unplate.tokenize_util as tku
import unplate.util
import unplate.options

# export UnplateSyntaxError
UnplateSyntaxError = unplate_compile.UnplateSyntaxError

def template(*args, **kwargs):
  raise Exception("Something's gone wrong. You should never actually invoke unplate.template().")


true = True


def compile(file_loc, options=options.defaults):

  with open(file_loc, 'r') as f:
    code = f.read()

  return compile_code(code, options, file_loc=file_loc)


def compile_anon(code, options=options.defaults):
  return compile_code(code, options, file_loc='<anonymous>')


def compile_code(code, options=options.defaults, *, file_loc):

  tokens = tku.tokenize_string(code)
  compiled_tokens = unplate_compile.compile_top(tokens, options, file_loc=file_loc)

  # Remove the wrapper
  unplate_wrapper = tku.tokenize_expr('unplate.true')
  true_token = tku.tokenize_one('False')
  compiled_tokens = util.replace_sublist(compiled_tokens, unplate_wrapper, [true_token])

  compiled_code = tku.untokenize(compiled_tokens)
  return compiled_code

