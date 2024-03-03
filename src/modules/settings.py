from pyrogram.types import Message

from src import modloader
from src.types import LANGS_STRS


router = modloader.Router("settings", author="tornadogram")


@router.module()
class Settings(modloader.Module):
    def __init__(self) -> None:
        self.config = modloader.Config(
            modloader.ConfigValue(
                "use_bot", True, "using bot?", modloader.validators.Boolean()
            )
        )

    @router.command(is_global=True)
    async def set_prefix(self, message: Message, args: str):
        if not args:
            await message.edit(self.shortcut("no_args"))
            return

        prefix = args[0]
        self.db.set("general", "prefix", prefix)
        await message.edit(f"Prefix successfully changed to {prefix}")

    @router.command(is_global=True)
    async def set_lang(self, message: Message, args: str):
        if not args:
            await message.edit(self.shortcut("no_args"))
            return

        lang = args
        if lang not in LANGS_STRS:
            await message.edit("Invalid language!")
            return

        self.db.set("general", "lang", lang)
        await message.edit(f"Language successfully changed to {lang}")
