from abc import ABC, abstractmethod
from datetime import datetime

from srс.domain.entities.sale import Sale


class SalesRepository(ABC):
    @abstractmethod
    async def get_sales(
            self,
            from_date: datetime,
            to_date: datetime,
            vending_machine_id: int | None = None,
    ) -> list[Sale]: pass
