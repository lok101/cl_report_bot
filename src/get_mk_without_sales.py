from datetime import datetime, timedelta

from src.entities import MK


def get_mk_without_sales(mks: list[MK], hours: int = 24) -> list[MK]:
    period = datetime.now() - timedelta(hours=hours)
    return [mk for mk in mks if mk.has_sales_in_period(period)]
