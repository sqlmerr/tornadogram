import logging
import asyncio
from typing import List

from src.manager import Manager


class TelegramHandler(logging.StreamHandler):
    def __init__(self, manager: Manager):
        self.manager = manager
        self.buffer: List[logging.LogRecord] = []
        asyncio.get_event_loop().create_task(self.send_to_telegram())
        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        if not self.manager.db.get("bot", "using_bot", False):
            return
        self.buffer.append(record)

    async def send_to_telegram(self):
        while True:
            if not self.buffer:
                await asyncio.sleep(3)
                continue
            text = ""
            for record in self.buffer:
                text += (
                    f"<b>[{record.levelname}]</b>\n <code>{record.message}</code>\n\n"
                )
            self.buffer.clear()

            await self.manager.bot.send_message(self.manager.me.id, text)
            await asyncio.sleep(3)
