from abc import ABC, abstractmethod

from srс.domain.entities.vending_machine import VendingMachine


class VendingMachineRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[VendingMachine]: pass
