from collections import defaultdict
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SaleModel(BaseModel):
    vm_id: int = Field(validation_alias='VendingMachine')
    vm_name: str = Field(validation_alias='VendingMachineName')
    good_name: str = Field(validation_alias='GoodsName')
    price: int = Field(validation_alias='Sum')
    timestamp: datetime = Field(validation_alias='DateTime')

    # noinspection PyNestedDecorators
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
    company: int = Field(validation_alias='CompanyId')
    # terminal_id: int | None = Field(validation_alias='ModemSerialNumber')

    # @property
    # def status(self) -> VMStatus:
    #     return VMStatus.ACTIVE if self.terminal_id else VMStatus.DISABLE


class VendingMachinesModel(BaseModel):
    items: list[VendingMachineModel] = Field(validation_alias='VendingMachines')

    def as_list(self) -> list[VendingMachineModel]:
        return self.items.copy()

    def as_hash_map(self) -> dict:
        return {vm.id: vm for vm in self.items}


class VendingMachineStatus(BaseModel):
    id: int = Field(validation_alias='VendingMachineId')
    statuses: set[int] = Field(validation_alias='Statuses')
    last_sale_timestamp: datetime = Field(validation_alias='LastSaleDateTime')
    last_ping_timestamp: datetime = Field(validation_alias='DateTime')

    # noinspection PyNestedDecorators
    @field_validator('last_sale_timestamp', 'last_ping_timestamp', mode='before')
    @classmethod
    def to_datetime(cls, val: str) -> datetime:
        return datetime.strptime(val, '%d.%m.%Y %H:%M:%S')

    # noinspection PyNestedDecorators
    @field_validator('statuses', mode='before')
    @classmethod
    def to_statuses_list(cls, val: str) -> set[int]:
        return set(map(int, val.split(',')))


class VendingMachinesStatusesModel(BaseModel):
    items: list[VendingMachineStatus] = Field(validation_alias='VendingMachines')

    def as_list(self) -> list[VendingMachineStatus]:
        return self.items.copy()

    def as_hash_map(self) -> dict:
        return {vm.id: vm for vm in self.items}
