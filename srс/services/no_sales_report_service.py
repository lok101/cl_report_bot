from datetime import date, datetime, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo

from srс.domain.entities.no_sales_report import NoSalesReport
from srс.domain.entities.sale import Sale
from srс.domain.entities.vending_machine import VendingMachine
from srс.domain.ports.sales_repository import SalesRepository
from srс.domain.value_objects.no_sales_item import NoSalesItem


class NoSalesReportService:
    def __init__(self, sales_repository: SalesRepository):
        self._sales_repository = sales_repository

    async def create_report_for_days(
            self,
            vending_machines: Iterable[VendingMachine],
            days: list[date],
            last_sale_days: int,
    ) -> NoSalesReport:
        if not days:
            return NoSalesReport(items=[])

        now: datetime = datetime.now(tz=ZoneInfo("Asia/Yekaterinburg"))
        last_sale_from: datetime = now - timedelta(days=last_sale_days)
        sales: list[Sale] = await self._sales_repository.get_sales(
            from_date=last_sale_from,
            to_date=now,
            vending_machine_id=None,
        )

        sales_by_vm_and_day: dict[int, set[date]] = self._group_sales_by_vm_and_day(sales)
        last_sale_by_vm: dict[int, datetime] = self._get_last_sale_by_vm(sales)

        day_set: set[date] = set(days)
        items: list[NoSalesItem] = []
        vending_machine: VendingMachine
        for vending_machine in vending_machines:
            vm_days: set[date] = sales_by_vm_and_day.get(vending_machine.kit_id, set())
            if self._has_any_day(vm_days, day_set):
                continue

            last_sale_timestamp: datetime | None = last_sale_by_vm.get(vending_machine.kit_id)
            item: NoSalesItem = NoSalesItem(
                vending_machine=vending_machine,
                last_sale_timestamp=last_sale_timestamp,
            )
            items.append(item)

        report: NoSalesReport = NoSalesReport(items=items)
        return report

    @staticmethod
    def _group_sales_by_vm_and_day(sales: list[Sale]) -> dict[int, set[date]]:
        grouped: dict[int, set[date]] = {}
        sale: Sale
        for sale in sales:
            grouped.setdefault(sale.vending_machine_id, set()).add(sale.timestamp.date())
        return grouped

    @staticmethod
    def _get_last_sale_by_vm(sales: list[Sale]) -> dict[int, datetime]:
        last_sales: dict[int, datetime] = {}
        sale: Sale
        for sale in sales:
            current: datetime | None = last_sales.get(sale.vending_machine_id)
            if current is None or sale.timestamp > current:
                last_sales[sale.vending_machine_id] = sale.timestamp
        return last_sales

    @staticmethod
    def _has_any_day(vm_days: set[date], required_days: set[date]) -> bool:
        return not vm_days.isdisjoint(required_days)
