from __future__ import annotations

from typing import Sequence, Type

from django.db import models
from django.db.models.base import ModelBase
from django.forms import modelform_factory, BaseForm


class UnrequiredFieldsFormMixin(BaseForm):
    """
    Make fields denoted by `unrequired_fields` be not required on the form
    """
    unrequired_fields = ()

    def __init__(self, *args, **kwargs):
        super(UnrequiredFieldsFormMixin, self).__init__(*args, **kwargs)
        for field in self.unrequired_fields:
            if field in self.fields:
                self.fields[field].required = False


def unrequire_form(form_or_model_cls: Type[BaseForm] | Type[models.Model], unrequired_fields: Sequence[str]):
    """
    Make fields denoted by `unrequired_fields` be not required on the form or model form denoted by `form_or_model_cls`.

    :param form_or_model_cls: Form class or model class to create a model form out of
    :param unrequired_fields: Fields that should become not required
    :return: Form class with fields denoted by unrequired_fields not required.
    """
    _unreq_fields = unrequired_fields

    if isinstance(form_or_model_cls, ModelBase):
        model_cls = form_or_model_cls
        form_cls = modelform_factory(model_cls, fields='__all__')
    else:
        form_cls = form_or_model_cls

    if issubclass(form_cls, UnrequiredFieldsFormMixin):
        class UnrequiredModelForm(form_cls):
            unrequired_fields = (*form_cls.unrequired_fields, *_unreq_fields)
    else:
        class UnrequiredModelForm(UnrequiredFieldsFormMixin, form_cls):
            unrequired_fields = _unreq_fields

    UnrequiredModelForm.__name__ = "Unrequired" + form_cls.__name__

    return UnrequiredModelForm


__all__ = (
    'UnrequiredFieldsFormMixin',
    'unrequire_form',
)
