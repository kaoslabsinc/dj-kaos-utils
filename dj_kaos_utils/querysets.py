import logging
from typing import Callable, TypeVar

from django.core.paginator import Paginator
from django.db import models, transaction
from django.db.models import Window, F, Min, Max
from django.db.models.functions import Rank

logger = logging.getLogger()

QS = TypeVar('QS', bound=models.QuerySet)


class RankedQuerySetMixin(models.QuerySet):
    """
    Mixin that adds an annotate_rank method to the QuerySet classes that inherit it. Used to annotate the rank of each
    row based on a field
    """

    def annotate_rank(self: QS, field, asc=False) -> QS:
        """
        Annotate the rank of each row based on the values in field.
        :param field: Rank entries based on values in field
        :param asc: Whether to rank the entries from lowest to highest. By default, rank from highest to lowest.
        :return:
        """
        order_by = F(field).asc() if asc else F(field).desc()
        return self.annotate(rank=Window(expression=Rank(), order_by=order_by))


class PageableQuerySet(models.QuerySet):
    def paginate_minmax(self: QS, limit: int) -> QS:
        d = self.values('id').aggregate(min=Min('id'), max=Max('id'))
        min_id, max_id = d['min'], d['max']
        if min_id is None:
            return self
        for i in range(min_id, max_id + 1, limit):
            yield self.filter(id__gte=i, id__lt=i + limit)

    def paginate_pks(self: QS, limit: int, simple: bool = True, mutating: bool = False) -> QS:
        qs = self.model.objects.all() if simple else self
        pk_values = self.values_list('pk', flat=True)
        if mutating:
            pk_values = tuple(pk_values)

        for page in Paginator(pk_values, limit):
            yield qs.filter(pk__in=page.object_list)

    def paginate_pks_mutating(self: QS, limit, simple: bool = True) -> QS:
        return self.paginate_pks(limit, simple=simple, mutating=True)

    def paginate(self: QS, limit: int) -> QS:
        return self.paginate_minmax(limit)

    def paginated_update(self, limit: int, page_op: Callable[[models.QuerySet], int]) -> int:
        """
        Run operation page_op on the queryset page by page
        :param limit: Page size
        :param page_op: Operation to run on each page. It should at the end update the database and return the number of
        rows updated
        :return: the total number of rows updated.
        """
        opts = self.model._meta
        verbose_name_plural = opts.verbose_name_plural
        total_count = self.count()

        count_all = 0
        for i, page in enumerate(self.paginate(limit)):
            count = page.count()
            logger.debug(f"({i + 1}) Running for {count} {verbose_name_plural}")
            with transaction.atomic():
                count = page_op(page)
            count_all += count
            logger.info(f"({i + 1}) Finished for {count} {verbose_name_plural} ({count_all}/{total_count} in total)")
        return count_all


__all__ = [
    'RankedQuerySetMixin',
    'PageableQuerySet',
]
