import unplate
exec(unplate.magic(__file__))

template = '' #[
  # I'm in a template,
  # here, in {__file__},
  # all alone...
#]

print("My template:", template)
