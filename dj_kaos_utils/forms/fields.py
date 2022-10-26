from django import forms
from django.utils.html import format_html_join, format_html


class ListTextWidget(forms.TextInput):
    def __init__(self, datalist, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = datalist
        self.attrs.update({'list': f'list__{name}'})

    def render(self, name, value, attrs=None, renderer=None):
        datalist_html = format_html('<datalist id="list__{name}">{options}</datalist>',
                                    name=self._name,
                                    options=format_html_join('', '<option value="{}">', self._list))

        return super(ListTextWidget, self).render(name, value, attrs=attrs) + datalist_html


__all__ = (
    'ListTextWidget',
)
