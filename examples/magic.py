import sys
sys.path.append('..')
import unplate


# Though it's recommende to use
#   exec(unplate.transform_file(__file__))
# Unplate /does/ offer a sleeker top-level
# API. It is, however, implementation-specific
# and may not work in environments that don't
# use cPython.

# The sleeker syntax is like this:
unplate.magic()
# This line is essentially the same as
#   exec(unplate.transform_file(__file__))
# on cPython.


# Templates still work:
template = unplate.template(
  #$ A working template!
)

print(template)
