import sys
sys.path.append('..')

import unplate

# Where the Unplate magic happens
exec(unplate.transform_file(__file__))


my_country = "Australia"
poem = unplate.template(
  #$ I'm in a template,
  #$ here, in {my_country},
  #$ all alone...
)

print(f"= A short poem =\n{poem}")


# unplate handles backslahses nicely, no escapes needed
backslashes = unplate.template(
  #$ Here's a backslash for you: \
  #$ \ this line begins with a backslash
  #$ this line ends with a backslash \
  #$ this line has \ a backslash in the middle!
)
print(f'\n= Backslashes =\n{backslashes}')


# escape the interpolation characters with \:
escapes = unplate.template(
  #$ This: {2+2} will be interpolated
  #$ This: \{2+2\} will not
)
print(f'\n= Escapes =\n{escapes}')
