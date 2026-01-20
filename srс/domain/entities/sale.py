from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Sale:
    vending_machine_id: int
    amount: float
    timestamp: datetime
