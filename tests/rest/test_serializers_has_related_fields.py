from dj_kaos_utils.rest.serializers import HasRelatedFieldsModelSerializer

from simple.models import Category, Product
from rest_framework import serializers

import pytest


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price',
            'code_id',
            'category',
        )


class CategorySerializer(HasRelatedFieldsModelSerializer,
                         serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'products')
        related_fields = ('products', )


@pytest.fixture
def create_category():

    def _create_category(products=None):
        category = Category.objects.create(name="Category")
        if products:
            category.products.set(products)
        return CategorySerializer(category).data

    return _create_category


@pytest.fixture
def product():
    return Product.objects.create(
        name="Product 1",
        price='1.00',
        code_id='code_id_1',
    )


def test_serializer_create_single(db):
    product_1 = dict(
        name="Created Product",
        price='1.00',
        code_id='code_id',
    )
    products = [product_1]
    category_data = dict(name="Category 1", products=products)

    serializer = CategorySerializer(data=category_data)
    assert serializer.is_valid()
    created_category = serializer.save()
    assert created_category.products.count() == 1


def test_serializer_create_multiple(db, create_category):
    data = create_category()
    product_1 = dict(
        name="Product 1",
        price='1.00',
        code_id='code_id_1',
    )
    product_2 = dict(
        name="Product 2",
        price='2.00',
        code_id='code_id_2',
    )
    data['products'] = [product_1, product_2]

    serializer = CategorySerializer(data=data)
    assert serializer.is_valid()

    created_category = serializer.save()
    assert created_category.products.count() == 2
    created_category.products.get(name=product_1['name'])
    created_category.products.get(name=product_2['name'])


def test_serializer_update_replace_obj(
    db,
    create_category,
    product,
):
    data = create_category(products=[product])
    new_product = dict(
        name="New Product",
        price='2.00',
        code_id='code_id_2',
    )

    data['products'] = [new_product]

    serializer = CategorySerializer(data=data)
    assert serializer.is_valid()

    updated_category = serializer.save()
    assert updated_category.products.count() == 1
    updated_category.products.get(name=new_product['name'])


def test_serializer_update_update_obj(db, create_category, product):
    data = create_category(products=[product])
    data['products'][0]['name'] = 'Updated Product'

    serializer = CategorySerializer(data=data)
    assert serializer.is_valid()

    updated_category = serializer.save()
    assert updated_category.products.count() == 1
    created_product_1 = updated_category.products.get(name='Updated Product')
