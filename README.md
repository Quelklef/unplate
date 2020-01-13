# unplate
A minimal Python templating engine for people who don't like templating engines.

## Philosophy
Most templating engines are all about separation. Separate the engine from the language. Separate the content from the display. These are noble goals, but they have a major flaw: they require templating engines to have their own, entirely new language. This means that **most templating engines are not very robust and blow up as soon as you try to do anything difficult** because they haven't had nearly as long time to mature as the host language. Even widely-used templating engines like Jinja2 have this issue. For instance, Jinja2 does not support multiple inheritance (a template inheriting a template inheriting a template).

Unplate aims to avoid this by going the complete opposite direction: it aims to be as integrated into the host language as possible. This means that **Unplate automatically gets to use all features of the host programming language**. This breaks separation of the templating engine from the host language, which unplate is willing to accept. It does *not* break separation of content from display; unplate still encourages this, thought it does not enforce it.

## Usage
Unplate templates are written directly into Python code within comments, so that syntax highlighting need not be changed. The Unplate script then compiles the comments back into working Python code, which should then be `exec()`'d.

Example:

(see `examples.py` for more examples)

```python3
import unplate
exec(unplate.magic(__file__))  # Where the magic happens

def make_namecard(name):
  """ Simple template example. Return an ASCII-art namecard. """
  greeting = unplate.template(
    # /----------------------------\
    # |                            |
    # |     Hello, my name is:     |
    # |     { name.ljust(18) }     |
    # |                            |
    # \----------------------------/
  )
  return greeting
```

The above code is functionally equivalent to the following:

```python3
import unplate
def make_namecard(name):
  greeting = unplate.compile("""/----------------------------\\
|                            |
|     Hello, my name is:     |
|     { name.ljust(18) }     |
|                            |
\\----------------------------/""", locals())
  return greeting
```

Which will behave as you probably expect it to.

As you can see, Unplate pretty naively compiles back into Python code. This is on purpose. The metaprogramming/macro aspect of Unplate is designed to be as minimal as possible because it's the place where the most can go wrong. Instead, most of the processing is done in `unplate.compile`.

Note that **the call to `unplate.magic` must be exactly the code `exec(unplate.magic(__file__))`** (in particular, the tokens must be equivalent).

### Why not just use f-strings?
Great question. As of right now, Unplate offers no functional benefit over f-string. However, it gets over a few Python lexical limitations:

- Unplate allows for a leading newline in the code that doens't appear in the template (`#$>`)
- Unplate allows for the template to be indented in the code.
- Overall, I had a bad experience trying to do this with f-strings--hence the project.

Additionally, there are planned features for Unplate that will go beyond f-strings, such as automatic input sanitization, e.g. for HTML templates.
