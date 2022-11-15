from typing import Type

from rest_framework import serializers
from rest_framework.settings import api_settings

from .utils import get_lookup_values

NON_FIELD_ERRORS_KEY = api_settings.NON_FIELD_ERRORS_KEY


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
        assert self.can_get or self.can_create or self.can_update, \
            "At least one of can_get, can_create or can_update should be set."
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_object(model, lookup_field, lookup_value):
        try:
            return model.objects.get(**{lookup_field: lookup_value})
        except model.DoesNotExist:
            raise serializers.ValidationError({
                lookup_field: f"{model._meta.object_name} matching query {lookup_field}={lookup_value} does not exist."
            })

    def to_internal_value(self, data):
        lookup_field = self.lookup_field
        assert lookup_field is not None, "You should specify lookup_field"

        lookup_value = data.pop(lookup_field, None)
        model = self.Meta.model

        if lookup_value is not None:
            if data:  # { uuid: "xxxxxxxx-xxxx-...", name : "Name" }, update
                if self.can_update:
                    instance = self._get_object(model, lookup_field, lookup_value)
                    return self.update(instance, data)
                else:
                    raise serializers.ValidationError({
                        NON_FIELD_ERRORS_KEY: "This api is not configured to update existing objects"
                    })
            else:  # e.g. { uuid: "xxxxxxxx-xxxx-..." }, get
                if self.can_get:
                    return self._get_object(model, lookup_field, lookup_value)
                else:
                    raise serializers.ValidationError({
                        NON_FIELD_ERRORS_KEY: "This api is not configured to get existing objects"
                    })
        else:  # e.g. { name : "Name" } or {} aka just a prompt to create the default object of this type
            if self.can_create:
                return self.create(data)
            else:
                raise serializers.ValidationError({
                    NON_FIELD_ERRORS_KEY: "This api is not configured to create new objects"
                })


def make_nested_writable(
    serializer_cls: Type[serializers.ModelSerializer],
    lookup_field=RelatedModelSerializer.lookup_field,
    get=RelatedModelSerializer.can_get,
    create=RelatedModelSerializer.can_create,
    update=RelatedModelSerializer.can_update
):
    class WritableNestedXXX(RelatedModelSerializer, serializer_cls):
        pass

    WritableNestedXXX.lookup_field = lookup_field
    WritableNestedXXX.can_get = get
    WritableNestedXXX.can_create = create
    WritableNestedXXX.can_update = update
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

    @staticmethod
    def _get_object(qs, lookup_field, lookup_value):
        try:
            return qs.get(**{lookup_field: lookup_value})
        except qs.model.DoesNotExist:
            raise serializers.ValidationError({
                lookup_field: f"{qs.model._meta.object_name} matching query {lookup_field}={lookup_value} does not exist."
            })

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
            rel_manager = getattr(instance, field)
            lookup = self.related_fields[field]
            rel_manager.exclude(
                **{f'{lookup}__in': get_lookup_values(data_list, lookup)}
            ).delete()

            for data in data_list:
                lookup_value = data.pop(lookup, None)
                if lookup_value is not None:
                    rel_instance = self._get_object(rel_manager, lookup, lookup_value)
                    if data:
                        for k, v in data.items():
                            setattr(rel_instance, k, v)
                            rel_instance.save()
                    else:
                        pass  # just reasserting the existing of this relationship (won't get deleted up there) TODO
                        # What if we want to add an existing object to the relationship? can we do that?
                else:
                    rel_manager.create(**data)

        return instance


__all__ = (
    'RelatedModelSerializer',
    'make_nested_writable',
    'HasRelatedFieldsModelSerializer',
)
