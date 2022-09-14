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
