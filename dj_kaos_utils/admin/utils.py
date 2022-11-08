import json

from django.urls import reverse, NoReverseMatch
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


def render_img(src: str, alt="", attrs=None):
    """
    Render img tag with src, alt and attrs

    :param src: src of img
    :param alt: alt attribute
    :param attrs: dict of extra attributes
    :return: safe html of img tag
    """
    attrs = attrs or {}
    return render_element('img', attrs={'src': src, 'alt': alt} | attrs)


def render_anchor(href: str, children=None, new_tab=True, attrs=None):
    """
    Render anchor/link tag with href, children, etc.

    :param href: the href link of the anchor
    :param children: what to render inside the anchor tag
    :param new_tab: whether the link should open a new tab
    :param attrs: other attributes to put on the element
    :return: anchor tag
    """
    attrs = attrs or {}
    _attrs = {'href': href}
    if children is None:
        children = href
    if new_tab:
        _attrs['target'] = '_blank'
        _attrs['rel'] = 'noreferrer'
    return render_element('a', children, attrs=_attrs | attrs)


def get_admin_link(obj):
    opts = obj._meta
    try:
        return reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=(obj.id,))
    except NoReverseMatch:
        return None


def render_admin_link(obj, **kwargs):
    admin_link = get_admin_link(obj)
    if admin_link:
        return render_anchor(admin_link, str(obj), **kwargs)


__all__ = (
    'pp_json',
    'render_element',
    'render_img',
    'render_anchor',
    'get_admin_link',
    'render_admin_link',
)
