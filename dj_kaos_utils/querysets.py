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
    """
    Provide support for paginating django querysets. Useful for running expensive operations in batches.
    """

    def paginate_minmax(self: QS, limit: int, id_field='id') -> QS:
        """
        Paginate by slicing the queryset using an autoincrement field.
        Requires the model in this queryset to have an autoincrement field, like id.
        Each page is guaranteed to have a maximum count of limit, but it each individual page could have a lower count.
        Does not retain the original order of the queryset in any way.

        :param limit: Size of each page
        :param id_field: The field to use for paging
        :return: iterator with each object being a page of the queryset with maximum size of limit
        """
        d = self.values(id_field).aggregate(min=Min(id_field), max=Max(id_field))
        min_id, max_id = d['min'], d['max']
        if min_id is None:
            return self
        for i in range(min_id, max_id + 1, limit):
            yield self.filter(id__gte=i, id__lt=i + limit)

    def paginate_pks(self: QS, limit: int, simple: bool = True, mutating: bool = False) -> QS:
        """
        Paginate the queryset by identifying each object in the queryset by its primary key, and reloading them from the
        queryset, page by page, by looking up their pks. Guarantees each page except the last page to have a size of
        limit.

        :param limit: Size of each page
        :param simple: If True, any queryset filtering or annotations on the base queryset (self) will be cleared for
        simplicity and efficiency
        :param mutating: If the base queryset (self) mutates during each iteration over the pages, set to True, which
        will cache the PK values into memory instead of reading from the DB on each page. Setting to True increases
        memory usage but guarantees that each page returned corrosposnds to the original objects in the queryset before
        any write/edit operations.
        :return: iterator with each object being a page of the queryset with maximum size of limit.
        Guaranteed each page except the last page to have a size of limit.
        """
        qs = self.model.objects.all() if simple else self
        pk_values = self.values_list('pk', flat=True)
        if mutating:
            pk_values = tuple(pk_values)

        for page in Paginator(pk_values, limit):
            yield qs.filter(pk__in=page.object_list)

    def paginate_pks_mutating(self: QS, limit, simple: bool = True) -> QS:
        """
        A shortcut for self.paginate_pks(limit, simple=simple, mutating=True)
        """
        return self.paginate_pks(limit, simple=simple, mutating=True)

    def paginate(self: QS, limit: int) -> QS:
        """
        A shortcut to the favourite way of paginating for the queryset class.
        By default, set to paginate_minmax, which should give the best performance in most cases.
        Override this method to change the default strategy used by the inheritor queryset class.

        :param limit: Size of each page
        :return: iterator with each object being a page of the queryset with maximum size of limit
        """
        return self.paginate_minmax(limit)

    def paginated_update(self, limit: int, page_op: Callable[[models.QuerySet], int]) -> int:
        """
        Run operation page_op on the queryset page by page. Each operation on a page is an atomic transaction, and will
        be committed to the database upon success.
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
