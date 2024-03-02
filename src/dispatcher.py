import logging
import inspect

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from src import manager, utils


async def message_filters(
    app: Client, message: Message, _manager: "manager.Manager"
) -> bool:
    if message.chat.id == _manager.me.id or message.outgoing:
        return True

    return False


class Dispatcher:
    def __init__(self, app: "manager.Manager") -> None:
        self.manager = app

    async def load(self) -> None:
        logging.info("Loading dispatcher")
        self.manager.app.add_handler(MessageHandler(self._message_handler), filters.all)

    async def _message_handler(self, app: Client, message: Message):
        if not await message_filters(app, message, self.manager):
            return

        full_cmd = utils.split_command(
            message.text or message.caption,
            self.manager.db.get("general", "prefix", "."),
        )
        if len(full_cmd) == 3:
            prefix, command, args = full_cmd
            command = self.manager.commands["global"].get(command)
        else:
            prefix, router, command, args = full_cmd
            command = self.manager.commands.get(router, {}).get(command)

        if not command:
            return

        fn_args = inspect.getfullargspec(command).args
        if "args" in fn_args:
            await command(message, args=args)
        else:
            await command(message)
