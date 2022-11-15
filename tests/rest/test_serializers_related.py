import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from dj_kaos_utils.rest.serializers import make_nested_writable
from simple.models import Product

empty_kwargs = dict(create=False, update=False, get=False)
get_kwargs = dict(create=False, update=False, get=True)
update_kwargs = dict(create=False, update=True, get=False)
update_get_kwargs = dict(create=False, update=True, get=True)
create_kwargs = dict(create=True, update=False, get=False)
create_get_kwargs = dict(create=True, update=False, get=True)
create_update_kwargs = dict(create=True, update=True, get=False)
create_update_get_kwargs = dict(create=True, update=True, get=True)


class ProductModelSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'name',
            'price',
            'code_id',
        )
        lookup_field = 'id'


@pytest.fixture
def product():
    return Product.objects.create(
        name="Product 1",
        price="1.00",
        code_id='code_id_1',
    )


def _test_create(nested_writable, raise_exception=False):
    data = {
        'name': "Created Product",
        'price': '1.00',
        'code_id': 'code_id_1',
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid(raise_exception=raise_exception)
    obj = serializer.validated_data
    Product.objects.get(id=obj.id)


def _test_update(product, nested_writable, raise_exception=False):
    data = {
        'id': product.id,
        'name': "New Name",
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid(raise_exception=raise_exception)
    updated_obj = serializer.validated_data
    assert updated_obj.id == product.id
    assert updated_obj.name == "New Name"


def _test_get(product, nested_writable, raise_exception=False):
    data = {
        'id': product.id,
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid(raise_exception=raise_exception)
    obj = serializer.validated_data
    assert obj.id == product.id


def _test_create_raise_exception(nested_writable):
    with pytest.raises(ValidationError):
        _test_create(nested_writable, raise_exception=True)


def _test_update_raise_exception(product, nested_writable):
    with pytest.raises(ValidationError):
        _test_update(product, nested_writable, raise_exception=True)


def _test_get_raise_exception(product, nested_writable):
    with pytest.raises(ValidationError):
        _test_get(product, nested_writable, raise_exception=True)


def _test_create_update_get(product, nw, create, update, get):
    args = [product, nw]
    _test_create(nw) if create else _test_create_raise_exception(nw)
    _test_update(*args) if update else _test_update_raise_exception(*args)
    _test_get(*args) if get else _test_get_raise_exception(*args)


def test_serializer_empty(db):
    with pytest.raises(AssertionError):
        make_nested_writable(ProductModelSerializer, **empty_kwargs)()


def test_serializer_create(db, product):
    nested_writable = make_nested_writable(ProductModelSerializer, **create_kwargs)
    _test_create_update_get(product,
                            nested_writable,
                            create=True,
                            update=False,
                            get=False)


def test_serializer_update(db, product):
    nested_writable = make_nested_writable(ProductModelSerializer, **update_kwargs)
    _test_create_update_get(product,
                            nested_writable,
                            create=False,
                            update=True,
                            get=False)


def test_serializer_get(db, product):
    nested_writable = make_nested_writable(ProductModelSerializer, **get_kwargs)
    _test_create_update_get(product,
                            nested_writable,
                            create=False,
                            update=False,
                            get=True)


def test_serializer_create_update(db, product):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           **create_update_kwargs)
    _test_create_update_get(product,
                            nested_writable,
                            create=True,
                            update=True,
                            get=False)


def test_serializer_create_get(db, product):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           **create_get_kwargs)
    _test_create_update_get(product,
                            nested_writable,
                            create=True,
                            update=False,
                            get=True)


def test_serializer_update_get(db, product):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           **update_get_kwargs)
    _test_create_update_get(product,
                            nested_writable,
                            create=False,
                            update=True,
                            get=True)


def test_serializer_create_update_get(db, product):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           **create_update_get_kwargs)
    _test_create_update_get(product,
                            nested_writable,
                            create=False,
                            update=True,
                            get=True)


def test_serializer_create_update_get(db, product):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           **create_update_get_kwargs)
    _test_create_update_get(product,
                            nested_writable,
                            create=True,
                            update=True,
                            get=True)
