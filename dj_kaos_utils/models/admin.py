from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.utils.html import format_html, format_html_join

from .mixins import HasWarnings


class HasWarningsAdmin(BaseModelAdmin):
    readonly_fields = ('warnings_display',)

    fieldsets = (
        ("Warnings", {'fields': ('warnings_display',)}),
    )

    @admin.display(description="warnings")
    def warnings_display(self, obj: HasWarnings):
        return obj and format_html(
            "<ol>{}</ol>",
            format_html_join('\n', '<li>{}</li>', zip(
                warning if isinstance(warning, str) else f"{warning[0]}: {warning[1]}"
                for warning in obj.get_warnings()
            ))
        )


__all__ = [
    'HasWarningsAdmin',
]
