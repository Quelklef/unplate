from transform import transform_code
import util

"""

Main Unplate module; top-level API

"""

# import and export options
from options import options


def magic():
  """ Magic alternative to exec(unplate.transform_file(__file__)) """
  caller_frameinfo = inspect.stack()[1]
  caller_frame     = caller_frameinfo.frame
  frame_members    = dict(inspect.getmembers(caller_frame))
  caller_lineno    = caller_frameinfo.lineno
  caller_filename  = caller_frameinfo.filename
  caller_locals    = frame_members['f_locals']
  caller_globals   = frame_members['f_globals']

  with open(caller_filename) as f:
    code = f.read()

  # Remove the calling code
  # TODO: instead of doing this, perhaps we should have all calls
  #       to top-level entrypoints beyond the first be noops?
  caller_line_idx = caller_lineno - 1
  code = util.remove_line(code, caller_line_idx)

  transformed = transform_code(code)
  exec(transformed, caller_globals, caller_locals)

  # TODO: quit() exits the program, not just the module
  quit()


def transform_file(file_loc):
  """
  Main entry point of unplate.

  Transforms some Python source code with interpolated Unplate expression
  into native Python source code.

  Call EXACTLY like this:
    exec(unplate.transform_file(__file__))
  """

  with open(file_loc) as f:
    code = f.read()

  # Remove the calling code
  unplate_call = 'exec(unplate.transform_file(__file__))'
  assert unplate_call in code
  code = code.replace(unplate_call, '')

  # Don't run the original code after the caller's exec() call
  # TODO: What if this gets commented out, e.g. by a multiline string?
  code += "\n\nquit()"

  return transform_code(code)


def compile(template, context):
  """ Compile a template with the given context. """

  # For now, just use a naive algorithm

  # Chunks of string to be .join()'d in the end
  result_chunks = []

  # One after the index of the final char in the previous chunk
  l = 0

  # Are we in an interpolated expression?
  in_expression = False

  template_len = len(template)

  char_idx = -1
  while True:
    char_idx += 1
    if char_idx == template_len: break

    char = template[char_idx]
    next_char = template[char_idx + 1] if char_idx < template_len - 1 else None

    # =

    if char == options.escape_char:
      if next_char == options.interpolation_left:
        # Escaped open interpolation
        result_chunks.append(template[l:char_idx] + options.interpolation_left)
        char_idx += 1
        l = char_idx + 1

      if next_char == options.interpolation_right:
        # Escaped close interpolation
        result_chunks.append(template[l:char_idx] + options.interpolation_right)
        char_idx += 1
        l = char_idx + 1

    elif char == options.interpolation_left:
      # Unesacped open interpolation
      in_expression = True
      result_chunks.append(template[l:char_idx])
      l = char_idx + 1

    elif char == options.interpolation_right:
      # Unescaped close interpolation
      if not in_expression:
        poisiton = util.char_to_rowcol(template, char_idx)
        raise ParsingError(position, position, f"Interpolation closing marker '{options.close_interpolation}' illegal here since we were not in an interpolated expression.")

      # Switch states
      in_expression = False

      # Get the captured expression
      expression = template[l:char_idx]
      l = char_idx + 1

      # Evaluate it and append it
      value = eval(expression, context)
      result_chunks.append(value)

    elif next_char == None:
      # At the end of the string
      final_chunk = template[l:]
      result_chunks.append(final_chunk)

    else:
      pass


  # Calculate the final string from the chunks
  result = ''.join(map(str, result_chunks))
  return result


def template(*args, **kwargs):
  raise Exception("Something's gone wrong. You should never actually invoke unplate.template().")
