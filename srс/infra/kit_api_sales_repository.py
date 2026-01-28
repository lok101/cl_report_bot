import time
from datetime import datetime
from zoneinfo import ZoneInfo

from kit_api import KitVendingAPIClient, SalesCollection
from kit_api.models.sales import SaleModel

from srс.domain.entities.sale import Sale
from srс.domain.ports.sales_repository import SalesRepository

_PROJECT_TZ = ZoneInfo("Asia/Yekaterinburg")

_CACHE_TTL_SECONDS: float = 60.0


class KitAPISalesRepository(SalesRepository):
    def __init__(self, client: KitVendingAPIClient):
        self._client = client
        self._cache: dict[int, list[Sale]] = {}
        self._cache_timestamp: float | None = None
        self._cache_from: datetime | None = None
        self._cache_to: datetime | None = None

    async def get_sales(
            self,
            from_date: datetime,
            to_date: datetime,
            vending_machine_id: int | None = None,
    ) -> list[Sale]:
        if not self._is_cache_valid(from_date=from_date, to_date=to_date):
            await self._refresh_cache(from_date=from_date, to_date=to_date)

        if vending_machine_id is None:
            return self._flatten_cache()

        return self._cache.get(vending_machine_id, []).copy()

    def _is_cache_valid(self, from_date: datetime, to_date: datetime) -> bool:
        if self._cache_timestamp is None:
            return False
        if not self._cache:
            return False
        if self._cache_from != from_date or self._cache_to != to_date:
            return False
        return (time.monotonic() - self._cache_timestamp) < _CACHE_TTL_SECONDS

    async def _refresh_cache(self, from_date: datetime, to_date: datetime) -> None:
        sales_model: SalesCollection = await self._client.get_sales(
            from_date=from_date,
            to_date=to_date,
        )
        cache: dict[int, list[Sale]] = {}
        sale_model: SaleModel

        for sale_model in sales_model.get_all():
            timestamp: datetime = sale_model.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=_PROJECT_TZ)
            sale: Sale = Sale(
                vending_machine_id=sale_model.vending_machine_id,
                amount=float(sale_model.price),
                timestamp=timestamp,
            )
            cache.setdefault(sale.vending_machine_id, []).append(sale)
        self._cache = cache
        self._cache_timestamp = time.monotonic()
        self._cache_from = from_date
        self._cache_to = to_date

    def _flatten_cache(self) -> list[Sale]:
        sales: list[Sale] = []
        vm_sales: list[Sale]
        for vm_sales in self._cache.values():
            sales.extend(vm_sales)
        return sales
