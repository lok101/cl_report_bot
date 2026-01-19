import aiohttp

URL = 'https://smartapp-code.sberdevices.ru/tools/api/now?tz=Europe/Moscow&format=dd/MM/yyyy'


async def get_now_timestamp() -> int:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.get(url=URL) as response:
            response.raise_for_status()
            data = await response.json()
            return data['timestamp']
