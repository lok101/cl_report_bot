import argparse
import os
import shlex
from typing import Any, Awaitable, Callable, Optional

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from kit_api import KitVendingAPIClient

from srс.controllers.sales_report_controller import SalesReportController
from srс.infra.telegram_client import TelegramClient


class BotArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
        raise ValueError(message)


def apply_heading_bold(message: str) -> str:
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


def _build_bot_parser() -> argparse.ArgumentParser:
    parser: BotArgumentParser = BotArgumentParser(description="Команда отчета бота")
    _add_report_args(parser)
    return parser


def _add_report_args(parser: argparse.ArgumentParser):
    parser.add_argument("--no-sales-today", action="store_true", help="Отчет без продаж за сегодня")


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
    return "/get_sales_report [--no-sales-today]"


def _parse_bot_args(text: str, parser: argparse.ArgumentParser) -> argparse.Namespace:
    args_tokens: list[str] | None = _extract_command_args(text)
    if args_tokens is None:
        raise ValueError("Команда не распознана")
    args: argparse.Namespace = parser.parse_args(args_tokens)
    return args


def _get_bot_token() -> str:
    load_dotenv()
    token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Не задан TELEGRAM_BOT_TOKEN")
    return token


class BotContextMiddleware(BaseMiddleware):
    def __init__(
        self,
        controller: SalesReportController,
        bot_parser: argparse.ArgumentParser,
    ):
        self._controller: SalesReportController = controller
        self._bot_parser: argparse.ArgumentParser = bot_parser

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        data["controller"] = self._controller
        data["bot_parser"] = self._bot_parser
        return await handler(event, data)


async def handle_sales_report(
    message: Message,
    controller: SalesReportController,
    bot_parser: argparse.ArgumentParser,
):
    raw_text: str = message.text or ""
    text: str = raw_text.strip()
    try:
        args: argparse.Namespace = _parse_bot_args(text, bot_parser)
    except ValueError as exc:
        error_text: str = f"Неверные аргументы: {exc}\nИспользование: {_format_bot_usage()}"
        formatted_error: str = TelegramClient.format_quote_markdown_v2(error_text)
        await message.answer(formatted_error, parse_mode="MarkdownV2")
        return
    report_message: str = await controller.build_report(args)
    if report_message:
        formatted_message: str = apply_heading_bold(report_message)
        payload_text: str = TelegramClient.format_quote_markdown_v2(formatted_message)
        await message.answer(payload_text, parse_mode="MarkdownV2")


async def run_bot(
    create_client: Callable[[], KitVendingAPIClient],
    build_controller: Callable[[KitVendingAPIClient], SalesReportController],
):
    client: KitVendingAPIClient = create_client()
    bot_token: str = _get_bot_token()
    try:
        controller: SalesReportController = build_controller(client)
        bot_parser: argparse.ArgumentParser = _build_bot_parser()
        async with Bot(token=bot_token) as bot:
            dispatcher: Dispatcher = Dispatcher()
            context_middleware: BotContextMiddleware = BotContextMiddleware(
                controller=controller,
                bot_parser=bot_parser,
            )
            dispatcher.message.middleware(context_middleware)
            dispatcher.message.register(handle_sales_report, Command("get_sales_report"))
            await dispatcher.start_polling(bot)
    finally:
        await client.close()


