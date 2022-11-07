from django.utils.safestring import mark_safe

from dj_kaos_utils.admin.utils import pp_json, _render_attrs, render_element, render_img, render_anchor
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
        lookup_field ='id'

@pytest.fixture
def created_product():
    return Product.objects.create(
        name = "Created Product",
        price = "1.00",
        code_id = 'code_id_1',
    )

def test_serializer_create(db):
    nested_writable = make_nested_writable(ProductModelSerializer, can_create=True)
    data = {
        'name': "Product 1",
        'price': '1.00',
        'code_id': 'id01',
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid()
    created_obj = serializer.validated_data
    Product.objects.get(id=created_obj.id)

def test_serializer_update(db, created_product):
    nested_writable = make_nested_writable(ProductModelSerializer, can_update=True)
    data = {
        'id': created_product.id,
        'name': "New Name",
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid()
    updated_obj = serializer.validated_data
    assert updated_obj.id == created_product.id
    assert updated_obj.name == "New Name"

def test_serializer_get(db, created_product):
    nested_writable = make_nested_writable(ProductModelSerializer, can_get=True)
    data = {
        'id': created_product.id,
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid()
    obj = serializer.validated_data
    assert obj.id == created_product.id
