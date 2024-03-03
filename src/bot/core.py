import asyncio
import logging

from configparser import NoSectionError, NoOptionError

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.token import TokenValidationError, validate_token

from src import manager
from .events import Events


class BotManager(Events):
    def __init__(self, manager: "manager.Manager") -> None:
        self.manager = manager
        self.bot: Bot = None
        self.dp: Dispatcher = None

    async def load(self):
        if not self.manager.db.get("bot", "using_bot", True):
            return
        logging.info("loading bot manager")
        try:
            token = self.manager.config.get("bot", "token")
        except (NoOptionError, NoSectionError):
            token = None

        if not token:
            is_valid = False
            print("Please create inline bot.")
            while not is_valid:
                token = input("Enter bot token: ")
                try:
                    validate_token(token)
                    break
                except TokenValidationError:
                    response = input("token is invalid, do you need inline bot? y/n: ")
                    if "y" in response.lower():
                        print("ok, please enter valid token")
                    else:
                        print("ok")
                        self.manager.db.set("bot", "using_bot", False)
                        return

            self.manager.config["bot"]["token"] = token

            with open("settings.ini", "w") as f:
                self.manager.config.write(f)

        token = self.manager.config["bot"]["token"]

        self.bot = Bot(token, default=DefaultBotProperties(parse_mode="html"))
        self.dp = Dispatcher()
        self.dp.message.register(self.message_handler)

        task = asyncio.create_task(self.dp.start_polling(self.bot))
        await asyncio.gather(task)

        logging.info("successfully")
