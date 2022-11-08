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
    return Product.objects.create(
        name="Product 1",
        price="1.00",
        code_id='code_id_1',
    )


@pytest.fixture
def create_product(create_category):
    return Product.objects.create(
        name="Product 1",
        price="1.00",
        code_id='code_id_1',
        category=create_category,
    )


def test_serializer_create(db):
    product_1 = dict(
        name="Created Product",
        price='1.00',
        code_id='code_id',
    )
    products = [product_1]
    category_data = dict(name="Category 1", products=products)

    serializer = CategorySerializer(data=category_data)
    assert serializer.is_valid()
    d = serializer.validated_data  # This is a dict
    created_category = serializer.save()
    assert created_category.products.count() == 1