from datetime import datetime, timedelta

from src.kit_api import KitAPIClient
from src.models import SalesModel


async def get_sales_data(client: KitAPIClient, now: datetime, hours: int = 72):
    endpoint = 'GetSales'
    up_date = now - timedelta(hours=hours)

    req_filter = client.build_filter(from_date=up_date, to_date=now)

    response = await client.post_request(endpoint, req_filter)

    return SalesModel.model_validate(response)
