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


__all__ = [
    'HasAutoFields',
]
