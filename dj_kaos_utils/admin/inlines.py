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


class AddInlineMixin(NoViewInlineMixin):
    """
    Mixin for inline admin classes. Used to create an inline that is used only as the form interface for the inline
    model. Primarily used alongside :class:`ListInlineMixin` to create edit_readonly fields for an admin
    """


class ListInlineMixin(NoAddInlineMixin):
    """
    Mixin for inline admin classes. Used to create an inline that is used to view objects, or change them, but not add
    new ones. Primarily used alongside :class:`AddInlineMixin` to create edit_readonly fields for an admin
    """


class ReadOnlyInlineMixin(NoAddInlineMixin, NoChangeInlineMixin):
    """
    Mixin for inline admin classes to create a readonly inline admin.
    """


__all__ = (
    'NoViewInlineMixin',
    'NoAddInlineMixin',
    'NoChangeInlineMixin',
    'AddInlineMixin',
    'ListInlineMixin',
    'ReadOnlyInlineMixin',
)
