from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Sale:
    name: str
    timestamp: datetime


@dataclass
class MK:
    id: int
    name: str
    sales: list[Sale]

    def is_valid_mk(self, stop_words: list[str]) -> bool:
        for word in stop_words:
            if word in self.name:
                return False
        return True

    def has_sales_in_period(self, period: datetime) -> bool:
        if self.last_sale_timestamp:
            return self.last_sale_timestamp < period

        return False

    @property
    def last_sale_timestamp(self) -> Optional[datetime]:
        if self.sales:
            return self.sales[0].timestamp

    def print_report(self):
        print(f'{self.name.ljust(50)} | {self.last_sale_timestamp.strftime("%d.%m.%Y %H:%M")}')
