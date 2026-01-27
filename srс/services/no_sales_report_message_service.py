from datetime import datetime

from srс.domain.entities.no_sales_report import NoSalesReport
from srс.domain.value_objects.no_sales_item import NoSalesItem


class NoSalesReportMessageService:
    def __init__(self, last_sale_days: int):
        self._last_sale_days = last_sale_days

    def create_message(self, report: NoSalesReport) -> str:
        if not report.items:
            return ""

        parts: list[str] = ["Аппараты без продаж:"]
        item: NoSalesItem
        for item in report.items:
            line: str = self._format_item(item)
            parts.append(line)

        message: str = "\n\n".join(parts)
        return message

    def _format_item(self, item: NoSalesItem) -> str:
        name: str = item.vending_machine.name
        last_sale_text: str = self._format_last_sale(item.last_sale_timestamp)
        return f"{name}\n{last_sale_text}"

    def _format_last_sale(self, timestamp: datetime | None) -> str:
        if timestamp is None:
            return f"Последняя продажа: более {self._last_sale_days} дней назад"

        formatted: str = timestamp.strftime("%d.%m.%Y %H:%M")
        return f"Последняя продажа: {formatted}"
