from collections import defaultdict
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, BeforeValidator


def str_to_datetime(val: str) -> datetime | None:
    if val:
        return datetime.strptime(val, '%d.%m.%Y %H:%M:%S')
    return None


class SaleModel(BaseModel):
    vm_id: int = Field(validation_alias='VendingMachine')
    vm_name: str = Field(validation_alias='VendingMachineName')
    good_name: str = Field(validation_alias='GoodsName')
    price: int = Field(validation_alias='Sum')
    timestamp: Annotated[datetime, Field(validation_alias='DateTime'), BeforeValidator(str_to_datetime)]


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


class VendingMachinesModel(BaseModel):
    items: list[VendingMachineModel] = Field(validation_alias='VendingMachines')

    def as_list(self) -> list[VendingMachineModel]:
        return self.items.copy()

    def as_hash_map(self) -> dict:
        return {vm.id: vm for vm in self.items}


class VendingMachineStatus(BaseModel):
    id: int = Field(validation_alias='VendingMachineId')
    statuses: set[int] = Field(validation_alias='Statuses')
    last_sale_timestamp: Annotated[
        datetime | None,
        Field(validation_alias='LastSaleDateTime'),
        BeforeValidator(str_to_datetime)
    ]
    last_ping_timestamp: Annotated[
        datetime,
        Field(validation_alias='DateTime'),
        BeforeValidator(str_to_datetime)
    ]

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
