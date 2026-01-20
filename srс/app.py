import argparse
import os
import shlex
from typing import Any, Optional

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
    parser: argparse.ArgumentParser = _build_cli_parser()
    args: argparse.Namespace = parser.parse_args()
    return args


def _build_cli_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Отчеты по продажам")
    _add_report_args(parser)
    parser.add_argument("--bot", action="store_true", help="Запуск в режиме Telegram-бота")
    return parser


def _build_bot_parser() -> argparse.ArgumentParser:
    parser: BotArgumentParser = BotArgumentParser(description="Команда отчета бота")
    _add_report_args(parser)
    return parser


def _add_report_args(parser: argparse.ArgumentParser):
    parser.add_argument("--interval", type=int, help="Интервал анализа в часах")
    parser.add_argument("--no-sales-today", action="store_true", help="Отчет без продаж за сегодня")


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


class BotArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
        raise ValueError(message)


def _extract_command_args(text: str) -> list[str] | None:
    tokens: list[str] = shlex.split(text)
    if not tokens:
        return None
    raw_command: str = tokens[0]
    command: str = raw_command.split("@")[0]
    if command != "/get_sales_report":
        return None
    return tokens[1:]


def _format_bot_usage() -> str:
    return "/get_sales_report [--interval N] [--no-sales-today]"


def _parse_bot_args(text: str, parser: argparse.ArgumentParser) -> argparse.Namespace:
    args_tokens: list[str] | None = _extract_command_args(text)
    if args_tokens is None:
        raise ValueError("Команда не распознана")
    args: argparse.Namespace = parser.parse_args(args_tokens)
    return args


async def _run_bot():
    telegram_client: TelegramClient = TelegramClient.from_env_for_bot()
    client: KitVendingAPIClient = _create_client()
    try:
        controller: SalesReportController = _build_controller(client)
        bot_parser: argparse.ArgumentParser = _build_bot_parser()
        offset: Optional[int] = await _initialize_bot_offset(telegram_client)
        while True:
            updates: list[dict[str, Any]] = await telegram_client.get_updates(offset=offset, timeout=60)
            for update in updates:
                update_data: dict[str, Any] = update
                update_id: int = int(update_data.get("update_id", 0))
                offset = update_id + 1
                message: dict[str, Any] | None = update_data.get("message")
                if not message:
                    continue
                text: str = str(message.get("text", "")).strip()
                if not text:
                    continue
                try:
                    args: argparse.Namespace = _parse_bot_args(text, bot_parser)
                except ValueError as exc:
                    if "Команда не распознана" in str(exc):
                        continue
                    error_text: str = f"Неверные аргументы: {exc}\nИспользование: {_format_bot_usage()}"
                    chat_id: str = str(message.get("chat", {}).get("id", ""))
                    if chat_id:
                        await telegram_client.send_message(error_text, chat_id=chat_id, as_quote=True)
                    continue
                report_message: str = await controller.build_report(args)
                if report_message:
                    chat_id: str = str(message.get("chat", {}).get("id", ""))
                    if chat_id:
                        formatted_message: str = _apply_heading_bold(report_message)
                        await telegram_client.send_message(formatted_message, chat_id=chat_id, as_quote=True)
    finally:
        await client.close()


async def _initialize_bot_offset(telegram_client: TelegramClient) -> Optional[int]:
    updates: list[dict[str, Any]] = await telegram_client.get_updates(timeout=0)
    if not updates:
        return None
    last_update_id: int = int(updates[-1].get("update_id", 0))
    return last_update_id + 1


def _build_controller(client: KitVendingAPIClient) -> SalesReportController:
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
    return controller


async def app():
    args: argparse.Namespace = _parse_args()
    if getattr(args, "bot", False):
        await _run_bot()
        return
    client: KitVendingAPIClient = _create_client()
    try:
        controller: SalesReportController = _build_controller(client)
        message: str = await controller.build_report(args)

        if message:
            telegram_client: TelegramClient = TelegramClient.from_env()
            formatted_message: str = _apply_heading_bold(message)
            await telegram_client.send_message(formatted_message, as_quote=True)
    finally:
        await client.close()


def _apply_heading_bold(message: str) -> str:
    headings: tuple[str, ...] = (
        "Аппараты без продаж:",
        "Аппараты с падением продаж:",
    )
    lines: list[str] = message.split("\n")
    index: int
    line: str
    for index, line in enumerate(lines):
        if line in headings:
            lines[index] = f"[[B]]{line}[[/B]]"
    return "\n".join(lines)
