from collections import defaultdict
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.enums import VMStatus


class SaleModel(BaseModel):
    vm_id: int = Field(validation_alias='VendingMachine')
    vm_name: str = Field(validation_alias='VendingMachineName')
    good_name: str = Field(validation_alias='GoodsName')
    price: int = Field(validation_alias='Sum')
    timestamp: datetime = Field(validation_alias='DateTime')

    @field_validator('timestamp', mode='before')
    @classmethod
    def to_datetime(cls, val: str) -> datetime:
        return datetime.strptime(val, '%d.%m.%Y %H:%M:%S')


class SalesModel(BaseModel):
    sales: list[SaleModel] = Field(validation_alias='Sales')

    def as_hash_map(self) -> dict[int, list[SaleModel]]:
        hash_map = defaultdict(list)
        for sale in self.sales:
            hash_map[sale.vm_id].append(sale)
        return hash_map


class VendingMachineModel(BaseModel):
    id: int = Field(validation_alias='VendingMachineId')
    name: str = Field(validation_alias='VendingMachineName')
    terminal_id: int | None = Field(validation_alias='ModemSerialNumber')

    @property
    def status(self) -> VMStatus:
        return VMStatus.ACTIVE if self.terminal_id else VMStatus.DISABLE


class VendingMachinesModel(BaseModel):
    vending_machines: list[VendingMachineModel] = Field(validation_alias='VendingMachines')

    def as_list(self) -> list[VendingMachineModel]:
        return self.vending_machines.copy()

    def as_hash_map(self) -> dict:
        return {vm.id: vm for vm in self.vending_machines}
