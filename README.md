# unplate
A minimal Python templating engine for people who don't like templating engines.

## Philosophy
Most templating engines are all about separation. Separate the engine from the language. Separate the content from the display. These are noble goals, but they have a major flaw: they require templating engines to have their own, entirely new language. This means that **most templating engines are not very robust and blow up as soon as you try to do anything difficult** because they haven't had nearly as long time to mature as the host language. Even widely-used templating engines like Jinja2 have this issue. For instance, Jinja2 does not support multiple inheritance (a template inheriting a template inheriting a template).

Unplate aims to avoid this by going the complete opposite direction: it aims to be as integrated into the host language as possible. This means that **unplate automatically gets to use all features of the host programming language**. This breaks separation of the templating engine from the host language, which unplate is willing to accept. It does *not* break separation of content from display; unplate still encourages this, thought it does not enforce it.

## Usage
TODO, once I figure out the best way to do this.
