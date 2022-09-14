from django.db import models
from django.db.models import Window, F
from django.db.models.functions import Rank


class RankedQuerySetMixin(models.QuerySet):
    """
    Mixin that adds an annotate_rank method to the QuerySet classes that inherit it. Used to annotate the rank of each
    row based on a field
    """

    def annotate_rank(self, field, asc=False):
        """
        Annotate the rank of each row based on the values in field.
        :param field: Rank entries based on values in field
        :param asc: Whether to rank the entries from lowest to highest. By default, rank from highest to lowest.
        :return:
        """
        order_by = F(field).asc() if asc else F(field).desc()
        return self.annotate(rank=Window(expression=Rank(), order_by=order_by))


__all__ = [
    'RankedQuerySetMixin',
]
