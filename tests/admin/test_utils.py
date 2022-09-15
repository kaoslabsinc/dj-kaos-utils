from dj_kaos_utils.admin.utils import pp_json


def test_pp_json():
    obj = {'key': 'value'}
    hl_json = pp_json(obj)
    assert "key" in hl_json
