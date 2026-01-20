from dataclasses import dataclass

from srс.domain.value_objects.sales_analyze_item import SalesAnalyzeItem


@dataclass(frozen=True, slots=True)
class SalesAnalyzeReport:
    items: list[SalesAnalyzeItem]
