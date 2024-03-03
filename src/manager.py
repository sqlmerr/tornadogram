from configparser import ConfigParser

from pyrogram import Client

from src.dispatcher import Dispatcher
from src.db import Database
from src.modloader import Loader
from src.bot import BotManager


class Manager:
    def __init__(self, client: Client, config: ConfigParser) -> None:
        self.app = client
        self.config = config

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
        self.modloader.save_config()
        await self.app.stop()
