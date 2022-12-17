import pytest
from rest_framework import serializers

from dj_kaos_utils.rest.serializers import WritableNestedSerializer
from simple.models import Category


class CategorySerializer(WritableNestedSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
        )
        read_only_fields = ('slug',)
        lookup_field = 'id'


@pytest.fixture
def category():
    return Category.objects.create(
        id=1,
        name='Category 1'
    )


@pytest.fixture
def category_data(category):
    return CategorySerializer(category).data


def test_cannot_change_pk(db, category, category_data):
    return  # TODO: temporarily disabling test
    category_data['id'] = 2

    serializer = CategorySerializer(instance=category, data=category_data)
    assert serializer.is_valid()
    updated_category = serializer.save()
    assert Category.objects.count() == 1
    assert updated_category.id == 1
