from typing import Type

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .utils import get_lookup_values


class RelatedModelSerializer(serializers.ModelSerializer):
    lookup_field = None
    can_get = True
    can_create = False
    can_update = False

    def __init__(self, *args, **kwargs):
        self.lookup_field = kwargs.pop('lookup_field', self.lookup_field) or getattr(self.Meta, 'lookup_field', None)
        self.can_get = kwargs.pop('can_get', self.can_get)
        self.can_create = kwargs.pop('can_create', self.can_create)
        self.can_update = kwargs.pop('can_update', self.can_update)
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_object(model, lookup_field, lookup_value):
        try:
            return model.objects.get(**{lookup_field: lookup_value})
        except model.DoesNotExist:
            raise ValidationError({
                lookup_field: f"{model._meta.object_name} matching query {lookup_field}={lookup_value} does not exist."
            })

    def to_internal_value(self, data):
        lookup_field = self.lookup_field
        assert lookup_field is not None, "You should specify lookup_field"

        lookup_value = data.pop(lookup_field, None)
        model = self.Meta.model

        if lookup_value is not None and not data:
            # e.g. { uuid: "123-1234-..." }
            if self.can_get:
                return self._get_object(model, lookup_field, lookup_value)
            else:
                raise ValidationError("This api is not configured to get existing objects")
        elif lookup_value is not None and data:
            # e.g. { uuid: "123-1234-...", name : "Name" }
            if self.can_update:
                instance = self._get_object(model, lookup_field, lookup_value)
                return self.update(instance, data)
            else:
                raise ValidationError("This api is not configured to update existing objects")
        elif lookup_value is None and data:
            # e.g. { name : "Name" }
            if self.can_create:
                return self.create(data)
            else:
                raise ValidationError("This api is not configured to create new objects")
        else:
            raise ValidationError("data is empty")


def make_nested_writable(serializer_cls: Type[serializers.ModelSerializer],
                         lookup_field=None,
                         can_get=True,
                         can_create=False,
                         can_update=False):
    class WritableNestedXXX(RelatedModelSerializer, serializer_cls):
        pass

    WritableNestedXXX.lookup_field = lookup_field
    WritableNestedXXX.can_get = can_get
    WritableNestedXXX.can_create = can_create
    WritableNestedXXX.can_update = can_update
    WritableNestedXXX.__name__ = WritableNestedXXX.__name__.replace('XXX', serializer_cls.__name__)

    return WritableNestedXXX


class HasRelatedFieldsModelSerializer(serializers.ModelSerializer):
    default_related_lookup_field = 'uuid'

    def __init__(self, *args, **kwargs):
        self.related_fields = self._get_related_fields()
        super().__init__(*args, **kwargs)

    def _get_related_fields(self):
        related_fields = {}
        for item in self.Meta.related_fields:
            if isinstance(item, tuple):
                field, lookup = item
            else:
                field, lookup = item, self.default_related_lookup_field
            related_fields[field] = lookup
        return related_fields

    def create(self, validated_data):
        rel_data_dict = {}
        for field in self.related_fields:
            rel_data_dict[field] = validated_data.pop(field)

        instance = super().create(validated_data)

        for field, data_list in rel_data_dict.items():
            for data in data_list:
                getattr(instance, field).create(**data)

        return instance

    def update(self, instance, validated_data):
        rel_data_dict = {}
        for field in self.Meta.related_fields:
            rel_data_dict[field] = validated_data.pop(field)

        instance = super().update(instance, validated_data)

        for field, data_list in rel_data_dict.items():
            lookup = self.related_fields[field]
            getattr(instance, field).exclude(
                **{f'{lookup}__in': get_lookup_values(data_list, lookup)}
            ).delete()

            for data in data_list:
                if lookup_value := data.pop(lookup, None):
                    instance.adjustments.update_or_create(**{lookup: lookup_value}, defaults=data)
                else:
                    instance.adjustments.create(**data)

        return instance


__all__ = (
    'RelatedModelSerializer',
    'make_nested_writable',
    'HasRelatedFieldsModelSerializer',
)
