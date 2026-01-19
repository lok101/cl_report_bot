import argparse
import asyncio

from dotenv import load_dotenv

from src.alert_service import AlertService
from src.entities import MK
from src.kit_api import KitAPIClient
from src.telegram_client import TelegramClient

load_dotenv()

_client: KitAPIClient = KitAPIClient()
_alert_service: AlertService = AlertService()


def _parse_interval() -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Отчёт по продажам')
    parser.add_argument('--interval', type=int, required=True, help='Интервал анализа в часах')
    args: argparse.Namespace = parser.parse_args()
    interval: int = args.interval
    return interval


async def main():
    try:
        time_interval: int = _parse_interval()
        mks: list[MK] = await _client.get_all_mks()
        report: str = _alert_service.build_report(mks, time_interval)
        if not report:
            report = 'Проблем не найдено.'

        print(report)

        telegram_client: TelegramClient = TelegramClient.from_env()
        await telegram_client.send_message(report)
    except Exception as ex:
        print(ex)


asyncio.run(main())
