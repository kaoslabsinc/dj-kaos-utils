from django.utils.timezone import make_aware
from py_kaos_utils.argparse import ArgParseTypes as PyArgParseTypes


class ArgParseTypes(PyArgParseTypes):
    """
    Contains static methods that can be passed to argparse.ArgumentParser().add_argument(type=)
    Adds on top of py_kaos_utils.argparse.ArgParseTypes types specific to Django.
    """

    @staticmethod
    def tz_aware_datetime(s):
        return make_aware(PyArgParseTypes.datetime(s))


__all__ = [
    'ArgParseTypes',
]
