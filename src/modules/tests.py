import sys
import atexit
import time
import os

from pyrogram.types import Message

from src import modloader


router = modloader.Router("tests", author="tornadogram")


@router.module()
class Tests(modloader.Module):
    @router.command(doc="ping", is_global=True)
    async def ping(self, message: Message):
        start = time.perf_counter()
        await message.edit("<b>Pong!</b>")
        end = time.perf_counter()

        await message.edit(f"<b>Pong! {round(end - start, 2)}</b>")

    @router.command(doc="show tree of routers, modules and commands")
    async def tree(self, message: Message):
        prefix = self.db.get("general", "prefix", ".")
        tree = ""
        for _router in self.manager.routers:
            a = f"✨ <b>{_router.name}: </b>\n"
            a += "  <b>Modules: </b>\n"
            for module in _router.modules:
                a += f"    <b>{module.name}</b>"

            a += "\n  <b>Commands: </b>\n"
            for cmd in self.manager.commands[_router.name].keys():
                a += f"    <b>{prefix}{cmd}</b>"
            tree += a
            tree += "\n"

        await message.edit(tree)

    @router.command(is_global=True)
    async def restart(self, message: Message):
        def restart():
            os.execl(sys.executable, sys.executable, "-m", "src")

        await message.edit("restarting...")
        atexit.register(restart)

        return sys.exit(0)
