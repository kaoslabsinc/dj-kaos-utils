from __future__ import annotations

import logging
from typing import Callable, TypeVar, Sequence

from django.core.paginator import Paginator
from django.db import models, transaction
from django.db.models import Window, F, Min, Max, Q
from django.db.models.functions import Rank

logger = logging.getLogger()

QS = TypeVar('QS', bound=models.QuerySet)
M = TypeVar('M', bound=models.Model)


class RankedQuerySetMixin(models.QuerySet):
    """
    Mixin that adds an `annotate_rank` method to the QuerySet classes that inherit it. Used to annotate the rank of each
    row based on a field
    """

    def annotate_rank(self: QS, field: str, rank_annotation_name: str = 'rank', asc: bool = False) -> QS:
        """
        Annotate the rank of each row based on the values in the designated field.

        :param field: Rank entries based on values in this field
        :param rank_annotation_name: The name of the annotation to store the rank. By default, ``rank``.
        :param asc: Whether to rank the entries from lowest to highest. By default, rank from highest to lowest.
        :return: Queryset with rank annotated by `field`
        """
        order_by = F(field).asc() if asc else F(field).desc()
        return self.annotate(**{
            rank_annotation_name: Window(expression=Rank(), order_by=order_by)
        })


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
            memory usage but guarantees that each page returned corresponds to the original objects in the queryset
            before any write/edit operations.
        :return: iterator with each object being a page of the queryset with maximum size of limit. Guaranteed each page
            except the last page to have a size of limit.
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


class BulkUpdateCreateQuerySet(models.QuerySet):
    def bulk_update_or_create(
        self: QS,
        objs: Sequence[M],
        lookup_fields: str | Sequence[str],
        update_fields: Sequence[str],
    ) -> QS:
        """
        Creates or updates in bulk a list of objects

        :param objs: List of model instances
        :param lookup_fields: Name of field(s) that uniquely identify the objects. You can pass a string to look up
            using one field, or an itertable to look up using multiple fields
        :param update_fields: List of fields to update. If value is falsy such as empty list, bulk_update won't run,
            which is useful for batch creating missing objects.
        :return: queryset containing all the objects, created and updated.
        """

        def get_obj_keys_tuple(obj: M, lookup_fields: Sequence[str]):
            return tuple(getattr(obj, field) for field in lookup_fields)

        def get_filter_q(objs: Sequence[M], lookup_fields: Sequence[str]):
            if len(lookup_fields) == 1:
                lookup_field = lookup_fields[0]
                return Q(**{lookup_field + '__in': [getattr(obj, lookup_field) for obj in objs]})

            q = Q()
            for obj in objs:
                q |= Q(**{
                    field: getattr(obj, field)
                    for field in lookup_fields
                })
            return q

        if isinstance(lookup_fields, str):
            lookup_fields = (lookup_fields,)

        existing = {
            get_obj_keys_tuple(obj, lookup_fields): obj
            for obj in self.filter(get_filter_q(objs, lookup_fields))
        }
        bulk_create = []
        bulk_update = []
        for obj in objs:
            lookup_tuple = get_obj_keys_tuple(obj, lookup_fields)
            if lookup_tuple in existing:
                existing_obj = existing[lookup_tuple]
                for field in update_fields:
                    setattr(existing_obj, field, getattr(obj, field))
                bulk_update.append(existing_obj)
            else:
                bulk_create.append(obj)
        self.bulk_create(bulk_create)
        if update_fields:
            self.bulk_update(bulk_update, update_fields)
        # Rerunning the queryset to make sure all instances returned have ids. The values in created are pointers to
        # instances before they have their id
        return self.filter(get_filter_q(objs, lookup_fields))


__all__ = [
    'RankedQuerySetMixin',
    'PageableQuerySet',
    'BulkUpdateCreateQuerySet',
]
