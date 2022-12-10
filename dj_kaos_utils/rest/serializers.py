from typing import Mapping, Type

from rest_framework import serializers
from rest_framework.settings import api_settings

NON_FIELD_ERRORS_KEY = api_settings.NON_FIELD_ERRORS_KEY

from django.db import models


# class WritableNestedSerializer(serializers.ModelSerializer):
#     """
#     WritableNestedSerializer functions as a ModelSerializer when serializing (retrieve and list) returning
#     nested models. When deserializing, acts as a SlugRelatedField if data is a string
#     (example UUID value) otherwise behaves as a writable nested serializer.
#     """
#
#     # Disable errors on nested writes. We know what we're doing!
#     serializers.raise_errors_on_nested_writes = lambda x, y, z: None
#
#     def __init__(self, *args, **kwargs):
#         self.lookup_field = kwargs.pop('lookup_field', self.Meta.lookup_field)
#         self.can_get = kwargs.pop('can_get', True)
#         self.can_create = kwargs.pop('can_create', False)
#         self.can_update = kwargs.pop('can_update', False)
#         super().__init__(*args, **kwargs)
#
#     def to_internal_value(self, data):
#         if isinstance(data, Mapping):
#             # data is a dict handle as ModelSerializer
#             return super().to_internal_value(data)
#         else:
#             # data is a lookup_value handle as SlugRelatedField
#             if self.can_get:
#                 return self.get_object(data)
#             else:
#                 self.raise_validation_error('get')
#
#     def save(self, **kwargs):
#         # Disable modifying value of lookup_field on save of root object. lookup_field cannot be read-only as we need
#         # to allow setting on nested serializers.
#         self._validated_data.pop(self.lookup_field, None)
#         return self.save_nested_fields(self, self._validated_data)
#
#     def save_nested_fields(self, field, validated_data, commit=True):
#         # Traverse validated_data searching for OrderedDict values and saving them to Django models.
#         # IMPORTANT: self will always reference the root (top) object upon which save() was called. Calling any method
#         # on the self object ie (self.lookup_field, etc.) is almost certainly incorrect. Use the field object
#         # instead ie. field.lookup_field
#
#         # If validated_data is already a Django a model we are done.
#         if isinstance(validated_data, django.db.models.Model):
#             return validated_data
#
#         m2m_fields = []
#         # Iterating over a copy of validated_data to be able to delete keys
#         for attr, val in validated_data.copy().items():
#             if isinstance(val, OrderedDict):
#                 # Nested field.
#                 validated_data[attr] = self.save_nested_fields(field.fields[attr], val)
#             elif isinstance(val, list):
#                 # Reverse foreign key many=True. val is a list of related objects.
#                 # .child accesses child serializer wrapped by ListSerializer
#                 child = field.fields[attr].child
#                 m2m_fields.append((child, attr, [child.save_nested_fields(child, v, commit=False) for v in val]))
#                 # Remove key from validated_data. We will process the reverse m2m fields after saving
#                 del validated_data[attr]
#
#         if field == self:
#             # We are done. Return validated_data and allow call to super().save() on root object since
#             # handling of decision to save vs. update is differnet than for nested objects.
#             if commit:
#                 self._validated_data = validated_data
#                 instance = super().save()
#             else:
#                 return validated_data
#         else:
#             if field.lookup_field in validated_data:
#                 instance = field.update_object(validated_data)
#             else:
#                 instance = field.create_object(validated_data)
#
#         # Handle m2m objects
#         # NOTE: Does not support removing any objects from the related object set. Objects in the
#         # list are only added or created in the related object set. Removing relationships requires
#         # allowing foreign key value to be null. To remove objects from the related object set
#         # either add the object to another related object set or the object itself should be deleted.
#         for field, attr, val in m2m_fields:
#             related_manager = getattr(instance, attr)
#             for obj in val:
#                 # obj values are either OrderDict or Django models
#                 if isinstance(obj, OrderedDict):
#                     if field.lookup_field in obj:
#                         # Update existing object and add it to the related object set.
#                         updated_obj = field.update_object(obj)
#                         related_manager.add(updated_obj)
#                     else:
#                         # Create new object, save it and put it in the related object set.
#                         # Check can_create as related_manager.create() doesn't use field.create() method
#                         if field.can_create:
#                             related_manager.create(**obj)
#                         else:
#                             field.raise_validation_error('create')
#                 else:
#                     # Add an existing Django model to the related object set.
#                     related_manager.add(obj)
#
#         return instance
#
#     def get_object(self, lookup_value):
#         model = self.Meta.model
#         try:
#             return model.objects.get(**{self.lookup_field: lookup_value})
#         except model.DoesNotExist:
#             raise serializers.ValidationError({
#                 self.lookup_field:
#                     f"{model._meta.object_name} matching query {self.lookup_field}={lookup_value} does not exist."
#             })
#
#     def update_object(self, validated_data):
#         if self.can_update:
#             lookup_value = validated_data[self.lookup_field]
#             instance = self.get_object(lookup_value)
#             return self.update(instance, validated_data)
#         else:
#             self.raise_validation_error('update')
#
#     def create_object(self, validated_data):
#         if self.can_create:
#             return self.create(validated_data)
#         else:
#             self.raise_validation_error('create')
#
#     def raise_validation_error(self, action):
#         raise serializers.ValidationError({
#             NON_FIELD_ERRORS_KEY: f"{self.__class__.__name__} is not configured to {action}"
#         })


def make_nested_writable(serializer_cls: Type[serializers.ModelSerializer]):
    class WritableNestedXXX(WritableNestedSerializer, serializer_cls):
        pass

    WritableNestedXXX.__name__ = WritableNestedXXX.__name__.replace('XXX', serializer_cls.__name__)

    return WritableNestedXXX


__all__ = (
    'WritableNestedSerializer',
    'make_nested_writable',
)


class WritableNestedSerializer(serializers.ModelSerializer):
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
        Returns a dictionary of nested fields and their data from the validated_data dictionary.
        The data for each nested field is removed from the validated_data dictionary.
        """
        nested_fields = {}
        for field_name, field in self.fields.items():
            if isinstance(field, WritableNestedSerializer):
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
            NON_FIELD_ERRORS_KEY: f"{self.__class__.__name__} is not configured to {action}"
        })

    def save_nested_fields(self, validated_data):
        nested_fields = self.pop_nested_fields(validated_data)

        for field_name, nested_data in nested_fields.items():
            nested_serializer: WritableNestedSerializer = self.fields[field_name]

            if isinstance(nested_data, models.Model):
                validated_data[field_name] = nested_data
            elif isinstance(nested_data, Mapping):
                if nested_serializer.lookup_field in nested_data:
                    if nested_serializer.can_update:
                        nested_lookup_value = nested_data[nested_serializer.lookup_field]
                        nested_instance = nested_serializer.get_object(nested_lookup_value)
                        validated_data[field_name] = nested_serializer.update(nested_instance, nested_data)
                    else:
                        self._raise_action_validation_error('update')
                else:
                    if nested_serializer.can_create:
                        validated_data[field_name] = nested_serializer.create(nested_data)
                    else:
                        self._raise_action_validation_error('create')
            else:
                # data is a lookup_value handle as SlugRelatedField
                lookup_value = nested_data
                if self.can_get:
                    validated_data[field_name] = nested_serializer.get_object(lookup_value)
                else:
                    self._raise_action_validation_error('get')

    def create(self, validated_data):
        self.save_nested_fields(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.save_nested_fields(validated_data)
        return super().update(instance, validated_data)
