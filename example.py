import unplate

# Don't ask questions, but you must wrap all your code
# in the following if statement:
if unplate.true:
  # The magic happens here
  exec(unplate.compile(__file__), globals(), locals())
else:

  # Template literals are denoted with unplate.template()
  template_0 = unplate.template(
    # I'm a template literal
    # line two
  )
  assert template_0 == "I'm a template literal\nline two\n", repr(template_0)

  # Interpolation of Python expressions is supported
  value = list(reversed('interpolation'))
  template_1 = unplate.template(
    # Unplate supports {{ ''.join(reversed(value)) }}
  )
  assert template_1 == 'Unplate supports interpolation\n', repr(template_1)

  # Templates may be threaded into control flow using
  # template builders:

  [unplate.begin(template_2)]
  # One line
  # Two line
  # >>> for color in ['red', 'blue']:
    # >>> capitalized = color.capitalize()
    # {{ capitalized }} line
  # <<<
  [unplate.end]

  assert template_2 == "One line\nTwo line\nRed line\nBlue line\n", repr(template_2)

  # the [braces] around 'unplate.begin()' and 'unplate.end()' do
  # not denote lists or anything like that. They are simply
  # there to add visual saliency to the unplate statements
  # to clearly mark them as special as compared to other statements.

  print("Tests passing!")
