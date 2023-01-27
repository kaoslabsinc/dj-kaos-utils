from typing import Type, Mapping

from django.db import models
from rest_framework import serializers
from rest_framework.serializers import ListSerializer
from rest_framework.settings import api_settings


class WritableNestedSerializer(serializers.ModelSerializer):
    """
    `WritableNestedSerializer` functions as a `ModelSerializer` when serializing (retrieve and list) returning
    nested models. When deserializing, acts as a `SlugRelatedField` if data is a string
    (example UUID value) otherwise behaves as a writable nested serializer.
    """

    # Disable errors on nested writes. We know what we're doing!
    serializers.raise_errors_on_nested_writes = lambda x, y, z: None

    def __init__(self, *args, **kwargs):
        self.lookup_field = kwargs.pop('lookup_field', self.Meta.lookup_field)
        self.can_get = kwargs.pop('can_get', True)
        self.can_create = kwargs.pop('can_create', False)
        self.can_update = kwargs.pop('can_update', False)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            # data is a dict handle as ModelSerializer
            return super().to_internal_value(data)
        else:
            # data is a lookup_value handle as SlugRelatedField
            if self.can_get:
                return self.get_object(data)
            else:
                self._raise_action_validation_error('get')

    def pop_nested_fields(self, validated_data):
        """
        Return a dictionary of nested fields and their data from the validated_data dictionary.
        The data for each nested field is removed from the validated_data dictionary.
        """
        nested_fields = {}
        for field_name, field in self.fields.items():
            if isinstance(field, WritableNestedSerializer):
                if validated_data.get(field_name) is not None:
                    nested_fields[field_name] = validated_data.pop(field_name)
        return nested_fields

    def pop_list_fields(self, validated_data):
        """
        Return a dictionary of list fields and their data from the validated_data dictionary.
        The data for each nested field is removed from the validated_data dictionary.
        """
        nested_fields = {}
        for field_name, field in self.fields.items():
            if isinstance(field, ListSerializer) and isinstance(field.child, WritableNestedSerializer):
                if validated_data.get(field_name) is not None:
                    nested_fields[field_name] = validated_data.pop(field_name)
        return nested_fields

    def get_object(self, lookup_value):
        model = self.Meta.model
        try:
            return model.objects.get(**{self.lookup_field: lookup_value})
        except model.DoesNotExist:
            raise serializers.ValidationError({
                self.lookup_field:
                    f"{model._meta.object_name} matching query {self.lookup_field}={lookup_value} does not exist."
            })

    def _raise_action_validation_error(self, action):
        raise serializers.ValidationError({
            api_settings.NON_FIELD_ERRORS_KEY: f"{self.__class__.__name__} is not configured to {action}"
        })

    def save_nested_data(self, nested_data, related_manager=None):
        if isinstance(nested_data, models.Model):
            return nested_data

        if self.lookup_field in nested_data:
            if self.can_update:
                nested_lookup_value = nested_data[self.lookup_field]
                nested_instance = self.get_object(nested_lookup_value)
                return self.update(nested_instance, nested_data)
            else:
                self._raise_action_validation_error('update')
        else:
            if self.can_create:
                if not related_manager:
                    return self.create(nested_data)
                else:
                    nested_list_fields = self.pop_list_fields(nested_data)
                    self.process_nested_fields(nested_data)
                    nested_instance = related_manager.create(**nested_data)
                    self.process_list_fields(nested_instance, nested_list_fields)
                    return nested_instance
            else:
                self._raise_action_validation_error('create')

    def process_nested_fields(self, validated_data):
        nested_fields = self.pop_nested_fields(validated_data)
        for field_name, nested_data in nested_fields.items():
            nested_serializer: WritableNestedSerializer = self.fields[field_name]
            validated_data[field_name] = nested_serializer.save_nested_data(nested_data)

    def process_list_fields(self, instance, list_fields):
        for field_name, list_data in list_fields.items():
            list_serializer: ListSerializer = self.fields[field_name]
            nested_serializer: WritableNestedSerializer = self.fields[field_name].child
            related_manager = getattr(instance, list_serializer.source)
            for nested_data in list_data:
                related_manager.add(nested_serializer.save_nested_data(nested_data, related_manager))

    def create(self, validated_data):
        list_fields = self.pop_list_fields(validated_data)
        self.process_nested_fields(validated_data)
        instance = super().create(validated_data)
        self.process_list_fields(instance, list_fields)
        return instance

    def update(self, instance, validated_data):
        list_fields = self.pop_list_fields(validated_data)
        self.process_nested_fields(validated_data)
        instance = super().update(instance, validated_data)
        self.process_list_fields(instance, list_fields)
        return instance


def make_nested_writable(serializer_cls: Type[serializers.ModelSerializer]):
    class WritableNestedXXX(WritableNestedSerializer, serializer_cls):
        pass

    WritableNestedXXX.__name__ = WritableNestedXXX.__name__.replace('XXX', serializer_cls.__name__)

    return WritableNestedXXX


__all__ = (
    'WritableNestedSerializer',
    'make_nested_writable',
)
