import os
import importlib

from typing import List

from pyrogram import Client

from src.dispatcher import Dispatcher
from src.db import Database
from src.modloader import Router, Loader


async def example_cmd(msg):
    await msg.edit("Hi")


class Manager:
    def __init__(self, client: Client) -> None:
        self.app = client

        self.routers: List[Router] = []
        self.commands: dict = {
            "global": {
                "example": example_cmd
            }
        }

        self.db = Database(os.getenv("REDIS_URL", "redis://localhost:6379"))
        self.dp = Dispatcher(self)
        self.modloader = Loader(self)
        self.me = None

    async def start(self):
        await self.app.start()
        self.me = await self.app.get_me()
        await self.modloader.load_modules()
        await self.dp.load()

    async def stop(self):
        await self.db.redis.close()
        await self.app.stop()


