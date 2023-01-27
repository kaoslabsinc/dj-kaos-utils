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

    Example:
        >>> class MyModelAdmin(admin.ModelAdmin):
        >>>     ...
        >>>     @admin.display
        >>>     def json_display(self, obj):
        >>>         return pp_json(obj.json)
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

    Example:
        >>> class MyModelAdmin(admin.ModelAdmin):
        >>>     ...
        >>>     @admin.display
        >>>     def alert_display(self, obj):
        >>>         return render_element('div', "Alert", {'class': 'alert'})
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

    Example:
        >>> class MyModelAdmin(admin.ModelAdmin):
        >>>     ...
        >>>     @admin.display
        >>>     def image_display(self, obj):
        >>>         return render_img('image.jpg', "Image", {'class': 'thumbnail'})
    """
    attrs = attrs or {}
    return render_element('img', attrs={'src': src, 'alt': alt} | attrs)


def render_anchor(href: str, children=None, attrs=None, new_tab=True, new_tab_icon=True):
    """
    Render anchor/link tag with href, children, etc.

    :param href: the href link of the anchor
    :param children: what to render inside the anchor tag
    :param attrs: other attributes to put on the element
    :param new_tab: whether the link should open a new tab
    :param new_tab_icon: whether to render a mini icon at the end of the link denoting it will open in a new tab.
        Only goes into effect if new_tab is True.
    :return: anchor tag

    Example:
        >>> class MyModelAdmin(admin.ModelAdmin):
        >>>     ...
        >>>     @admin.display
        >>>     def url_display(self, obj):
        >>>         return render_anchor('https://www.example.com', "Link")
    """
    attrs = attrs or {}
    _attrs = {'href': href}
    if children is None:
        children = href
    if new_tab:
        _attrs['target'] = '_blank'
        _attrs['rel'] = 'noreferrer'
        if new_tab_icon:
            children = render_element('span', children, {'style': "margin-right: 0.5rem"})
            children += render_element('sup', '⇱', {'style': "transform: scaleX(-1); display: inline-block;"})
    return render_element('a', children, attrs=_attrs | attrs)


def get_admin_link(obj):
    """
    Return the admin change page link for the given object, or None if the link cannot be generated.

    :param obj: the object for which to get the admin change page link
    :type obj: django model instance
    :return: the admin change page link if it exists or None otherwise
    :rtype: str or None
    :raises: `NoReverseMatch` if the admin change URL does not exist for the given object

    Example:
        >>> class MyModel(models.Model):
        >>>     def get_absolute_url(self):
        >>>         return get_admin_link(self)
    """
    opts = obj._meta
    try:
        return reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=(obj.id,))
    except NoReverseMatch:
        return None


def render_admin_link(obj, **kwargs):
    """
    Return marked-as-safe html containing an anchor tag linking to the admin change page of the object. If the object
    doesn't have an admin change page, return the string representation of the object

    :param obj: the model instance to grab the link for
    :param kwargs: extra kwargs to pass to `render_anchor`
    :return: marked-as-safe html of the anchor tag

    Example:
        >>> class MyModelAdmin(admin.ModelAdmin):
        >>>     def parent_display(self, obj):
        >>>         return render_admin_link(obj.parent)
    """
    admin_link = get_admin_link(obj)
    if admin_link:
        return render_anchor(admin_link, str(obj), **kwargs)
    else:
        return str(obj)


__all__ = (
    'pp_json',
    'render_element',
    'render_img',
    'render_anchor',
    'get_admin_link',
    'render_admin_link',
)
