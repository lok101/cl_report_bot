from dataclasses import dataclass

from srс.domain.entities.vending_machine import VendingMachine


@dataclass(frozen=True, slots=True)
class SalesAnalyzeItem:
    vending_machine: VendingMachine
    average_daily_sales: float
    yesterday_sales: float
    deviation_ratio: float
