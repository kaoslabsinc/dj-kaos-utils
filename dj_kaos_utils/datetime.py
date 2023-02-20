from __future__ import annotations

from django.conf import settings
from py_kaos_utils.datetime import DatetimeWrapper as PyDTWrapper


class DatetimeWrapper(PyDTWrapper):
    def __init__(self, raw_datetime, timezone_str=settings.TIME_ZONE):
        super().__init__(raw_datetime, timezone_str)


DT = DatetimeWrapper

__all__ = (
    'DatetimeWrapper',
    'DT',
)
