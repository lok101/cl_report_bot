from abc import ABC, abstractmethod


class VendingMachineRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[...]: pass
