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


class PrepopulateSlugAdminMixin(BaseModelAdmin):
    """
    Makes the inheriting admin prepopulate the slug field from the field denoted by `slug_source`.
    Assumes by default, the slug field is ``model.slug``. If the field name is different, you can set it with
    `slug_field`.
    """
    slug_field = 'slug'
    slug_source = None

    def get_prepopulated_fields(self, request, obj=None):
        assert self.slug_source
        prepopulated_fields = super().get_prepopulated_fields(request, obj)
        if obj:  # editing an existing object
            return prepopulated_fields
        return {**prepopulated_fields, self.slug_field: (self.slug_source,)}


__all__ = (
    'EditReadonlyAdminMixin',
    'PrepopulateSlugAdminMixin',
)
