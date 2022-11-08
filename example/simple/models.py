from django.db import models
from django.utils.text import slugify

from dj_kaos_utils.models import HasAutoFields, MoneyField, LowerCaseCharField, BulkUpdateCreateQuerySet, \
    RankedQuerySetMixin, PageableQuerySet


class Category(HasAutoFields, models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def set_auto_fields(self):
        if not self.slug and self.name:
            self.slug = slugify(self.name)


class ProductQuerySet(PageableQuerySet, RankedQuerySetMixin, BulkUpdateCreateQuerySet):
    pass


class Product(models.Model):
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,
                                 related_name='products')
    name = models.CharField(max_length=255)
    price = MoneyField()

    code_id = LowerCaseCharField(max_length=255)

    objects = ProductQuerySet.as_manager()
