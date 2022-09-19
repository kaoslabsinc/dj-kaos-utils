from django.core.management import call_command

from simple.models import Product


def test_TaskCommand(db):
    call_command('create_sample_products')
    assert Product.objects.count() == 10
