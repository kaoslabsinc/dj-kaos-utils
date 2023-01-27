from __future__ import annotations

import datetime

from dateutil import parser
from django.utils.timezone import is_aware, make_aware


def parse_and_make_tz_aware(s: str | None) -> datetime.datetime | None:
    """
    Parse the string s into a datetime object and make it timezone aware if it is not so already.

    :param s: String to be parsed into a timezone
    :return: Timezone aware datetime instance
    """
    if s is None:
        return

    dt = parser.parse(s)
    if not is_aware(dt):
        dt = make_aware(dt)
    return dt


__all__ = [
    'parse_and_make_tz_aware',
]
