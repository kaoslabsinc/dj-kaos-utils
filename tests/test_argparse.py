import argparse
import datetime
import zoneinfo

from dj_kaos_utils.argparse import ArgParseTypes


def test_ArgParseTypes_tz_aware_datetime():
    parser = argparse.ArgumentParser()
    parser.add_argument('tz_aware_datetime', type=ArgParseTypes.tz_aware_datetime)

    args = parser.parse_args(["Aug 25th 2022"])
    # or vars(args)['tz_aware_datetime']
    assert args.tz_aware_datetime == datetime.datetime(2022, 8, 25, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
