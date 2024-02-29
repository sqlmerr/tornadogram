from pyrogram.types import Message

from src import modloader


router = modloader.Router("tests", author="tornadogram")


@router.module()
class Tests(modloader.Module):
    @router.command(doc="ping", is_global=True)
    async def ping(self, message: Message):
        await message.edit("aaa")

    @router.command(doc="show tree of routers, modules and commands")
    async def tree(self, message: Message):
        prefix = await self.db.get("general.prefix", ".")
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

        await message.edit(tree)
