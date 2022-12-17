from itertools import product

import pytest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from dj_kaos_utils.rest.serializers import WritableNestedSerializer
from simple.models import Category, Product


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


def make_nested_writable(**kwargs):
    class ProductSerializer(WritableNestedSerializer):
        category = CategorySerializer(**kwargs)

        class Meta:
            model = Product
            fields = (
                'name',
                'price',
                'code_id',
                'category',
            )
            lookup_field = 'id'

    return ProductSerializer


# Test all combinations of can_get, can_update, can_create
@pytest.fixture(scope="module",
                params=product([False, True], [False, True], [False, True]))
def product_serializer(request):
    can_get, can_update, can_create = request.param
    return make_nested_writable(can_get=can_get,
                                can_update=can_update,
                                can_create=can_create)


@pytest.fixture
def product_data(product_serializer, product):
    return product_serializer(product).data


@pytest.fixture
def category(db):
    return Category.objects.create(id=1, name='Category 1')


@pytest.fixture
def product(category):
    return Product.objects.create(
        id=1,
        category=category,
        name="Product 1",
        price="1.00",
        code_id='code_id_1',
    )


def test_create(product_serializer, product_data, product):
    product_data['category'] = {'name': 'Create Category'}
    serializer = product_serializer(instance=product, data=product_data)
    serializer.is_valid(raise_exception=True)
    if serializer.fields['category'].can_create:
        product = serializer.save()
        assert product.category.name == product_data['category']['name']
    else:
        with pytest.raises(ValidationError):
            serializer.save()


def test_update(product_serializer, product_data, product):
    product_data['category'] = {'id': 1, 'name': 'Update Category'}
    serializer = product_serializer(instance=product, data=product_data)
    serializer.is_valid(raise_exception=True)
    if serializer.fields['category'].can_update:
        product = serializer.save()
        assert product.category.id == product_data['category']['id']
        assert product.category.name == product_data['category']['name']
    else:
        with pytest.raises(ValidationError):
            serializer.save()


def test_get(product_serializer, product_data, product):
    product_data['category'] = 1
    serializer = product_serializer(instance=product, data=product_data)
    if serializer.fields['category'].can_get:
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        assert product.category.id == product_data['category']
    else:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()


@pytest.mark.django_db
def test_create2(product_serializer, product_data, product):
    product_data['category'] = {'name': 'Create Category'}
    serializer = product_serializer(data=product_data)
    if serializer.fields['category'].can_create:
        assert serializer.is_valid(), serializer.errors
        product = serializer.save()
        assert product.category.name == 'Create Category'
    else:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()


@pytest.mark.django_db
def test_update2(product_serializer, product_data, product):
    product_data['category'] = {'id': 1, 'name': 'Update Category'}
    serializer = product_serializer(product, data=product_data)
    if serializer.fields['category'].can_update:
        assert serializer.is_valid(), serializer.errors
        product = serializer.save()
        assert product.category.name == 'Update Category'
        assert product.category.id == 1
    else:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()


@pytest.mark.django_db
def test_get2(product_serializer, product_data, product):
    category2 = Category.objects.create(id=2, name='Category 2')
    product_data['category'] = category2.id
    serializer = product_serializer(product, data=product_data)
    if serializer.fields['category'].can_get:
        assert serializer.is_valid(), serializer.errors
        product = serializer.save()
        assert product.category.name == 'Category 2'
    else:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()
