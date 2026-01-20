from dataclasses import dataclass

from srс.domain.value_objects.no_sales_item import NoSalesItem


@dataclass(frozen=True, slots=True)
class NoSalesReport:
    items: list[NoSalesItem]
