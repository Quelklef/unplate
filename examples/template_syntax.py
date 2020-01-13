import sys
sys.path.append('..')
import unplate
exec(unplate.transform_file(__file__))


# Unplate allows you to customize the template syntax.

# Change the interpolation syntax from {braces} to <angles>
unplate.options.interpolation_left = '<'
unplate.options.interpolation_right = '>'

# Change the escape char from \backslash to ~tilde
unplate.options.escape_char = '~'

template = unplate.template(
  #$ This: <1/2> will be interpolated
  #$ This: {1/2} no longer will be
  #$ This: ~<1/2~> will be escaped
)
print(template)


