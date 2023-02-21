from __future__ import annotations

import datetime as dt
from typing import Optional
from zoneinfo import ZoneInfo

from django.conf import settings
from py_kaos_utils.datetime import DatetimeWrapper as PyDTWrapper


class DatetimeWrapper(PyDTWrapper):
    def __init__(self,
                 raw_dt: str | dt.datetime,
                 raw_tz: Optional[str | ZoneInfo] = settings.TIME_ZONE):
        super().__init__(raw_dt, raw_tz)


DT = DatetimeWrapper

__all__ = (
    'DatetimeWrapper',
    'DT',
)
