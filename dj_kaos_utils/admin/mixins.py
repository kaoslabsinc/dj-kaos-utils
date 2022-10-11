from django.contrib.admin.options import BaseModelAdmin


class EditReadonlyAdminMixin(BaseModelAdmin):
    """
    Fields defined in :attr:`edit_readonly_fields` are editable upon creation, but after that they become readonly
    Set :attr:`allow_superusers` to True to allow superusers to edit such fields even in an edit form.
    """
    allow_superusers = False
    edit_readonly_fields = ()

    def get_edit_readonly_fields(self, request, obj=None):
        return self.edit_readonly_fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not obj:  # is in add form not edit
            return readonly_fields
        if self.allow_superusers and request.user.is_superuser:
            return readonly_fields
        return readonly_fields + self.get_edit_readonly_fields(request, obj)


__all__ = [
    'EditReadonlyAdminMixin',
]
