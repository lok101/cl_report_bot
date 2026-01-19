import argparse
import asyncio
from typing import Any, Optional

from dotenv import load_dotenv

from src.alert_service import AlertService
from src.entities import MK
from src.kit_api import KitAPIClient
from src.telegram_client import TelegramClient

load_dotenv()

_client: KitAPIClient = KitAPIClient()
_alert_service: AlertService = AlertService()


def _parse_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Отчёт по продажам')
    parser.add_argument('--interval', type=int, help='Интервал анализа в часах')
    parser.add_argument('--listen', action='store_true', help='Слушать команды бота')
    args: argparse.Namespace = parser.parse_args()
    return args


async def _build_report(interval: int) -> str:
    mks: list[MK] = await _client.get_all_mks()
    report: str = _alert_service.build_report(mks, interval)
    if not report:
        report = 'Проблем не найдено.'
    return report


async def _handle_command(text: str, chat_id: str, telegram_client: TelegramClient):
    parts: list[str] = text.strip().split()
    if not parts:
        return

    command: str = parts[0].split('@')[0]
    if command != '/get_sales_report':
        return

    if len(parts) < 2:
        await telegram_client.send_message(
            'Нужен интервал в часах. Пример: /get_sales_report 24',
            chat_id=chat_id,
        )
        return

    try:
        interval: int = int(parts[1])
    except ValueError:
        await telegram_client.send_message(
            'Интервал должен быть числом. Пример: /get_sales_report 24',
            chat_id=chat_id,
        )
        return

    report: str = await _build_report(interval)
    await telegram_client.send_message(report, chat_id=chat_id)


async def _listen_for_commands():
    telegram_client: TelegramClient = TelegramClient.from_env()
    offset: Optional[int] = None

    while True:
        updates: list[dict[str, Any]] = await telegram_client.get_updates(offset=offset, timeout=60)
        last_update_id: Optional[int] = None

        for update in updates:
            update_id: Optional[int] = update.get("update_id") if isinstance(update, dict) else None
            if isinstance(update_id, int):
                last_update_id = update_id

            if not isinstance(update, dict):
                continue

            message: Optional[dict[str, Any]] = update.get("message")
            if not isinstance(message, dict):
                continue

            text: Optional[str] = message.get("text") if isinstance(message.get("text"), str) else None
            if not text:
                continue

            chat: Optional[dict[str, Any]] = message.get("chat")
            if not isinstance(chat, dict):
                continue

            chat_id_value: Optional[Any] = chat.get("id")
            if chat_id_value is None:
                continue

            chat_id: str = str(chat_id_value)
            await _handle_command(text, chat_id, telegram_client)

        if last_update_id is not None:
            offset = last_update_id + 1


async def main():
    try:
        args: argparse.Namespace = _parse_args()
        if args.listen:
            await _listen_for_commands()
            return

        if args.interval is None:
            raise ValueError('Нужно указать --interval или --listen')

        report: str = await _build_report(args.interval)
        print(report)

        telegram_client: TelegramClient = TelegramClient.from_env()
        await telegram_client.send_message(report)
    except Exception as ex:
        print(ex)


asyncio.run(main())
