from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VendingMachine:
    kit_id: int
    name: str
