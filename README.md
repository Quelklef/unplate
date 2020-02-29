# unplate
A minimal Python templating engine for people who don't like templating engines.

## Philosophy
(The short verison)

Most templating enginges try to do too much. Due to this, trying to do anything moderately fancy blows them up. This issue comes from an over-focus on separation of data and presentation. Unplate aims to avoid this issue by integrating into the host language as much as possible, so Unplate gets all the power of the host language for free. Separation of data and presentation _is_ still possible and encouraged.

## Example

Also see `example.py`

```python3
import unplate

# These first few lines are magic that's required for Unplate to work
if unplate.true:
  exec(unplate.compile(__file__), globals(), locals())
else:

  def make_namecard(name):
    """ Simple template example. Return an ASCII-art namecard. """
    greeting = unplate.template(
      # /----------------------\
      # |  Hello, my name is:  |
      # |  { name.ljust(18) }  |
      # \----------------------/
    )
    return greeting
```

The above code is functionally equivalent to the following:

```python3
def make_namecard(name):
  greeting = (
f"""/----------------------\\
|  Hello, my name is:  |
|  { name.ljust(18) }  |
\\----------------------/
""")
  return greeting
```

Except the Unplate code is far prettier.

## Second example

Unplate supports template building

```python3
import unplate
if unplate.true:
  exec(unplate.compile(__file__), globals(), locals())
else:

  [unplate.begin(my_template)]
  # One line
  # Two line
  # >>> for color in ['red', 'blue']:
    # >>> capitalized = color.capitalize()
    # {capitalized} line
  # <<<
  [unplate.end]
```

gives the following result in `my_template`:

```
One line
Two line
Red line
Blue line

```

(Note the trailing newline)
