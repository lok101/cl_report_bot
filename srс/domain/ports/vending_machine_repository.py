from abc import ABC, abstractmethod

from srс.domain.entities.vending_machine import VendingMachine


class VendingMachineRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[VendingMachine]: pass
