import enum
import hashlib
import json
import os
import time
from datetime import datetime

import aiohttp
from typing import Any, Optional

from dotenv import load_dotenv

from src.entities import MK
from src.models import VendingMachinesModel, VendingMachinesStatusesModel

load_dotenv()
BASE_URL = "https://api2.kit-invest.ru/APIService.svc"


class Endpoints(enum.StrEnum):
    VM_STATUSES = 'GetVMStates'
    VMS = 'GetVendingMachines'


def _datetime_to_str(val: datetime) -> str:
    return val.strftime('%d.%m.%Y %H:%M:%S')


class KitAPIClient:
    def __init__(self):
        self._company_id = os.getenv("KIT_API_COMPANY_ID")
        self._user_login = os.getenv("KIT_API_LOGIN")
        self._password = os.getenv("KIT_API_PASSWORD")
        self._base_url = BASE_URL
        self.request_counter = int(time.time_ns())

    async def get_all_mks(self) -> list[MK]:
        all_vms = await self.get_all_vms()
        all_states = await self.get_all_vms_states()

        vms_hash_map = all_vms.as_hash_map()

        res = []

        for state in all_states.as_list():
            vm = vms_hash_map[state.id]

            if vm.id != state.id:
                raise Exception('Id двух переданных объектов должны быть одинаковыми.')

            mk = MK(
                id=vm.id,
                name=vm.name,
                statuses=state.statuses,
                last_sale_timestamp=state.last_sale_timestamp,
                last_ping_timestamp=state.last_ping_timestamp,
                company=vm.company
            )
            res.append(mk)

        return res

    async def get_all_vms(self) -> VendingMachinesModel:
        vms = await self._post_request(endpoint=Endpoints.VMS)
        return VendingMachinesModel.model_validate(vms)

    async def get_all_vms_states(self) -> VendingMachinesStatusesModel:
        vms = await self._post_request(endpoint=Endpoints.VM_STATUSES)
        return VendingMachinesStatusesModel.model_validate(vms)

    async def _post_request(self, endpoint: str, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        request_body = self._build_request_body()

        if payload:
            request_body.update(payload)

        request = json.dumps(request_body)

        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{self._base_url}/{endpoint}", data=request) as response:
                response.raise_for_status()
                data = await response.json()

                if data['ResultCode'] != 0:
                    raise Exception(f'Получен ResultCode - {data['ResultCode']}')

                return data

    def build_filter(
            self,
            from_date: datetime,
            to_date: datetime,
            company_id: Optional[str] = None,
            vending_machine_id: Optional[int] = None,
    ) -> dict[str, Any]:
        up_date = _datetime_to_str(from_date)
        to_date = _datetime_to_str(to_date)
        company_id = str(company_id) if company_id else self._company_id
        filter_obj = {
            "UpDate": up_date,
            "ToDate": to_date,
            "CompanyId": company_id
        }
        if vending_machine_id is not None:
            filter_obj["VendingMachineId"] = str(vending_machine_id)
        return {'Filter': filter_obj}

    def _build_request_body(self) -> dict[str, Any]:
        self.request_counter += 1
        request_id = self.request_counter
        sign = hashlib.md5(f"{self._company_id}{self._password}{request_id}".encode("utf-8")).hexdigest()
        return {
            'Auth': {
                "CompanyId": self._company_id,
                "RequestId": request_id,
                "UserLogin": self._user_login,
                "Sign": sign
            }
        }
