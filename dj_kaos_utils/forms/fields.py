from django import forms
from django.utils.html import format_html_join, format_html


class ListTextWidget(forms.TextInput):
    """
    A Django form widget that renders a text input with a datalist populated with options from a given list.

    Example:
        >>> class MyForm(forms.Form):
        >>>     my_field = forms.CharField(widget=ListTextWidget(datalist=['option1', 'option2', 'option3']))
    """

    def __init__(self, datalist, name, *args, **kwargs):
        """
        Initialize the widget with the list of options and the name of the datalist.

        :param datalist: list of options for the datalist
        :type datalist: list
        :param name: name of the datalist
        :type name: str
        """

        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = datalist
        self.attrs.update({'list': f'list__{name}'})

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the text input and datalist.
        """

        datalist_html = format_html('<datalist id="list__{name}">{options}</datalist>',
                                    name=self._name,
                                    options=format_html_join('', '<option value="{}">', self._list))

        return super(ListTextWidget, self).render(name, value, attrs=attrs) + datalist_html


__all__ = (
    'ListTextWidget',
)
