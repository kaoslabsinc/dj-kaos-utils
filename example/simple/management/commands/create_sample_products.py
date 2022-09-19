from dj_kaos_utils.management import TaskCommand
from ...models import Product


class Command(TaskCommand):
    def run_task(self, *args, **options):
        Product.objects.bulk_create([
            Product(name=f'name{i}', price=0, code_id=str(i))
            for i in range(10)
        ])
