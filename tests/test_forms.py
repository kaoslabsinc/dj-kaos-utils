from django.forms import modelform_factory

from dj_kaos_utils.forms import unrequire_form
from simple.models import Product


def test_unrequire_form():
    form_cls = modelform_factory(Product, exclude=())
    form = form_cls(dict(price=10, code_id='code'))
    assert not form.is_valid()

    form_cls_unq = unrequire_form(Product, ('name',))
    form = form_cls_unq(dict(price=10, code_id='code'))
    assert form.is_valid()

    form_cls_unq_form = unrequire_form(form_cls, ('name',))
    form = form_cls_unq_form(dict(price=10, code_id='code'))
    assert form.is_valid()
