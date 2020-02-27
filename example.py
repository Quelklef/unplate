import unplate

# Don't ask questions, but you must wrap all your code
# in the following if statement:
if unplate.true:
  # The magic happens here
  exec(unplate.compile(__file__), globals(), locals())
else:

  # Template literals are denoted with unplate.template()
  template_0 = unplate.template(
    #" I'm a template literal
    #" line two
  )
  assert template_0 == "I'm a template literal\nline two\n"

  # The " at the beginning of the comment notes that the
  # template is 'verbatim', i.e. all of its contents will
  # be interpreted literally.

  # Interpolation is supported by using '$' instead:
  value = 'interpolation'
  template_1 = unplate.template(
    #$ Unplate supports {value}
  )
  assert template_1 == 'Unplate supports interpolation\n'

  # The semantics of interpolated templates match
  # those of Python f-strings.
  # In fact, interpolated templates compile down into
  # f-strings.

  # Templates may be threaded into control flow using
  # template builders:

  [unplate.begin(template_2)]

  #" A line
  #" A second line

  for i in range(3):
    pass
    #$ line #{i + 1}

  if True:
    pass
    #" I will be added

  if False:
    pass
    #" I will not

  # Unfortunately, due to Python parsing oddities, the
  # template comment MUST come after the 'pass' statement

  [unplate.end]

  assert template_2 == "A line\nA second line\nline #1\nline #2\nline #3\nI will be added\n", repr(template_2)

  # the [braces] around 'unplate.begin()' and 'unplate.end()' do
  # not denote lists or anything like that. They are simply
  # there to add visual saliency to the unplate statements
  # to clearly mark them as special as compared to other statements.

  print("Tests passing!")
