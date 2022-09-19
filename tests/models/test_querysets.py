import pytest
from django.db import models
from django.db.models import ExpressionWrapper, F, Value

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


def test_PageableQuerySet_paginate_minmax__empty(db):
    pg_qs = Product.objects.all().paginate_minmax(100)
    with pytest.raises(StopIteration):
        next(pg_qs)


def test_PageableQuerySet_paginate_minmax(db):
    products = [
        Product(name=f'name{i}', price=0, code_id=str(i))
        for i in range(1000)
    ]
    Product.objects.bulk_create(products)
    for i, page in enumerate(Product.objects.all().paginate_minmax(100)):
        assert page.filter(code_id=i * 100 + 50).exists

    Product.objects.filter(code_id__in=[1, 2, 3, 4]).delete()
    paginated_qs = Product.objects.all().paginate_minmax(10)

    assert next(paginated_qs).count() == 6
    assert next(paginated_qs).count() == 10


def test_PageableQuerySet_paginate_pks(db):
    products = [
        Product(name=f'name{i}', price=0, code_id=str(i))
        for i in range(1000)
    ]
    Product.objects.bulk_create(products)
    for i, page in enumerate(Product.objects.all().order_by('pk').paginate_pks(100)):
        assert page.filter(code_id=i * 100 + 50).exists

    Product.objects.filter(code_id__in=[1, 2, 3, 4]).delete()
    paginated_qs = Product.objects.all().order_by('pk').paginate_pks(10)

    assert next(paginated_qs).count() == 10
    assert next(paginated_qs).count() == 10


def test_PageableQuerySet_paginate_pks__mutate(db):
    products = [
        Product(name=f'name{i}', price=0, code_id=str(i))
        for i in range(100)
    ]
    Product.objects.bulk_create(products)
    qs = Product.objects.filter(name__in=['name2', 'name12', 'name22']).order_by('pk')
    pg_qs = qs.paginate_pks(1)
    next_p = next(pg_qs)
    assert next_p[0].name == 'name2'
    next_p.update(name='name45')
    next_p = next(pg_qs)
    assert next_p[0].name == 'name22'


def test_PageableQuerySet_paginate_pks_not_simple(db):
    products = [
        Product(name=f'name{i}', price=0, code_id=str(i))
        for i in range(1000)
    ]
    Product.objects.bulk_create(products)

    paginated_qs = Product.objects.all().order_by('pk').annotate(field=Value('value')).paginate_pks(10, simple=False)
    assert next(paginated_qs)[0].field == 'value'

    paginated_qs = Product.objects.all().order_by('pk').annotate(field=Value('value')).paginate_pks(10, simple=True)
    assert getattr(next(paginated_qs)[0], 'field', 'nope') == 'nope'


def test_PageableQuerySet_paginate_pks_mutating(db):
    products = [
        Product(name=f'name{i}', price=0, code_id=str(i))
        for i in range(100)
    ]
    Product.objects.bulk_create(products)
    qs = Product.objects.filter(name__in=['name2', 'name12', 'name22']).order_by('pk')
    pg_qs = qs.paginate_pks_mutating(1)
    next_p = next(pg_qs)
    assert next_p[0].name == 'name2'
    next_p.update(name='name45')
    next_p = next(pg_qs)
    assert next_p[0].name == 'name12'


def test_PageableQuerySet_paginate(db):
    products = [
        Product(name=f'name{i}', price=0, code_id=str(i))
        for i in range(10000)
    ]
    Product.objects.bulk_create(products)
    for i, page in enumerate(Product.objects.all().paginate(1000)):
        assert page.filter(code_id=i * 1000 + 500).exists


def test_PageableQuerySet_paginated_update(db):
    products = [
        Product(name=f'name{i}', price=0, code_id=str(i))
        for i in range(1000)
    ]
    Product.objects.bulk_create(products)
    Product.objects.all().paginated_update(100, lambda page: page.update(price=1000))
    assert not Product.objects.filter(price__lt=1000).exists()


def test_PageableQuerySet_paginated_update__atomic(db):
    products = [
        Product(name=f'name{i}', price=0, code_id=str(i))
        for i in range(1000)
    ]
    Product.objects.bulk_create(products)

    def update_page(page):
        if page[0].code_id == '500':
            raise Exception
        return page.update(price=1000)

    with pytest.raises(Exception):
        Product.objects.all().paginated_update(100, lambda page: update_page(page))
    assert Product.objects.filter(price__lt=1000).count() == 500


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
