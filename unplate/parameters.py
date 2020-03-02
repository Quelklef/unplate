import unplate.tokenize_util as tku
import unplate.util

template_literal_pattern = tku.tokenize_expr('unplate.template(\nBODY)')
template_literal_open, template_literal_close = tku.split_pattern(template_literal_pattern, 'BODY')

template_builder_open_pattern = tku.tokenize_expr("[unplate.begin(NAME)]")
template_builder_open_left, template_builder_open_right = tku.split_pattern(template_builder_open_pattern, 'NAME')
template_builder_close = tku.tokenize_expr('[unplate.end]')
