from simple.models import Product


def test_RankedQuerySetMixin():
    pass


def test_RankedQuerySetMixin_asc():
    pass


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
