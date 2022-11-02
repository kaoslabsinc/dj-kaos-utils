from dataclasses import MISSING
from typing import Type

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class RelatedModelSerializer(serializers.ModelSerializer):
    lookup_field = None
    should_create = False
    should_update = False

    def __init__(self, *args, **kwargs):
        self.lookup_field = kwargs.pop('lookup_field', self.lookup_field) or getattr(self.Meta, 'lookup_field', None)
        self.should_create = kwargs.pop('should_create', self.should_create)
        self.should_update = kwargs.pop('should_update', self.should_update)
        super().__init__(*args, **kwargs)

    def _get_model_cls_and_lookup(self, validated_data):
        model = self.Meta.model
        # TODO: What about the case where the combination of two or more fields constitute a key?
        lookup_field = self.lookup_field
        lookup_value = validated_data.get(lookup_field, MISSING)
        return model, lookup_field, lookup_value

    def get_object(self, validated_data):
        model, lookup_field, lookup_value = self._get_model_cls_and_lookup(validated_data)
        if lookup_value is MISSING:
            # TODO: should be caught in validation
            raise ValidationError({lookup_field: f"{lookup_field} is required to look up the object"})
        # TODO: Should we also check the validity of the lookup value during validation?
        return model.objects.get(**{lookup_field: lookup_value})

    def create_object(self, validated_data):
        model, lookup_field, lookup_value = self._get_model_cls_and_lookup(validated_data)
        if lookup_value is not MISSING:
            # TODO: should be caught in validation
            raise ValidationError({
                lookup_field: f"{lookup_field} is defined but shouldn't be since we only want to create new objects"
            })
        return self.create(validated_data)

    def update_object(self, validated_data):
        model, lookup_field, lookup_value = self._get_model_cls_and_lookup(validated_data)
        instance = self.get_object(validated_data)
        validated_data.pop(lookup_field)
        self.update(instance, validated_data)

    def _x_or_create_object(self, validated_data, update=False):
        model, lookup_field, lookup_value = self._get_model_cls_and_lookup(validated_data)
        if lookup_value is MISSING:
            return self.create(validated_data), True
        validated_data.pop(lookup_field)
        if not update:
            return model.objects.get_or_create(
                **{lookup_field: lookup_value},
                defaults=validated_data,
            )
        else:
            return model.objects.update_or_create(
                **{lookup_field: lookup_value},
                defaults=validated_data,
            )

    def get_or_create_object(self, validated_data):
        return self._x_or_create_object(validated_data)

    def update_or_create_object(self, validated_data):
        return self._x_or_create_object(validated_data, update=True)

    def to_internal_value(self, data):
        assert self.lookup_field is not None, "You should specify lookup_field"
        if self.should_create and self.should_update:
            return self.update_or_create_object(data)[0]
        elif self.should_create:
            return self.get_or_create_object(data)[0]
        elif self.should_update:
            return self.update_object(data)
        else:
            return self.get_object(data)


def make_nested_writable(serializer_cls: Type[serializers.ModelSerializer],
                         lookup_field=None,
                         should_create=False,
                         should_update=False):
    class WritableNestedXXX(RelatedModelSerializer, serializer_cls):
        pass

    WritableNestedXXX.lookup_field = lookup_field
    WritableNestedXXX.should_create = should_create
    WritableNestedXXX.should_update = should_update
    WritableNestedXXX.__name__ = WritableNestedXXX.__name__.replace('XXX', serializer_cls.__name__)

    return WritableNestedXXX


__all__ = (
    'RelatedModelSerializer',
    'make_nested_writable',
)
