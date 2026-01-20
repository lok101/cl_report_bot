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

    async def create_report(
            self,
            vending_machines: Iterable[VendingMachine],
            interval_hours: int,
            last_sale_days: int,
    ) -> NoSalesReport:
        now_moscow: datetime = self._get_moscow_now_naive()
        interval_from: datetime = now_moscow - timedelta(hours=interval_hours)
        last_sale_from: datetime = now_moscow - timedelta(days=last_sale_days)

        interval_sales: list[Sale] = await self._sales_repository.get_sales(
            from_date=interval_from,
            to_date=now_moscow,
            vending_machine_id=None,
        )
        last_sales: list[Sale] = await self._sales_repository.get_sales(
            from_date=last_sale_from,
            to_date=now_moscow,
            vending_machine_id=None,
        )

        interval_sales_by_vm: dict[int, list[Sale]] = self._group_sales_by_vm(interval_sales)
        last_sale_by_vm: dict[int, datetime] = self._get_last_sale_by_vm(last_sales)

        items: list[NoSalesItem] = []
        vending_machine: VendingMachine
        for vending_machine in vending_machines:
            if interval_sales_by_vm.get(vending_machine.kit_id):
                continue

            last_sale_timestamp: datetime | None = last_sale_by_vm.get(vending_machine.kit_id)
            item: NoSalesItem = NoSalesItem(
                vending_machine=vending_machine,
                last_sale_timestamp=last_sale_timestamp,
            )
            items.append(item)

        report: NoSalesReport = NoSalesReport(items=items)
        return report

    async def create_report_for_days(
            self,
            vending_machines: Iterable[VendingMachine],
            days: list[date],
            last_sale_days: int,
    ) -> NoSalesReport:
        if not days:
            return NoSalesReport(items=[])

        now_moscow: datetime = self._get_moscow_now_naive()
        last_sale_from: datetime = now_moscow - timedelta(days=last_sale_days)
        sales: list[Sale] = await self._sales_repository.get_sales(
            from_date=last_sale_from,
            to_date=now_moscow,
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
    def _get_moscow_now_naive() -> datetime:
        now_moscow: datetime = datetime.now(ZoneInfo("Europe/Moscow"))
        return now_moscow.replace(tzinfo=None)

    @staticmethod
    def _normalize_timestamp_to_moscow_naive(timestamp: datetime) -> datetime:
        if timestamp.tzinfo is None:
            return timestamp
        moscow_timestamp: datetime = timestamp.astimezone(ZoneInfo("Europe/Moscow"))
        return moscow_timestamp.replace(tzinfo=None)

    @staticmethod
    def _group_sales_by_vm(sales: list[Sale]) -> dict[int, list[Sale]]:
        grouped: dict[int, list[Sale]] = {}
        sale: Sale
        for sale in sales:
            grouped.setdefault(sale.vending_machine_id, []).append(sale)
        return grouped

    def _group_sales_by_vm_and_day(self, sales: list[Sale]) -> dict[int, set[date]]:
        grouped: dict[int, set[date]] = {}
        sale: Sale
        for sale in sales:
            normalized_timestamp: datetime = self._normalize_timestamp_to_moscow_naive(sale.timestamp)
            sale_day: date = normalized_timestamp.date()
            grouped.setdefault(sale.vending_machine_id, set()).add(sale_day)
        return grouped

    def _get_last_sale_by_vm(self, sales: list[Sale]) -> dict[int, datetime]:
        last_sales: dict[int, datetime] = {}
        sale: Sale
        for sale in sales:
            normalized_timestamp: datetime = self._normalize_timestamp_to_moscow_naive(sale.timestamp)
            current: datetime | None = last_sales.get(sale.vending_machine_id)
            if current is None or normalized_timestamp > current:
                last_sales[sale.vending_machine_id] = normalized_timestamp
        return last_sales

    @staticmethod
    def _has_any_day(vm_days: set[date], required_days: set[date]) -> bool:
        return not vm_days.isdisjoint(required_days)
