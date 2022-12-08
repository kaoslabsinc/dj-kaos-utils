from simple.models import Category, Product
from rest_framework import serializers
from dj_kaos_utils.rest.serializers import WritableNestedSerializer
from itertools import product
import pytest

from rest_framework.exceptions import ValidationError

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

# Test all combinations of can_get, can_update, can_create
@pytest.fixture(scope="module", params=product([False, True], [False, True], [False, True]))
def category_serializer(request):
    can_get, can_update, can_create = request.param
    return make_nested_writable(can_get=can_get, can_update=can_update, can_create=can_create)

@pytest.fixture
def category_data(category_serializer, category):
    return category_serializer(category).data

@pytest.fixture
def category(product):
    category = Category.objects.create(
        id=1,
        name='Category 1'
    )
    category.products.add(product)
    return category


@pytest.fixture
def product(db):
    return Product.objects.create(
        id=1,
        name="Product 1",
        price="1.00",
        code_id='code_id_1',        
    )


def test_serializer_create(category_serializer, category, category_data):
    create_product = {
        'name': "Created Product",
        'price': '1.00',
        'code_id': 'code_id',
    }
    category_data['products'] = [create_product]

    serializer = category_serializer(instance=category, data=category_data)
    serializer.is_valid(raise_exception=True)
    if serializer.fields['products'].child.can_create:
        category = serializer.save()
        assert category.products.count() == 2
        category.products.get(name=create_product['name'])
    else:
        with pytest.raises(ValidationError):
            serializer.save()


def test_serializer_update(category_serializer, category, category_data):
    category_data['products'][0]['name'] = "Updated Product"

    serializer =category_serializer(instance=category, data=category_data)
    serializer.is_valid(raise_exception=True)
    if serializer.fields['products'].child.can_update:
        category = serializer.save()
        assert category.products.count() == 1
        category.products.get(name=category_data['products'][0]['name'])
    else:
        with pytest.raises(ValidationError):
            serializer.save()

def test_serializer_get(category_serializer, category, category_data):
    new_product = Product.objects.create(
        id=2,
        name="Product 2",
        price="2.00",
        code_id='code_id_2',        
    )
    category_data['products'] = [new_product.id]

    serializer =category_serializer(instance=category, data=category_data)
    if serializer.fields['products'].child.can_get:
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        assert category.products.count() == 2
        category.products.get(id=new_product.id)
    else:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()
