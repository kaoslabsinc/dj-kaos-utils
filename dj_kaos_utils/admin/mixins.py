from django.contrib.admin.options import BaseModelAdmin
from django.shortcuts import get_object_or_404
from django_object_actions import BaseDjangoObjectActions


class EditReadonlyAdminMixin(BaseModelAdmin):
    """
    Fields defined in :attr:`edit_readonly_fields` are editable upon creation, but after that they become readonly
    Set :attr:`allow_superusers` to True to allow superusers to edit such fields even in an edit form.

    Example:
        >>> class MyModelAdmin(EditReadonlyAdminMixin, admin.ModelAdmin):
        >>>     edit_readonly_fields = ('slug',)
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

    Example:
        >>> class MyModelAdmin(PrepopulateSlugAdminMixin, admin.ModelAdmin):
        >>>     slug_field = 'slug'
        >>>     slug_source = 'name'
    """
    slug_field = 'slug'
    slug_source = None

    def get_prepopulated_fields(self, request, obj=None):
        assert self.slug_source
        prepopulated_fields = super().get_prepopulated_fields(request, obj)
        if obj:  # editing an existing object
            return prepopulated_fields
        return {**prepopulated_fields, self.slug_field: (self.slug_source,)}


class DjangoObjectActionsPermissionsMixin(BaseDjangoObjectActions):
    """
    Built on DjangoObjectActions Admin, it checks if the user has change permissions on the object in order to show the
    change actions
    """

    def get_change_actions(self, request, object_id, form_url):
        obj = get_object_or_404(self.model, pk=object_id)
        self.__obj = obj
        if not self.has_change_permission(request, obj):
            return ()
        else:
            return super(DjangoObjectActionsPermissionsMixin, self).get_change_actions(request, object_id, form_url)

    def _get_change_action_object(self):
        return self.__obj


class AreYouSureActionsAdminMixin(BaseDjangoObjectActions):
    """
    Add a confirmation prompt to the certain object actions defined in `are_you_sure_actions`.

    Example:
        >>> class MyModelAdmin(AreYouSureActionsAdminMixin, admin.ModelAdmin):
        >>>     are_you_sure_actions = ('archive',)
    """
    are_you_sure_actions = ()
    are_you_sure_prompt_f = "Are you sure you want to {label} this object?"

    def __init__(self, *args, **kwargs):
        super(AreYouSureActionsAdminMixin, self).__init__(*args, **kwargs)
        for action in self.are_you_sure_actions:
            tool = getattr(self, action)
            label = getattr(tool, 'label', action).lower()
            are_you_sure_prompt = self.are_you_sure_prompt_f.format(tool=tool, label=label)
            tool.__dict__.setdefault('attrs', {})
            tool.__dict__['attrs'].setdefault('onclick', f"""return confirm("{are_you_sure_prompt}");""")


class ExcludeFromNonSuperusersMixin(BaseModelAdmin):
    """
    Admin mixin to make some fields hidden to non-superusers. Define such fields using `.exclude_from_non_superusers`,
    or dynamically by overriding `.get_exclude_from_non_superusers()`.

    Example:
        >>> class MyModelAdmin(ExcludeFromNonSuperusersMixin, admin.ModelAdmin):
        >>>     exclude_from_non_superusers = ('is_superuser',)
    """
    exclude_from_non_superusers = ()

    def get_exclude_from_non_superusers(self, request, obj=None):
        return self.exclude_from_non_superusers

    def get_exclude(self, request, obj=None):
        exclude = super(ExcludeFromNonSuperusersMixin, self).get_exclude(request, obj) or ()
        if request.user.is_superuser:
            return exclude
        return (
            *exclude,
            *self.get_exclude_from_non_superusers(request, obj),
        )


class ExcludeFromFieldsetsMixin(BaseModelAdmin):
    """
    Admin mixin to make sure fields that are in `exclude` are removed from the `fieldsets` definition.
    By default, without this mixin, if a field defined in `fieldsets` is in `exclude`, Django throws an
    error complaining about a missing value for the field.

    Example:
        >>> class MyModelAdmin(ExcludeFromFieldsetsMixin, admin.ModelAdmin):
        >>>     pass
    """

    def get_fieldsets(self, request, obj=None):
        exclude = self.get_exclude(request, obj)
        fieldsets = super().get_fieldsets(request, obj) or ()
        return [
            (fieldset_name,
             {
                 **fieldset_dict,
                 'fields': [field for field in fieldset_dict['fields'] if field not in exclude]
             })
            for fieldset_name, fieldset_dict in fieldsets
        ]


__all__ = (
    'EditReadonlyAdminMixin',
    'PrepopulateSlugAdminMixin',
    'DjangoObjectActionsPermissionsMixin',
    'AreYouSureActionsAdminMixin',
    'ExcludeFromNonSuperusersMixin',
    'ExcludeFromFieldsetsMixin',
)
