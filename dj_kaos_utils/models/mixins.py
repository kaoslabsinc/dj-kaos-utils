from __future__ import annotations

from py_kaos_utils.string import create_initials


class HasAutoFields:
    """
    Mixin for models that have fields that can be automatically set, for example from the value of other fields.
    """

    def set_auto_fields(self):
        """Override this method to set the fields that need to be automatically set"""

    def clean(self):
        self.set_auto_fields()
        super(HasAutoFields, self).clean()

    def save(self, *args, **kwargs):
        self.set_auto_fields()
        super(HasAutoFields, self).save(*args, **kwargs)


class HasInitials:
    """
    Add property `initials` to its inheritor classes. Take the value form the field defined by `take_initials_from` and
    return the initial letters of each word in it, capitalized.
    Interface using `instance.initials`.
    """
    take_initials_from = None

    @property
    def initials(self):
        """
        Take the value form the field defined by `take_initials_from` and return the initial letters of each word in it,
        capitalized.
        Example: John Smith => JS
        :return: Initial letters of each word in the value from the field `take_initials_from`, capitalized.
        """
        if self.take_initials_from is None:
            raise AttributeError(f"take_initials_from not defined on {self.__class__}")
        return create_initials(getattr(self, self.take_initials_from))


class HasWarnings:
    """
    Adds a method `get_warnings` useful to catch issues that aren't worthy of throwing a `ValidationError`

    Example:
        >>> class MyModel(models.Model):
        >>>     def get_warnings(self):
        >>>         warnings = super().get_warnings()
        >>>         if self.fulfills_condition():
        >>>             return [*warnings, "New warning"]
        >>>         return warnings
    """

    def get_warnings(self) -> list[str | tuple[str, str]]:
        """
        Override this method and append any warnings to the result of calling `super()`

        :return: A list of warnings. Each item in the list is either a tuple of (field_name, warning description) or
            just warning description.
        """
        return []


__all__ = [
    'HasAutoFields',
    'HasInitials',
    'HasWarnings',
]
