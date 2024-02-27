import os

from pyrogram import Client

from src.dispatcher import Dispatcher
from src.db import Database


async def example_cmd(msg):
    await msg.edit("Hi")


class Manager:
    def __init__(self, client: Client) -> None:
        self.app = client
        self.commands: dict = {
            "example": example_cmd
        }

        self.db = Database(os.getenv("REDIS_URL", "redis://localhost:6397"))
        self.dp = Dispatcher(self)

    async def start(self):
        await self.app.start()
        await self.dp.load()
