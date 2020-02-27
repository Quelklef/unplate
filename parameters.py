import tokenize_util as tku
import util

template_literal_pattern = tku.tokenize_expr('unplate.template(\nBODY)')
template_literal_open, template_literal_close = tku.split_pattern(template_literal_pattern, 'BODY')
"""
Tokens marking the open and close of a template literal.
For instance,

  t = unplate.template(
    #" my template
  )
  assert t == "my template"
"""

template_builder_open_pattern = tku.tokenize_expr("[unplate.begin(NAME)]")
template_builder_open_left, template_builder_open_right = tku.split_pattern(template_builder_open_pattern, 'NAME')
template_builder_close = tku.tokenize_expr('[unplate.end]')
"""
Tokens marking the open and close of a template builder.
For instance,

  [unplate.begin(my_template)]
  for i in range(10):
    #$ line #{i}
  [unplate.end]
  print(my_template)
"""

interpolation_prefix = '$ '
"""
The string that marks a comment as an interpolating Unplate
template. For instance,

  x = 5
  t = unplate.template(
    #$ x is {x}
  )
  assert t == "x is 5"
"""

interpolation_open = '{'
"""
Marks the beginning of an interpolated expression within a template
"""

interpolation_close = '}'
"""
Marks the end of an interpolated expression within a template
"""

interpolation_escape = '\\'
"""
Used to escape an interpolation open or close
"""

verbatim_prefix = '" '
"""
Marks a comment as a verbatim unplate template. For instance,

  t = unplate.template(
    #" the following will not be interpolated: {x}
  )
  assert "{x}" in t
"""
