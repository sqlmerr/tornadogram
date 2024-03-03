from pyrogram.types import Message

from src import modloader


router = modloader.Router("config", author="tornadogram")


@router.module("rawconfig")
class RawConfig(modloader.Module):
    strings = {
        "incorrect_args": "<emoji id=5210952531676504517>❌</emoji> <b>Incorrect args!</b>"
    }

    strings_ru = {
        "incorrect_args": "<emoji id=5210952531676504517>❌</emoji> <b>Неправильные аргументы!</b>"
    }

    @router.command()
    async def rset(self, message: Message, args: str = ""):
        if not args:
            await message.edit(self.shortcut("no_args"))
            return
        args = args.split(maxsplit=2)
        if len(args) < 3:
            await message.edit(self.strings("incorrect_args"))
            return

        module, option, value = args
        module = self.manager.modloader.find_module(module)
        if not module:
            await message.edit(self.shortcut("not_found").format("Module"))
            return

        try:
            module.config[option] = value
            module.set("__config__", module.config)
            await message.edit(self.shortcut("successfully"))
        except Exception as e:
            await message.edit(self.shortcut("error").format(e))
