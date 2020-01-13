import sys
sys.path.append('..')
import unplate
exec(unplate.transform_file(__file__))


# Unplate allows you to customize the template
# syntax.
# You can change the escape character as
# well as the interpolation characters
unplate.options.interpolation_left = '<'
unplate.options.interpolation_right = '>'
unplate.options.escape_char = '~'
template = unplate.template(
  # This: <1/2> will be interpolated
  # This: {1/2} no longer will be
  # This: ~<1/2~> will be escaped
)
print(template)


