import json

from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer  # NoQA: Pycharm trips over this import


def pp_json(obj):
    """
    Return a syntax highlighted python dictionary/json in html

    :param obj: The dictionary/json to be pretty printed
    :return: syntax highlighted python dictionary/json in html
    """
    response = json.dumps(obj, sort_keys=True, indent=2)
    formatter = HtmlFormatter(style='colorful')
    response = highlight(response, JsonLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    return mark_safe(style + response)


def _render_attrs(attrs):
    """
    Given dictionary `attrs`, render html attributes with the same keys and values

    :param attrs: dictionary of attributes
    :return: String of key value pairs in html attributes format
    """
    return format_html_join(
        ' ', '{}="{}"', ((k, v) for k, v in attrs.items())
    )


def render_element(tag, children=None, attrs=None):
    """
    Render safe html element

    :param tag: the html tag to render, i.e. p or h1
    :param children: the children of the html element, will be escaped unless marked safe
    :param attrs: dictionary of attributes to render on the element
    :return: safe html element with tag, attributes and children
    """
    attrs = attrs or {}
    if children is None:
        return format_html(
            """<{} {}>""",
            tag, _render_attrs(attrs)
        )
    else:
        return format_html(
            """<{tag} {attrs}>{children}</{tag}>""",
            tag=tag, attrs=_render_attrs(attrs), children=children
        )
