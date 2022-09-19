from django.db import models
from django.db.models import ExpressionWrapper, F

from simple.models import Product


def test_RankedQuerySetMixin(db):
    products = [
        Product(name='name', price=i, code_id=str(i))
        for i in [1, 2, 3, 3, 4]
    ]
    Product.objects.bulk_create(products)
    ranked = list(Product.objects.all().annotate(
        price2=ExpressionWrapper(F('price'), output_field=models.IntegerField())
    ).annotate_rank('price2').values_list('code_id', 'rank').order_by('-code_id'))
    assert ranked == [
        ('4', 1),
        ('3', 2),
        ('3', 2),
        ('2', 4),
        ('1', 5),
    ]


def test_RankedQuerySetMixin_asc(db):
    products = [
        Product(name='name', price=i, code_id=str(i))
        for i in [1, 2, 3, 3, 4]
    ]
    Product.objects.bulk_create(products)
    ranked = list(Product.objects.all().annotate(
        price2=ExpressionWrapper(F('price'), output_field=models.IntegerField())
    ).annotate_rank('price2', asc=True).values_list('code_id', 'rank').order_by('code_id'))
    assert ranked == [
        ('1', 1),
        ('2', 2),
        ('3', 3),
        ('3', 3),
        ('4', 5),
    ]


def test_PageableQuerySet_paginate_minmax():
    pass


def test_PageableQuerySet_paginate_pks():
    pass


def test_PageableQuerySet_paginate_pks_not_simple():
    pass


def test_PageableQuerySet_paginate_pks_mutating():
    pass


def test_PageableQuerySet_paginate():
    pass


def test_PageableQuerySet_paginated_update():
    pass


def test_BulkUpdateCreateQuerySet__create(db):
    products = [
        Product(name='name', price=0, code_id=str(i))
        for i in range(10)
    ]
    Product.objects.bulk_update_or_create(products, 'code_id', ())
    assert Product.objects.count() == 10


def test_BulkUpdateCreateQuerySet__update(db):
    products = [
        Product(name='name', price=0, code_id=str(i))
        for i in range(5)
    ]
    Product.objects.bulk_update_or_create(products, 'code_id', ())
    assert Product.objects.count() == 5

    products = [
        Product(name='name', price=10, code_id=str(i))
        for i in range(10)
    ]
    Product.objects.bulk_update_or_create(products, 'code_id', ('price',))
    assert Product.objects.count() == 10
    assert Product.objects.get(code_id='0').price == 10


def test_BulkUpdateCreateQuerySet__no_update(db):
    products = [
        Product(name='name', price=0, code_id=str(i))
        for i in range(5)
    ]
    Product.objects.bulk_update_or_create(products, 'code_id', ())
    assert Product.objects.count() == 5

    products = [
        Product(name='name', price=10, code_id=str(i))
        for i in range(10)
    ]
    Product.objects.bulk_update_or_create(products, 'code_id', ())
    assert Product.objects.count() == 10
    assert Product.objects.get(code_id='0').price == 0


def test_BulkUpdateCreateQuerySet__multi_field_lookup(db):
    products = [
        Product(name=f'name{i % 2}', price=0, code_id=str(i))
        for i in range(5)
    ]
    Product.objects.bulk_update_or_create(products, ('name', 'code_id'), ())
    assert Product.objects.count() == 5

    products = [
        Product(name=f'name0', price=10, code_id='6')
    ]
    Product.objects.bulk_update_or_create(products, ('name', 'code_id'), ('price',))
    assert Product.objects.count() == 6
    assert Product.objects.get(code_id='6').price == 10
