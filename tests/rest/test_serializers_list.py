from simple.models import Category, Product
from rest_framework import serializers
from dj_kaos_utils.rest.serializers import WritableNestedSerializer

import pytest


class ProductSerializer(WritableNestedSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price',
            'code_id',
            'category',
        )
        lookup_field = 'id'

def make_nested_writable(**kwargs):
    class CategorySerializer(WritableNestedSerializer):
        id = serializers.IntegerField(required=False)
        products = ProductSerializer(many=True, **kwargs)

        class Meta:
            model = Category
            fields = (
                'id',
                'name',
                'slug',
                'products',
            )
            read_only_fields = ('slug', )
            lookup_field = 'id'
    return CategorySerializer


@pytest.fixture
def category(product):
    category = Category.objects.create(
        id=1,
        name='Category 1'
    )
    category.products.add(product)
    return category


@pytest.fixture
def product():
    return Product.objects.create(
        id=1,
        name="Product 1",
        price="1.00",
        code_id='code_id_1',        
    )

@pytest.fixture
def category_data(category):
    return CategorySerializer(category).data




def test_serializer_create(db, category):
    category_data = make_nested_writable(can_create=True)(category).data
    create_product = {
        'name': "Created Product",
        'price': '1.00',
        'code_id': 'code_id',
    }
    category_data['products'] = [create_product]

    serializer = make_nested_writable(can_create=True)(instance=category, data=category_data)
    assert serializer.is_valid()
    category = serializer.save()
    assert category.products.count() == 2
    category.products.get(name=create_product['name'])


def test_serializer_update(db, category):
    category_data = make_nested_writable(can_update=True)(category).data
    category_data['products'][0]['name'] = "Updated Product"

    serializer = make_nested_writable(can_update=True)(instance=category, data=category_data)
    assert serializer.is_valid()
    category = serializer.save()
    assert category.products.count() == 1
    category.products.get(name=category_data['products'][0]['name'])


def test_serializer_get(db, category):
    category_data = make_nested_writable(can_get=True)(category).data
    new_product = Product.objects.create(
        id=2,
        name="Product 2",
        price="2.00",
        code_id='code_id_2',        
    )
    category_data['products'] = [new_product.id]

    serializer = make_nested_writable(can_get=True)(instance=category, data=category_data)
    assert serializer.is_valid()
    category = serializer.save()
    assert category.products.count() == 2
    category.products.get(id=new_product.id)
