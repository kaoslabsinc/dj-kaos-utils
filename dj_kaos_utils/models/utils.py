from django.core.exceptions import ObjectDoesNotExist
from django.db import models


def check_fk_exists(instance: models.Model, fk_field_name: str):
    try:
        return getattr(instance, fk_field_name)
    except ObjectDoesNotExist:
        return None
