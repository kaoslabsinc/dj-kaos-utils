import datetime
from zoneinfo import ZoneInfo

from django.conf import settings

from dj_kaos_utils.datetime import DT


class TestDatetimeWrapper:
    def test_timezone(self):
        wrapped_dt = DT(datetime.datetime(2022, 1, 1, 12, 30, 0))
        assert wrapped_dt.tz == ZoneInfo(settings.TIME_ZONE)
