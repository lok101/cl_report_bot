import hashlib
import json
import os
import time
from datetime import datetime

import aiohttp
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://api2.kit-invest.ru/APIService.svc"


def _datetime_to_str(val: datetime) -> str:
    return val.strftime('%d.%m.%Y %H:%M:%S')


class KitAPIClient:
    def __init__(self):
        self._company_id = os.getenv("KIT_API_COMPANY_ID")
        self._user_login = os.getenv("KIT_API_LOGIN")
        self._password = os.getenv("KIT_API_PASSWORD")
        self._base_url = BASE_URL
        self.request_counter = int(time.time_ns())

    async def post_request(
            self, endpoint: str, payload: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:

        if payload is None:
            payload = {}

        full_payload = {"Auth": self._build_auth()}
        full_payload.update(payload)
        request = json.dumps(full_payload)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=f"{self._base_url}/{endpoint}", data=request
            ) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    def build_filter(
            from_date: datetime,
            to_date: datetime,
            company_id: Optional[int] = None,
            vending_machine_id: Optional[int] = None,
    ) -> dict[str, Any]:
        up_date = _datetime_to_str(from_date)
        to_date = _datetime_to_str(to_date)
        filter_obj = {"UpDate": up_date, "ToDate": to_date}
        if company_id is not None:
            filter_obj["CompanyId"] = str(company_id)
        if vending_machine_id is not None:
            filter_obj["VendingMachineId"] = str(vending_machine_id)
        return {'Filter': filter_obj}

    def _generate_request_id(self) -> int:
        self.request_counter += 1
        return self.request_counter

    def _generate_sign(self, request_id: int) -> str:

        sign_string = f"{self._company_id}{self._password}{request_id}"
        return hashlib.md5(sign_string.encode("utf-8")).hexdigest()

    def _build_auth(self) -> dict[str, Any]:

        request_id = self._generate_request_id()
        return {
            "CompanyId": self._company_id,
            "RequestId": request_id,
            "UserLogin": self._user_login,
            "Sign": self._generate_sign(request_id),
        }
