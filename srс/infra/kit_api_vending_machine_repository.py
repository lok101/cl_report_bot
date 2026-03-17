import re

from kit_api import KitVendingAPIClient, VendingMachineModel

from srс.domain.entities.vending_machine import VendingMachine
from srс.domain.ports.vending_machine_repository import VendingMachineRepository


class KitAPIVendingMachineRepository(VendingMachineRepository):
    def __init__(self, client: KitVendingAPIClient):
        self._client = client

    async def get_all(self) -> list[VendingMachine]:
        vms: list[VendingMachineModel] = await self._client.get_vending_machines()
        items: list[VendingMachine] = []

        for model in vms:
            vm: VendingMachine = self._map_to_domain(model)

            if vm.is_active:
                items.append(vm)

        return items

    @staticmethod
    def _map_to_domain(model: VendingMachineModel) -> VendingMachine:
        machine_name: str = model.name

        def get_active_status(name: str) -> bool:
            if "тест" in name.lower():
                return False

            pattern = r'^\[ X \]'
            match = re.match(pattern, name, re.IGNORECASE)

            if match:
                return False

            return True

        return VendingMachine(
            name=machine_name,
            kit_id=model.id,
            is_active=get_active_status(machine_name),
        )
