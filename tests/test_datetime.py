import datetime
import zoneinfo

from dj_kaos_utils.datetime import parse_and_make_tz_aware


def test_parse_and_make_tz_aware_None():
    assert parse_and_make_tz_aware(None) is None


def test_parse_and_make_tz_aware_no_tz_str():
    intended_dt = datetime.datetime(2022, 8, 5, 12, 34, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
    assert parse_and_make_tz_aware("Aug 5th 2022 12:34pm") == intended_dt


def test_parse_and_make_tz_aware_no_tz_str_non_utc_tz(settings):
    settings.TIME_ZONE = 'America/Vancouver'

    intended_dt = datetime.datetime(2022, 8, 5, 12, 34, tzinfo=zoneinfo.ZoneInfo(key='America/Vancouver'))
    assert parse_and_make_tz_aware("Aug 5th 2022 12:34pm") == intended_dt


def test_parse_and_make_tz_aware():
    intended_dt = datetime.datetime(2022, 8, 5, 20, 34, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
    assert parse_and_make_tz_aware("Aug 5th 2022 12:34pm -08:00").timestamp() == intended_dt.timestamp()
