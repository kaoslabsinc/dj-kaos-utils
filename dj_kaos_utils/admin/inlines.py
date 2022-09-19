from django.contrib.admin.options import InlineModelAdmin


class NoViewInlineMixin(InlineModelAdmin):
    """
    Admin inline mixin that doesn't show any objects (but can show the form to add).
    """

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.none()  # no existing records will appear


class NoAddInlineMixin(InlineModelAdmin):
    """
    Admin inline mixin that doesn't show the form to add new objects
    """

    def has_add_permission(self, request, obj):
        return False


class NoChangeInlineMixin(InlineModelAdmin):
    """
    Admin inline mixin that makes the existing objects not be editable.
    """

    def has_change_permission(self, request, obj=None):
        return False


__all__ = [
    'NoViewInlineMixin',
    'NoAddInlineMixin',
    'NoChangeInlineMixin',
]
