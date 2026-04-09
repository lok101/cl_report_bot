import json
import re
import time
from pathlib import Path

from kit_api import KitVendingAPIClient, VendingMachineModel

from srс.domain.entities.vending_machine import VendingMachine
from srс.domain.ports.vending_machine_repository import VendingMachineRepository


def _agent_debug_ndjson(payload: dict[str, object]) -> None:
    # #region agent log
    payload = {
        "sessionId": "d50d82",
        "timestamp": int(time.time() * 1000),
        **payload,
    }
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    for path in (
        Path("/var/log/cl_report_bot/debug-d50d82.log"),
        Path(__file__).resolve().parents[2] / "debug-d50d82.log",
    ):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(line)
            break
        except OSError:
            continue
    # #endregion


class KitAPIVendingMachineRepository(VendingMachineRepository):
    def __init__(self, client: KitVendingAPIClient):
        self._client = client

    async def get_all(self) -> list[VendingMachine]:
        raw_vms = await self._client.get_vending_machines()
        _agent_debug_ndjson(
            {
                "runId": "verify",
                "hypothesisId": "A",
                "location": "kit_api_vending_machine_repository.py:get_all",
                "message": "raw get_vending_machines return type",
                "data": {
                    "type_name": type(raw_vms).__name__,
                    "has_get_all": hasattr(raw_vms, "get_all"),
                },
            }
        )
        vms: list[VendingMachineModel] = (
            raw_vms if isinstance(raw_vms, list) else raw_vms.get_all()
        )
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
