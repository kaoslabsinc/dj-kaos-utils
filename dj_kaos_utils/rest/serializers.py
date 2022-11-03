from dataclasses import MISSING
from typing import Type

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .utils import get_lookup_values


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
        try:
            return model.objects.get(**{lookup_field: lookup_value})
        except model.DoesNotExist:
            raise ValidationError({lookup_field: f"{model._meta.object_name} matching query {lookup_field}={lookup_value} does not exist."})


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
