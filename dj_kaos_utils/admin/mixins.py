from django.contrib.admin.options import BaseModelAdmin


class EditReadonlyAdminMixin(BaseModelAdmin):
    """
    Fields defined in :attr:`edit_readonly_fields` are editable upon creation, but after that they become readonly
    """
    edit_readonly_fields = ()

    def get_edit_readonly_fields(self, request, obj=None):
        return self.edit_readonly_fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:  # editing an existing object
            return self.get_edit_readonly_fields(request, obj) + readonly_fields
        return readonly_fields


__all__ = [
    'EditReadonlyAdminMixin',
]
