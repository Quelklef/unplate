import unplate
exec(unplate.magic(__file__))

poem = unplate.template(
  # I'm in a template,
  # here, in {__file__},
  # all alone...
)

print(f"A short poem:{poem}")


serious = unplate.template(
  # Australia is on fire.
  # Global climate change is out of control.
  # We may not make it.
)

print(f"\nAnd now for something more serious:\n{serious}")
