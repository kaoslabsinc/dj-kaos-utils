from typing import Sequence


def get_lookup_values(seq_of_dicts: Sequence[dict], lookup_field):
    return tuple(d.get(lookup_field) for d in seq_of_dicts if d.get(lookup_field))


__all__ = (
    'get_lookup_values',
)
