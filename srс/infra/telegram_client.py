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

    @classmethod
    def from_env_for_bot(cls) -> "TelegramClient":
        load_dotenv()
        token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")

        if not token:
            raise ValueError("Не задан TELEGRAM_BOT_TOKEN")

        safe_chat_id: str = chat_id or ""
        return cls(token=token, chat_id=safe_chat_id)

    async def send_message(self, text: str, chat_id: Optional[str] = None, as_quote: bool = False):
        url: str = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload_text: str
        parse_mode: str = "MarkdownV2"
        if as_quote:
            payload_text = self._format_quote_markdown_v2(text)
        else:
            payload_text = self._escape_markdown_v2(text)
        target_chat_id: str = self._chat_id if chat_id is None else str(chat_id)
        payload: dict[str, str] = {
            "chat_id": target_chat_id,
            "text": payload_text,
            "parse_mode": parse_mode,
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

    @staticmethod
    def _format_quote_markdown_v2(text: str) -> str:
        bold_prefix: str = "[[B]]"
        bold_suffix: str = "[[/B]]"
        lines: list[str] = text.split("\n")
        quoted_lines: list[str] = []
        line: str
        for line in lines:
            if line.startswith(bold_prefix) and line.endswith(bold_suffix):
                content: str = line[len(bold_prefix) : -len(bold_suffix)]
                escaped_content: str = TelegramClient._escape_markdown_v2_for_quote(content)
                quoted_line: str = f"> *{escaped_content}*"
            else:
                escaped_line: str = TelegramClient._escape_markdown_v2_for_quote(line)
                quoted_line = f"> {escaped_line}" if escaped_line else "> "
            quoted_lines.append(quoted_line)
        return "\n".join(quoted_lines)

    @staticmethod
    def _escape_markdown_v2_for_quote(text: str) -> str:
        to_escape: tuple[str, ...] = (
            "\\",
            "_",
            "*",
            "[",
            "]",
            "(",
            ")",
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
            "~",
            "`",
        )
        result: str = text
        for ch in to_escape:
            result = result.replace(ch, f"\\{ch}")
        return result
