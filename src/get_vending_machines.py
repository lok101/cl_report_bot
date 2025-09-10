from src.kit_api import KitAPIClient
from src.models import VendingMachinesModel


async def get_vending_machines(client: KitAPIClient):
    endpoint = 'GetVendingMachines'

    response = await client.post_request(endpoint)

    return VendingMachinesModel.model_validate(response)
