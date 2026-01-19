import os
from typing import Any, Optional

import aiohttp
from dotenv import load_dotenv


class TelegramClient:
    def __init__(self, token: str, chat_id: str):
        self._token: str = token
        self._chat_id: str = chat_id

    @classmethod
    def from_env(cls) -> "TelegramClient":
        load_dotenv()
        token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            raise ValueError("Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")

        return cls(token=token, chat_id=chat_id)

    async def send_message(self, text: str, chat_id: Optional[str] = None):
        url: str = f"https://api.telegram.org/bot{self._token}/sendMessage"
        escaped_text: str = self._escape_markdown_v2(text)
        target_chat_id: str = self._chat_id if chat_id is None else str(chat_id)
        payload: dict[str, str] = {
            "chat_id": target_chat_id,
            "text": f"```{escaped_text}```",
            "parse_mode": "MarkdownV2",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=payload) as response:
                response.raise_for_status()
                data: dict[str, Any] = await response.json()
                if not data.get("ok"):
                    raise Exception(f"Ошибка Telegram API: {data}")

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 60) -> list[dict[str, Any]]:
        url: str = f"https://api.telegram.org/bot{self._token}/getUpdates"
        params: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params) as response:
                response.raise_for_status()
                data: dict[str, Any] = await response.json()
                if not data.get("ok"):
                    raise Exception(f"Ошибка Telegram API: {data}")
                result: list[dict[str, Any]] = data.get("result", [])
                return result

    @staticmethod
    def _escape_markdown_v2(text: str) -> str:
        to_escape: tuple[str, ...] = (
            "_",
            "*",
            "[",
            "]",
            "(",
            ")",
            "~",
            "`",
            ">",
            "#",
            "+",
            "-",
            "=",
            "|",
            "{",
            "}",
            ".",
            "!",
        )
        result: str = text
        for ch in to_escape:
            result = result.replace(ch, f"\\{ch}")
        return result
