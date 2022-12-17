from itertools import product

import pytest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from dj_kaos_utils.rest.serializers import WritableNestedSerializer
from simple.models import Category, Product2


class ProductSerializer(WritableNestedSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Product2
        fields = (
            'id',
            'name',
            'price',
            'code_id',
            'category',
        )
        lookup_field = 'id'


class NestedProductSerializer(ProductSerializer):
    id = serializers.IntegerField(required=False)

    class Meta(ProductSerializer.Meta):
        extra_kwargs = {'category': {'required': False}}


def make_nested_writable(**kwargs):
    class CategorySerializer(WritableNestedSerializer):
        id = serializers.IntegerField(required=False)
        products2 = NestedProductSerializer(many=True, **kwargs)

        class Meta:
            model = Category
            fields = (
                'id',
                'name',
                'slug',
                'products2',
            )
            read_only_fields = ('slug',)
            lookup_field = 'id'

    return CategorySerializer


# Test all combinations of can_get, can_update, can_create
@pytest.fixture(scope="module", params=product([False, True], [False, True], [False, True]))
def category_serializer(request):
    can_get, can_update, can_create = request.param
    return make_nested_writable(can_get=can_get, can_update=can_update, can_create=can_create)


@pytest.fixture
def category_data(category_serializer, category):
    return category_serializer(category).data


@pytest.fixture
def category(db):
    category = Category.objects.create(
        id=1,
        name='Category 1'
    )
    return category


@pytest.fixture
def product(category):
    return Product2.objects.create(
        id=1,
        name="Product 1",
        price="1.00",
        code_id='code_id_1',
        category=category,
    )


@pytest.fixture
def category_data(category, product, category_serializer):
    return category_serializer(category).data


def test_serializer_create(category_serializer, category, category_data):
    create_product = {
        'name': "Created Product",
        'price': '1.00',
        'code_id': 'code_id',
    }
    category_data['products2'] = [create_product]

    serializer = category_serializer(instance=category, data=category_data)
    serializer.is_valid(raise_exception=True)
    if serializer.fields['products2'].child.can_create:
        category = serializer.save()
        assert category.products2.count() == 2
        category.products2.get(name=create_product['name'])
    else:
        with pytest.raises(ValidationError):
            serializer.save()


def test_serializer_update(category_serializer, category, category_data):
    category_data['products2'][0]['name'] = "Updated Product"

    serializer = category_serializer(instance=category, data=category_data)
    serializer.is_valid(raise_exception=True)
    if serializer.fields['products2'].child.can_update:
        category = serializer.save()
        assert category.products2.count() == 1
        category.products2.get(name=category_data['products2'][0]['name'])
    else:
        with pytest.raises(ValidationError):
            serializer.save()


def test_serializer_get(category_serializer, category, category_data):
    new_product = Product2.objects.create(
        id=2,
        name="Product 2",
        price="2.00",
        code_id='code_id_2',
        category=Category.objects.create(
            name='Category 5'
        ),
    )
    category_data['products2'] = [new_product.id]

    serializer = category_serializer(instance=category, data=category_data)
    if serializer.fields['products2'].child.can_get:
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        assert category.products2.count() == 2
        category.products2.get(id=new_product.id)
    else:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()
