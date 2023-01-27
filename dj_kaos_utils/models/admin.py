from __future__ import annotations

from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.utils.html import format_html, format_html_join

from .mixins import HasWarnings


class HasWarningsAdmin(BaseModelAdmin):
    """
    A Django ModelAdmin class to display warnings associated with an object of `HasWarnings` class.
    """

    readonly_fields = ('warnings_display',)
    fieldsets = (
        ("Warnings", {'fields': ('warnings_display',)}),
    )

    @admin.display(description="warnings")
    def warnings_display(self, obj: HasWarnings):
        """
        Return the processed warnings of the object as an ordered list in HTML format.

        :param obj: an object of `HasWarnings` class
        :type obj: HasWarnings
        :return: warnings as an ordered list in HTML format
        :rtype: str
        """
        processed_warnings = (
            warning if isinstance(warning, str) else format_html("<code>{}</code>: {}", *warning)
            for warning in obj.get_warnings()
        )
        return obj and format_html(
            "<ol>{}</ol>",
            format_html_join('\n', '<li>{}</li>', zip(processed_warnings))
        )


__all__ = [
    'HasWarningsAdmin',
]
