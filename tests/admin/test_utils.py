from dj_kaos_utils.admin.utils import pp_json, render_attrs


def test_pp_json():
    obj = {'key': 'value'}
    hl_json = pp_json(obj)
    assert "key" in hl_json
    assert "value" in hl_json


def test_render_attrs():
    attrs = {'key': 'value'}
    html_attrs = render_attrs(attrs)
    assert 'key="value"' in html_attrs
