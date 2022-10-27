from django.contrib import admin


class BooleanAdminFilter(admin.SimpleListFilter):
    """
    An admin filter that works like an on-off switch.
    """

    def lookups(self, request, model_admin):
        return (
            (True, "True"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return self.filter(request, queryset)
        return queryset

    def filter(self, request, queryset):
        """
        Override this method to filter the queryset when the filter value is set to True

        :param request: the request from the admin site
        :param queryset: the queryset passed by the admin
        :return: filtered queryset
        """
        raise NotImplementedError


class QuerysetChoiceFilter(admin.SimpleListFilter):
    queryset_filters = ()

    def lookups(self, request, model_admin):
        lookups = []
        for filter_def in self.queryset_filters:
            if isinstance(filter_def, tuple):
                key, verbose_name = filter_def
            else:
                key, verbose_name = filter_def, filter_def.replace('_', ' ').capitalize()
            lookups.append((key, verbose_name))
        return lookups

    def queryset(self, request, queryset):
        value = self.value()
        if value in self.queryset_filters:
            return getattr(queryset, value)()
        return queryset


__all__ = (
    'BooleanAdminFilter',
    'QuerysetChoiceFilter',
)
