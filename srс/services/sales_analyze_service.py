from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import DefaultDict, Iterable
from zoneinfo import ZoneInfo

from srс.domain.entities.sale import Sale
from srс.domain.entities.sales_analyze_report import SalesAnalyzeReport
from srс.domain.entities.vending_machine import VendingMachine
from srс.domain.ports.sales_repository import SalesRepository
from srс.domain.value_objects.sales_analyze_item import SalesAnalyzeItem

_PROJECT_TZ = ZoneInfo("Asia/Yekaterinburg")


class SalesAnalyzeService:
    def __init__(self, sales_repository: SalesRepository, days_for_average: int, decline_threshold: float):
        self._sales_repository = sales_repository

        self._days_for_average = days_for_average
        self._decline_threshold = decline_threshold

    async def create_sales_analyze_report(self, vending_machines: Iterable[VendingMachine]) -> SalesAnalyzeReport:
        """Пропускает аппараты, на которых совсем не было продаж (падение на 100%)."""

        from_date: datetime
        to_date: datetime
        yesterday: date
        from_date, to_date, yesterday = self._get_date_range()

        sales: list[Sale] = await self._sales_repository.get_sales(
            from_date=from_date,
            to_date=to_date,
            vending_machine_id=None,
        )
        sales_by_vm: dict[int, list[Sale]] = self._group_sales_by_vm(sales)

        items: list[SalesAnalyzeItem] = []
        for vending_machine in vending_machines:
            vm_sales: list[Sale] = sales_by_vm.get(vending_machine.kit_id, [])
            day_totals: dict[date, float] = self._sum_sales_by_day(vm_sales, from_date, to_date)
            total_sum: float = sum(day_totals.values())
            average: float = total_sum / self._days_for_average
            yesterday_total: float = day_totals.get(yesterday, 0.0)

            if average <= 0.0:
                continue

            if yesterday_total <= 0:
                continue

            if yesterday_total >= average * self._decline_threshold:
                continue

            deviation_ratio: float = (average - yesterday_total) / average
            item: SalesAnalyzeItem = SalesAnalyzeItem(
                vending_machine=vending_machine,
                average_daily_sales=average,
                yesterday_sales=yesterday_total,
                deviation_ratio=deviation_ratio,
            )
            items.append(item)

        report: SalesAnalyzeReport = SalesAnalyzeReport(items=items)
        return report

    def _get_date_range(self) -> tuple[datetime, datetime, date]:
        today: date = datetime.now(_PROJECT_TZ).date()
        from_date: date = today - timedelta(days=self._days_for_average)
        from_datetime: datetime = datetime.combine(from_date, time.min).replace(tzinfo=_PROJECT_TZ)
        to_datetime: datetime = datetime.combine(today, time.max).replace(tzinfo=_PROJECT_TZ)
        yesterday: date = today - timedelta(days=1)
        return from_datetime, to_datetime, yesterday

    @staticmethod
    def _group_sales_by_vm(sales: list[Sale]) -> dict[int, list[Sale]]:
        grouped: DefaultDict[int, list[Sale]] = defaultdict(list)
        for sale in sales:
            grouped[sale.vending_machine_id].append(sale)
        return dict(grouped)

    @staticmethod
    def _sum_sales_by_day(
            sales: list[Sale],
            from_date: datetime,
            to_date: datetime,
    ) -> dict[date, float]:
        totals: DefaultDict[date, float] = defaultdict(float)
        for sale in sales:
            if sale.timestamp < from_date or sale.timestamp >= to_date:
                continue
            sale_day: date = sale.timestamp.date()
            totals[sale_day] += sale.amount
        return dict(totals)
