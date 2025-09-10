from src.entities import MK, Sale
from src.enums import VMStatus
from src.models import VendingMachinesModel, SalesModel


def create_mks(vms: VendingMachinesModel, sales: SalesModel) -> list[MK]:
    res = []
    sales_hash_map = sales.as_hash_map()

    for vm in vms.as_list():
        if vm.status is VMStatus.ACTIVE:
            sale_models = sales_hash_map.get(vm.id, [])
            sales = [Sale(sm.good_name, sm.timestamp) for sm in sale_models]
            mk = MK(vm.id, vm.name, sales)
            res.append(mk)

    return res
