from django.contrib import admin


class BooleanAdminFilter(admin.SimpleListFilter):
    """
    An admin filter that works like an on-off switch; two options: on, off (all)

    Example:
        >>> class ByAvailableFilter(BooleanAdminFilter):
        >>>     title = "availability"
        >>>     parameter_name = 'is_available'
        >>>
        >>>     def filter(self, request, queryset):
        >>>         return queryset.filter(is_available=True)
    """

    def lookups(self, request, model_admin):
        return (
            ('on', "On"),
        )

    def queryset(self, request, queryset):
        if self.value() == 'on':
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


class YesNoAdminFilter(admin.SimpleListFilter):
    """
    Admin filter with three options: yes, no and all.

    Example:
        >>> class IsArchivedFilter(BooleanAdminFilter):
        >>>     title = "archived"
        >>>     parameter_name = 'is_archived'
        >>>
        >>>     def filter_yes(self, request, queryset):
        >>>         return queryset.filter(is_archived=True)
        >>>
        >>>     def filter_no(self, request, queryset):
        >>>         return queryset.filter(is_archived=False)
    """

    def lookups(self, request, model_admin):
        return (
            ('yes', "Yes"),
            ('no', "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return self.filter_yes(request, queryset)
        if self.value() == 'no':
            return self.filter_no(request, queryset)
        return queryset

    def filter_yes(self, request, queryset):
        """
        Override this method to filter the queryset when the filter value is set to yes

        :param request: the request from the admin site
        :param queryset: the queryset passed by the admin
        :return: filtered queryset
        """
        raise NotImplementedError

    def filter_no(self, request, queryset):
        """
        Override this method to filter the queryset when the filter value is set to no

        :param request: the request from the admin site
        :param queryset: the queryset passed by the admin
        :return: filtered queryset
        """
        raise NotImplementedError


__all__ = (
    'BooleanAdminFilter',
    'QuerysetChoiceFilter',
    'YesNoAdminFilter',
)
