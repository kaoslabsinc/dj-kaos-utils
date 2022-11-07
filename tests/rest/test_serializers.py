from dj_kaos_utils.rest.serializers import make_nested_writable

from simple.models import Product
from rest_framework.serializers import ModelSerializer
import pytest


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
def created_product():
    return Product.objects.create(
        name="Product 1",
        price="1.00",
        code_id='code_id_1',
    )


def _test_create(nested_writable):
    data = {
        'name': "Created Product",
        'price': '1.00',
        'code_id': 'code_id_1',
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid()
    obj = serializer.validated_data
    Product.objects.get(id=obj.id)


def _test_update(created_product, nested_writable):
    data = {
        'id': created_product.id,
        'name': "New Name",
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid()
    updated_obj = serializer.validated_data
    assert updated_obj.id == created_product.id
    assert updated_obj.name == "New Name"


def _test_get(created_product, nested_writable):
    data = {
        'id': created_product.id,
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid()
    obj = serializer.validated_data
    assert obj.id == created_product.id


def test_serializer_create(db):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           can_create=True)
    _test_create(nested_writable)


def test_serializer_update(db, created_product):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           can_update=True)
    _test_update(created_product, nested_writable)


def test_serializer_get(db, created_product):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           can_get=True)
    _test_get(created_product, nested_writable)


def test_serializer_create_update_do_create(db):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           can_create=True,
                                           can_update=True)
    _test_create(nested_writable)


def test_serializer_create_update_do_update(db, created_product):
    nested_writable = make_nested_writable(ProductModelSerializer,
                                           can_create=True,
                                           can_update=True)
    _test_update(created_product, nested_writable)
