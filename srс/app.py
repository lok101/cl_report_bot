import argparse
import os

from dotenv import load_dotenv
from kit_api import KitVendingAPIClient

from srс.controllers.sales_report_controller import SalesReportController
from srс.infra.kit_api_sales_repository import KitAPISalesRepository
from srс.infra.kit_api_vending_machine_repository import KitAPIVendingMachineRepository
from srс.infra.telegram_client import TelegramClient
from srс.services.no_sales_report_message_service import NoSalesReportMessageService
from srс.services.no_sales_report_service import NoSalesReportService
from srс.domain.entities.sales_analyze_report import SalesAnalyzeReport
from srс.domain.entities.vending_machine import VendingMachine
from srс.services.sales_analyze_service import SalesAnalyzeService
from srс.services.sales_report_message_service import SalesReportMessageService
from srс.use_cases.no_sales_reports import CreateNoSalesReportMessage

load_dotenv()

LAST_SALE_DAYS: int = 10


def _get_required_env(name: str) -> str:
    value: str | None = os.getenv(name)
    if not value:
        raise ValueError(f"Не задано значение {name}")
    return value


def _parse_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Отчеты по продажам")
    parser.add_argument("--interval", type=int, help="Интервал анализа в часах")
    parser.add_argument("--no-sales-today", action="store_true", help="Отчет без продаж за сегодня")
    args: argparse.Namespace = parser.parse_args()
    return args


def _create_client() -> KitVendingAPIClient:
    login: str = _get_required_env("KIT_API_LOGIN")
    password: str = _get_required_env("KIT_API_PASSWORD")
    company_id_str: str = _get_required_env("KIT_API_COMPANY_ID")
    company_id: int = int(company_id_str)
    client: KitVendingAPIClient = KitVendingAPIClient()
    client.login(login, password, company_id)
    return client


def _get_sales_analyze_settings() -> tuple[int, float]:
    days_for_average_str: str = _get_required_env("DAYS_FOR_AVERAGE")
    decline_threshold_str: str = _get_required_env("DECLINE_THRESHOLD")
    days_for_average: int = int(days_for_average_str)
    decline_threshold: float = float(decline_threshold_str)
    return days_for_average, decline_threshold


async def app():
    args: argparse.Namespace = _parse_args()
    client: KitVendingAPIClient = _create_client()
    try:
        vending_machine_repo: KitAPIVendingMachineRepository = KitAPIVendingMachineRepository(client)
        sales_repo: KitAPISalesRepository = KitAPISalesRepository(client)
        no_sales_service: NoSalesReportService = NoSalesReportService(sales_repo)
        no_sales_message_service: NoSalesReportMessageService = NoSalesReportMessageService(
            last_sale_days=LAST_SALE_DAYS,
        )
        no_sales_use_case: CreateNoSalesReportMessage = CreateNoSalesReportMessage(
            vending_machines_repository=vending_machine_repo,
            report_service=no_sales_service,
            message_service=no_sales_message_service,
            last_sale_days=LAST_SALE_DAYS,
        )

        async def _build_decline_report() -> str:
            days_for_average: int
            decline_threshold: float
            days_for_average, decline_threshold = _get_sales_analyze_settings()
            sales_analyze_service: SalesAnalyzeService = SalesAnalyzeService(
                sales_repo,
                days_for_average,
                decline_threshold,
            )
            sales_message_service: SalesReportMessageService = SalesReportMessageService()
            vending_machines: list[VendingMachine] = await vending_machine_repo.get_all()
            report: SalesAnalyzeReport = await sales_analyze_service.create_sales_analyze_report(
                vending_machines=vending_machines,
            )
            message: str = sales_message_service.create_message(report)
            return message

        controller: SalesReportController = SalesReportController(
            vending_machines_repository=vending_machine_repo,
            no_sales_use_case=no_sales_use_case,
            no_sales_service=no_sales_service,
            no_sales_message_service=no_sales_message_service,
            last_sale_days=LAST_SALE_DAYS,
            decline_report_builder=_build_decline_report,
        )
        message: str = await controller.build_report(args)

        if message:
            telegram_client: TelegramClient = TelegramClient.from_env()
            await telegram_client.send_message(message)
    finally:
        await client.close()
