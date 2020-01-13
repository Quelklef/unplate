import unplate
exec(unplate.magic(__file__))

poem = unplate.template(
  # I'm in a template,
  # here, in {__file__},
  # all alone...
)

print(f"= A short poem =\n{poem}")


# unplate handles backslahses nicely, no escapes needed
backslashes = unplate.template(
  # Here's a backslash for you: \
  # \ this line begins with a backslash
  # this line ends with a backslash \
  # this line has \ a backslash in the middle!
)
print(f'\n= Backslashes =\n{backslashes}')


# escape the interpolation characters with \:
escapes = unplate.template(
  # This: {2+2} will be interpolated
  # This: \{2+2\} will not
)
print(f'\n= Escapes =\n{escapes}')


# you can also change the escape character as
# well as the interpolation characters
unplate.options.interpolation_left = '<'
unplate.options.interpolation_right = '>'
unplate.options.escape_char = '~'
options = unplate.template(
  # This: <1/2> will be interpolated
  # This: {1/2} no longer will be
  # This: ~<1/2~> will be escaped
)
print(f'\n= Options =\n{options}')
