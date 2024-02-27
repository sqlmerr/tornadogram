import logging

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from src import manager, utils


async def message_filters(message: Message) -> bool:
    if not message.outgoing:
        return False

    return True


class Dispatcher:
    def __init__(self, app: "manager.Manager") -> None:
        self.app = app

    async def load(self) -> None:
        logging.info("Loading dispatcher")
        self.app.app.add_handler(
            MessageHandler(self._message_handler),
            filters.all
        )

    async def _message_handler(self, app: Client, message: Message):
        prefix, command, args = utils.split_command(message.text or message.caption)
        if not self.app.commands.get(command):
            return
        command = self.app.commands.get(command)

        if not await message_filters(message):
            return

        await command(message)
