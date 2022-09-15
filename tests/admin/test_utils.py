from django.utils.safestring import mark_safe

from dj_kaos_utils.admin.utils import pp_json, _render_attrs, render_element, render_img


def test_pp_json():
    obj = {'key': 'value'}
    hl_json = pp_json(obj)
    assert "key" in hl_json
    assert "value" in hl_json


def test_render_attrs():
    attrs = {'key': 'value'}
    html_attrs = _render_attrs(attrs)
    assert 'key="value"' in html_attrs


def test_render_element():
    el = render_element('img', attrs={'src': "image.png"})
    assert el == '<img src="image.png">'


def test_render_element_children():
    el = render_element('div', mark_safe('<h1>Hey!</h1>'), {'class': "alert alert-success"})
    assert el == '<div class="alert alert-success"><h1>Hey!</h1></div>'


def test_render_img():
    el = render_img("image.png")
    assert el == '<img src="image.png" alt="">'
