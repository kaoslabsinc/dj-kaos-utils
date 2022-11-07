from django.utils.safestring import mark_safe

from dj_kaos_utils.admin.utils import pp_json, _render_attrs, render_element, render_img, render_anchor
from dj_kaos_utils.rest.serializers import make_nested_writable

from simple.models import Product
from rest_framework.serializers import ModelSerializer


class ProductModelSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'name',
            'price',
            'code_id',
        )
        lookup_field ='id'


def test_serializer_create(db):
    nested_writable = make_nested_writable(ProductModelSerializer, can_create=True)
    data = {
        'name': "Product 1",
        'price': '1.00',
        'code_id': 'id01',
    }
    serializer = nested_writable(data=data)
    assert serializer.is_valid()
    obj = serializer.validated_data
    Product.objects.get(id=obj.id)