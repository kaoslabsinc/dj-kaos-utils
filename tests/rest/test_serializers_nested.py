import pytest
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from dj_kaos_utils.rest.serializers import WritableNestedSerializer
from simple.models import Category, Product

empty_kwargs = dict(can_create=False, can_update=False, can_get=False)
get_kwargs = dict(can_create=False, can_update=False, can_get=True)
update_kwargs = dict(can_create=False, can_update=True, can_get=False)
update_get_kwargs = dict(can_create=False, can_update=True, can_get=True)
create_kwargs = dict(can_create=True, can_update=False, can_get=False)
create_get_kwargs = dict(can_create=True, can_update=False, can_get=True)
create_update_kwargs = dict(can_create=True, can_update=True, can_get=False)
create_update_get_kwargs = dict(can_create=True, can_update=True, can_get=True)


class CategorySerializer(WritableNestedSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
        )
        read_only_fields = ('slug', )


def make_nested_writable(**kwargs):

    class ProductSerializer(WritableNestedSerializer):
        category = CategorySerializer(lookup_field='id', **kwargs)

        class Meta:
            model = Product
            fields = (
                'name',
                'price',
                'code_id',
                'category',
            )

    return ProductSerializer


@pytest.fixture
def category():
    return Category.objects.create(
        id=1,
        name='Category 1'
    )


@pytest.fixture
def product(category):
    return Product.objects.create(
        id=1,
        category=category,
        name="Product 1",
        price="1.00",
        code_id='code_id_1',        
    )


def _test_create(product, nested_writable_kwargs, raise_exception=False):
    product_data = make_nested_writable(**nested_writable_kwargs)(product).data
    product_data['category'] = {'name': 'Create Category'}
    serializer = make_nested_writable(**nested_writable_kwargs)(
        data=product_data)
    assert serializer.is_valid(raise_exception=raise_exception)
    product = serializer.save()
    assert product.category.name == product_data['category']['name']


def _test_update(product, nested_writable_kwargs, raise_exception=False):
    product_data = make_nested_writable(**nested_writable_kwargs)(product).data
    product_data['category'] = {'id': 1, 'name': 'Update Category'}
    serializer = make_nested_writable(**nested_writable_kwargs)(
        data=product_data)
    assert serializer.is_valid(raise_exception=raise_exception)
    product = serializer.save()
    assert product.category.id == product_data['category']['id']
    assert product.category.name == product_data['category']['name']


def _test_get(product, nested_writable_kwargs, raise_exception=False):
    product_data = make_nested_writable(**nested_writable_kwargs)(product).data
    product_data['category'] = 1
    serializer = make_nested_writable(**nested_writable_kwargs)(
        data=product_data)
    # assert serializer.is_valid(raise_exception=raise_exception)
    serializer.is_valid(raise_exception=True)
    product = serializer.save()
    assert product.category.id == product_data['category']


def _test_create_raise_exception(_, nested_writable_kwargs):
    with pytest.raises(ValidationError):
        _test_create(_, nested_writable_kwargs, raise_exception=True)


def _test_update_raise_exception(product, nested_writable):
    with pytest.raises(ValidationError):
        _test_update(product, nested_writable, raise_exception=True)


def _test_get_raise_exception(product, nested_writable):
    with pytest.raises(ValidationError):
        _test_get(product, nested_writable, raise_exception=True)


def _test_create_update_get(product, nested_writable_kwargs, create, update,
                            get):
    args = [product, nested_writable_kwargs]
    _test_create(*args) if create else _test_create_raise_exception(*args)
    _test_update(*args) if update else _test_update_raise_exception(*args)
    _test_get(*args) if get else _test_get_raise_exception(*args)


def test_serializer_empty(db):
    with pytest.raises(AssertionError):
        make_nested_writable(**empty_kwargs)()


def test_serializer_create(db, product):
    _test_create_update_get(product,
                            create_kwargs,
                            create=True,
                            update=False,
                            get=False)


def test_serializer_update(db, product):
    _test_create_update_get(product,
                            update_kwargs,
                            create=False,
                            update=True,
                            get=False)


def test_serializer_get(db, product):
    _test_create_update_get(product,
                            get_kwargs,
                            create=False,
                            update=False,
                            get=True)


def test_serializer_create_update(db, product):
    _test_create_update_get(product,
                            create_update_kwargs,
                            create=True,
                            update=True,
                            get=False)


def test_serializer_create_get(db, product):
    _test_create_update_get(product,
                            create_get_kwargs,
                            create=True,
                            update=False,
                            get=True)


def test_serializer_update_get(db, product):
    _test_create_update_get(product,
                            update_get_kwargs,
                            create=False,
                            update=True,
                            get=True)


def test_serializer_create_update_get(db, product):
    _test_create_update_get(product,
                            create_update_get_kwargs,
                            create=True,
                            update=True,
                            get=True)
