from __future__ import annotations

from django.db import models
from django.db.models.query_utils import RegisterLookupMixin


class TwoPlacesDecimalField(models.DecimalField):
    """A DecimalField with 2 decimal places"""
    description = "A DecimalField with 2 decimal places"

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = kwargs.get('max_digits', 12)
        kwargs['decimal_places'] = 2
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_digits']
        del kwargs['decimal_places']
        return name, path, args, kwargs


class MoneyField(TwoPlacesDecimalField):
    """Model field representing an amount of money"""
    description = "An amount of money"


class CaseInsensitiveFieldMixin(RegisterLookupMixin):
    """
    Field mixin that uses case-insensitive lookup alternatives if they exist.

    Example:
        >>> class LowerCaseLookupCharField(CaseInsensitiveFieldMixin, models.CharField):
        >>>     pass
    """
    LOOKUP_CONVERSIONS = {
        'exact': 'iexact',
        'contains': 'icontains',
        'startswith': 'istartswith',
        'endswith': 'iendswith',
        'regex': 'iregex',
    }

    def get_lookup(self, lookup_name):
        converted = self.LOOKUP_CONVERSIONS.get(lookup_name, lookup_name)
        return super().get_lookup(converted)


class ToLowerCaseFieldMixin(models.Field):
    """
    Always save the field as lowercase
    """

    def to_python(self, value):
        return super(ToLowerCaseFieldMixin, self).to_python(value).lower()


class LowerCaseCharField(CaseInsensitiveFieldMixin, ToLowerCaseFieldMixin, models.CharField):
    """
    CharField that saves the values passed to it as lowercase.
    """


__all__ = [
    'TwoPlacesDecimalField',
    'MoneyField',
    'CaseInsensitiveFieldMixin',
    'ToLowerCaseFieldMixin',
    'LowerCaseCharField',
]
