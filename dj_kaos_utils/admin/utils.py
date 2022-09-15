import json

from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer  # NoQA: Pycharm trips over this import


def pp_json(d):
    """
    Return a syntax highlighted python dictionary/json in html
    :param d: The dictionary to be pretty printed
    :return: syntax highlighted python dictionary/json in html
    """
    response = json.dumps(d, sort_keys=True, indent=2)
    formatter = HtmlFormatter(style='colorful')
    response = highlight(response, JsonLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    return mark_safe(style + response)
