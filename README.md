# unplate
A minimal Python templating engine for people who don't like templating engines.

## Philosophy
(The short verison)

Most templating enginges try to do too much. Due to this, trying to do anything moderately fancy blows them up. This is due to an over-focus on separation of data and presentation. Unplate aims to avoid this issue by integrating into the host language as much as possible, so Unplate gets all the power of the host language for free. Separation of data and presentation is still possible, and encouraged.

## Example

There are more examples in `example.py`, but here's just one:

```python3
import unplate
exec(unplate.magic(__file__))  # Where the magic happens

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
import unplate
def make_namecard(name):
  greeting = unplate.compile("""/----------------------\\
|  Hello, my name is:  |
|  { name.ljust(18) }  |
\\----------------------/""", locals())
  return greeting
```

Except the Unplate code is far prettier.

## Notes of Interest:

1. The code-rewriting part of Unplate is pretty naive. This is on purpose. Code-rewriting is difficult and fragile, so Unplate keeps it to a minimum.

2. The call to `unplate.magic` must be **exactly** the code `exec(unplate.magic(__file__))`. That is, the tokens must be equivalent.

### Why not just use f-strings?
As of now, these are the reasons:
- Unplate allows you to control your indentation via where you place your comments.
- Unplate allows for customizable syntax (see `examples.py`).
- I personally had a bad experience trying to do this with f-strings, which is why I'm making this.

Unplate has more features to come, so this list will only grow!
