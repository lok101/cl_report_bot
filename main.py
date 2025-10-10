import asyncio

from src.alert_service import AlertService
from src.kit_api import KitAPIClient

_client = KitAPIClient()
_alert_service = AlertService()


async def main():
    time_interval = int(input('Введите время для анализа: '))
    mks = await _client.get_all_mks()
    _alert_service.print_mk_without_sales(mks, time_interval)
    _alert_service.print_mk_with_network_connection_error(mks)
    _alert_service.print_snack_with_sales_unknown_product(mks)


asyncio.run(main())
