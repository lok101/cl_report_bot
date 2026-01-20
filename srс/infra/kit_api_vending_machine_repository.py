from kit_api import KitVendingAPIClient, VendingMachinesCollection, VendingMachineModel

from srс.domain.entities.vending_machine import VendingMachine
from srс.domain.ports.vending_machine_repository import VendingMachineRepository


class KitAPIVendingMachineRepository(VendingMachineRepository):
    def __init__(self, client: KitVendingAPIClient):
        self._client = client

    async def get_all(self) -> list[VendingMachine]:
        vms: VendingMachinesCollection = await self._client.get_vending_machines()
        items: list[VendingMachine] = []
        vm_model: VendingMachineModel

        active_machines = vms.get_active()

        for vm_model in active_machines:
            item: VendingMachine = VendingMachine(
                kit_id=vm_model.id,
                name=vm_model.name,
            )
            items.append(item)
        return items
