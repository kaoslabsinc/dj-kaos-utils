from django.contrib import admin

from dj_kaos_utils.admin import EditReadonlyAdminMixin
from .models import Category


@admin.register(Category)
class CategoryAdmin(EditReadonlyAdminMixin, admin.ModelAdmin):
    edit_readonly_fields = ('slug',)
