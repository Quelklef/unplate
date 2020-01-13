from tokenize_util import detach_token, tokenize_one, tokenize_fragment
import util

class Options:
  """

  An object containing Unplate options. Contains the following attributes:

  prefix
    default: '$ '
    The string after the comment hash ('#') that marks the coment as part of
    an Unplate template. This may be set to '', but it is not recommended,
    as using a prefix makes the code more explicit about what is and isn't
    a template.

  allow_template_comment_outside_template
    default: False
    If False, throw an error if there is a comment that both starts with
    the Unplate prefix but is not part of an Unplate template.
    It is recommended to make this False unless the template comment
    prefix is either '' or ' '.

  interpolation_left
    default: '{'
    The character marking the start of an interpolated expression in a template.

  interpolation_right
    default: '}'
    The character marking the end of an interpolated expresssion in a template

  escape_char
    default: '\\'
    The character used to escape the left and right interpolation characters

  pattern
    default: 'unplate.template(\nTEMPLATE\n)'
    A string denoting the syntax for an Unplate template. The string MUST contain
    a 'TEMPLATE' identifier, which represents where the template is expected.

  pattern_tokens (read only)
    default: the tokens for 'unplate.template(\nTEMPLATE\n)'
    The tokens of the curent pattern.

  open_token (read only)
    default: the tokens for 'unplate.template('
    The tokens to the left of the 'TEMPLATE' token in template_pattern.

  close_tokens (read only)
    default: the tokens for ')'
    The tokens to the right of the 'TEMPLATE' token in template_pattern.

  """

  def __init__(self):
    self.allow_template_comment_outside_template = False
    self.pattern = 'unplate.template(\nTEMPLATE\n)'
    self.prefix = '$ '
    self.interpolation_left = '{'
    self.interpolation_right = '}'
    self.escape_char = '\\'

  @property
  def pattern(self):
    return self._pattern

  @pattern.setter
  def pattern(self, pattern):
    self._pattern = pattern
    self.pattern_tokens = tokenize_fragment(self._pattern)

    body_marker = tokenize_one('TEMPLATE')
    def eqs_body_marker(token):
      return detach_token(body_marker) == detach_token(token)
    marker_idx = util.find(self.pattern_tokens, eqs_body_marker)

    self.open_tokens = self.pattern_tokens[:marker_idx]
    self.close_tokens = self.pattern_tokens[marker_idx+1:]




# Make global options
options = Options()
