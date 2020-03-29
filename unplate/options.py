import unplate.tokenize_util as tku
import unplate.util

class Options:
  """

  Customizable Unplate parameters.
  Contains the following atributes:

    template_literal_open
      default: the tokens for 'unplate.template('
      The tokens that signifiy the opening of a template literal

    template_literal_close
      default: the tokens for ')'
      The tokens that signify the closing of a template literal

    template_builder_open_left
      default: the tokens for '[unplate.begin('
      The tokens that signify the opening of a template builder, before the variable name

    template_builder_open_right
      default: the tokens for ')'
      The tokens that signify the opening of a template builder, after the variable name

    template_builder_close
      default: the tokens for '[unplate.end]'
      The tokens that signify the closing of a template builder


  """

  def __init__(self):

    template_literal_pattern = tku.tokenize_expr('unplate.template(\nBODY)')
    self.template_literal_open, self.template_literal_close = tku.split_pattern(template_literal_pattern, 'BODY')

    template_builder_open_pattern = tku.tokenize_expr("[unplate.begin(NAME)]")
    self.template_builder_open_left, self.template_builder_open_right = tku.split_pattern(template_builder_open_pattern, 'NAME')
    self.template_builder_close = tku.tokenize_expr('[unplate.end]')

defaults = Options()
