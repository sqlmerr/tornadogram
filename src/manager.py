from configparser import ConfigParser
from typing import List

from pyrogram import Client

from src.dispatcher import Dispatcher
from src.db import Database
from src.modloader import Router, Loader
from src.bot import BotManager


async def example_cmd(msg):
    await msg.edit("Hi")


class Manager:
    def __init__(self, client: Client, config: ConfigParser) -> None:
        self.app = client
        self.config = config

        self.routers: List[Router] = []
        self.commands: dict = {"global": {"example": example_cmd}}

        self.db = Database()
        self.dp = Dispatcher(self)
        self.modloader = Loader(self)
        self.me = None
        
        self.bot_manager = BotManager(self)
        self.bot = None

    async def start(self):
        await self.app.start()
        self.me = await self.app.get_me()
        await self.modloader.load_modules()
        await self.dp.load()

        await self.bot_manager.load()
        self.bot = self.bot_manager.bot


    async def stop(self):
        await self.app.stop()
