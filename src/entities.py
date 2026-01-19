from dataclasses import dataclass
from datetime import datetime, timedelta

from src.enums import Company, MKStatuses

MINUTES_TO_CONNECTION_ERROR_STATUS = 15


def timestamp() -> datetime:
    return datetime.now() - timedelta(hours=2)


@dataclass
class Sale:
    name: str
    timestamp: datetime


@dataclass(frozen=True)
class MK:
    id: int
    name: str
    statuses: set[int]
    last_sale_timestamp: datetime
    last_ping_timestamp: datetime
    company: Company

    def has_sale_in_selected_time_range(self, hours: int) -> bool:
        if self.last_sale_timestamp is None:
            return False
        return timestamp() - timedelta(hours=hours) < self.last_sale_timestamp

    def has_connection_error(self) -> bool:
        return timestamp() - timedelta(minutes=MINUTES_TO_CONNECTION_ERROR_STATUS) > self.last_ping_timestamp

    def has_status(self, status: MKStatuses) -> bool:
        return status in self.statuses

    def is_snack(self) -> bool:
        return self.company == Company.SNACK
