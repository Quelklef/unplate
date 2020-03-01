# unplate
A minimal Python templating engine for people who don't like templating engines.

## What?

Think "templating engine", but instead of _interfacing with_ Python, Unplate is rather _embedded within_ Python.

### Example: Template Literal

The simplest type of template is a _template literal_. It is denoted with `unplate.template(my_template)`, where the template is written in comments. Interpolation is supported, f-string style.

```python
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

```python
def make_namecard(name):
  greeting = (
f"""/----------------------\\
|  Hello, my name is:  |
|  { name.ljust(18) }  |
\\----------------------/
""")
  return greeting
```

### Example: Template Builders

Templates may also contain logic, e.g. for-loops. These are supported by "template builders" which are opened with `[unplate.begin(template_name)]` and closed with `[unplate.end]`. Python statements can interpolated into template builders by beginning the line with `>>>`. Dedentation must be explicitly denoted, using `<<<`.

```python
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

```text
One line
Two line
Red line
Blue line

```

(Note the trailing newline)

## Why?

Essentially, because I got frustrated.

Across the board, my experiences with templating engines has been the same. They look fantastic at the beginning, but always turn out to have pretty severely limited functionality or questionable design decisions.

For instance:

1. [Liquid has no `not` operator](https://github.com/Shopify/liquid/issues/138). What the hell? So you can't say `{% if not post.is_hidden %}`. You can instead say `{% unless post.is_hidden %}`, but that only works if you're trying to negate the _entire_ condition---expressing something like `if post.is_published and not post.is_hidden` isn't possible without resorting to tricks like:
   -  [nesting `if` and `unless`](https://github.com/Shopify/liquid/issues/138#issuecomment-8529289)
   -  [writing it as `post.is_published and post.is_hidden != true`](https://github.com/Shopify/liquid/issues/138#issuecomment-429072341)
   -  [using four statements to negate a variable](https://github.com/Shopify/liquid/issues/138#issuecomment-428742512).
2. By default, Jinja2 templates fail silently on an undefined variable: ["If a variable or attribute does not exist [...] the default behavior is to evaluate to an empty string if printed or iterated over, and to fail for every other operation"](https://jinja.palletsprojects.com/en/2.11.x/templates/#variables). I actually understand this choice, but only for use in production (generally better to serve something incomplete than nothing at all). For development, though, it makes no sense. To their credit, [the behavior can be changed](https://stackoverflow.com/q/3983581/4608364).
3. [Jinja2 doesn't/didn't support a templating interhiting from a template inheriting from a template](https://stackoverflow.com/q/1976651/4608364). Again to their credit, this now [seems to be supported in 2.11](https://jinja.palletsprojects.com/en/2.11.x/templates/#nesting-extends).
4. [Recursion in Jinja2 is really awkward](https://jinja.palletsprojects.com/en/2.11.x/templates/#for) (scroll to "It is also possible to use loops recursively").
5. I once was building a blog rendered with Liquid and wanted to compare the dates of two posts. However, the date objects themselves could not be compared. I was able to do it by formatting both dates to `YYYY-MM-DD` and using lexicographical string comparison on those results. It worked, but it was ugly, and ridiculous that I had to go through such a hoop in order to tell if one date came after another or not.

So, in my experience, templating engines tend to have limited functionality and doing anything even kinda difficult requires weird tricks.

But usually the host language---the programming language rendering the template---already _has_ all this functionality. Mainstream languages generally have a `not` operator, yell at you upon referencing an undefined variable, support clean recursion, and can compare dates! So why, I figured, are we doing all this work to _re_-implement this functionality, poorly, in the templating language, when we already _have_ it [1]?

This is the idea of Unplate. Instead of separating ourselves from the host language, integrate into it. This way, we get all the functionality of that language for free. No need to reimplement anything.

[1]: The answer, I think, is actually simple: what we gain is agnosticism to the host language; Jinja2 and Liquid can both, in theory, be rendered via multiple different programming languages. This is the main disadvantage of using Unplate---it's Python-only---but one that I posit is not actually much of a problem in most situations.

### What about separation of data and display?

Surely the situation isn't this way for no reason. I think probably the reason that templating engines do this---separate themselves so much from the host language---is in the name of _separation of data and display_: you should process your data in one area, and display it in another. This is perfectly reasonable, and valid!

However, need it be so painful?

I say no! With Unplate, you still _can_ separate data and display: just keep your template logic to a minimum. Unplate does make it easier to break this rule, but it's still possible---and encouraged---to follow it.
