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
def category_1_data():
    return dict(name="Category 1")


@pytest.fixture
def category_1(category_1_data):
    return Category.objects.create(**category_1_data)


@pytest.fixture
def create_product(create_category):
    return Product.objects.create(
        name="Product 1",
        price="1.00",
        code_id='code_id_1',
        category=create_category,
    )


@pytest.fixture
def product_1_data():
    return dict(
        name="Product 1",
        price='1.00',
        code_id='code_id_1',
    )


@pytest.fixture
def product_2_data():
    return dict(
        name="Product 2",
        price='2.00',
        code_id='code_id_2',
    )


@pytest.fixture
def product_1(product_1_data):
    return Product.objects.create(**product_1_data)


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
    created_category = serializer.save()
    assert created_category.products.count() == 1


def test_serializer_create_multiple(db):
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
    products = [product_1, product_2]
    category_data = dict(name="Category 1", products=products)

    serializer = CategorySerializer(data=category_data)
    assert serializer.is_valid()
    created_category = serializer.save()
    assert created_category.products.count() == 2
    created_product_1 = created_category.products.get(name=product_1['name'])
    created_product_2 = created_category.products.get(name=product_2['name'])


def test_serializer_update_replace_obj(db, category_1_data, category_1,
                                       product_1, product_2_data):
    category_1.products.set([product_1])
    data = dict(
        products=[product_2_data],
        name=category_1.name,
        id=category_1.id,
    )
    serializer = CategorySerializer(data=data)
    assert serializer.is_valid()
    created_category = serializer.save()
    assert created_category.products.count() == 1
    created_product_1 = created_category.products.get(
        name=product_2_data['name'])
