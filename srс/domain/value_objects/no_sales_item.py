from dataclasses import dataclass
from datetime import datetime

from srс.domain.entities.vending_machine import VendingMachine


@dataclass(frozen=True, slots=True)
class NoSalesItem:
    vending_machine: VendingMachine
    last_sale_timestamp: datetime | None
