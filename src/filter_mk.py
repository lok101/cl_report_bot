from src.entities import MK

stop_words = ['УГМК', 'Офис']


def filter_mk(mks: list[MK]) -> list[MK]:
    return [mk for mk in mks if mk.is_valid_mk(stop_words)]
