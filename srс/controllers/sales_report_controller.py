import argparse
from collections.abc import Awaitable, Callable
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from srс.domain.entities.no_sales_report import NoSalesReport
from srс.domain.entities.vending_machine import VendingMachine
from srс.domain.ports.vending_machine_repository import VendingMachineRepository
from srс.services.no_sales_report_message_service import NoSalesReportMessageService
from srс.services.no_sales_report_service import NoSalesReportService
from srс.use_cases.no_sales_reports import CreateNoSalesReportMessage


class SalesReportController:
    def __init__(
            self,
            vending_machines_repository: VendingMachineRepository,
            no_sales_use_case: CreateNoSalesReportMessage,
            no_sales_service: NoSalesReportService,
            no_sales_message_service: NoSalesReportMessageService,
            last_sale_days: int,
            decline_report_builder: Callable[[], Awaitable[str]],
    ):
        self._vending_machines_repository = vending_machines_repository
        self._no_sales_use_case = no_sales_use_case
        self._no_sales_service = no_sales_service
        self._no_sales_message_service = no_sales_message_service
        self._last_sale_days = last_sale_days
        self._decline_report_builder = decline_report_builder

    async def build_report(self, args: argparse.Namespace) -> str:
        interval: int | None = args.interval
        no_sales_today: bool = args.no_sales_today

        if interval is not None:
            report: str = await self._no_sales_use_case.execute(interval_hours=interval)
            return report

        if no_sales_today:
            report_today: str = await self._build_no_sales_today()
            return report_today

        no_sales_report: str = await self._build_no_sales_yesterday_today()
        decline_report: str = await self._decline_report_builder()
        combined: str = self._combine_messages(no_sales_report, decline_report)
        return combined

    async def _build_no_sales_today(self) -> str:
        days: list[date] = self._get_moscow_today()
        vending_machines: list[VendingMachine] = await self._vending_machines_repository.get_all()
        report: NoSalesReport = await self._no_sales_service.create_report_for_days(
            vending_machines=vending_machines,
            days=days,
            last_sale_days=self._last_sale_days,
        )
        message: str = self._no_sales_message_service.create_message(report)
        return message

    async def _build_no_sales_yesterday_today(self) -> str:
        days: list[date] = self._get_moscow_yesterday_today()
        vending_machines: list[VendingMachine] = await self._vending_machines_repository.get_all()
        report: NoSalesReport = await self._no_sales_service.create_report_for_days(
            vending_machines=vending_machines,
            days=days,
            last_sale_days=self._last_sale_days,
        )
        message: str = self._no_sales_message_service.create_message(report)
        return message

    @staticmethod
    def _get_moscow_today() -> list[date]:
        now_moscow: datetime = datetime.now(ZoneInfo("Europe/Moscow"))
        today: date = now_moscow.date()
        return [today]

    @staticmethod
    def _get_moscow_yesterday_today() -> list[date]:
        now_moscow: datetime = datetime.now(ZoneInfo("Europe/Moscow"))
        today: date = now_moscow.date()
        yesterday: date = today - timedelta(days=1)
        return [yesterday, today]

    @staticmethod
    def _combine_messages(first: str, second: str) -> str:
        parts: list[str] = []
        if first:
            parts.append(first)
        if second:
            parts.append(second)
        combined: str = "\n\n".join(parts)
        return combined
