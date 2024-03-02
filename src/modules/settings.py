from pyrogram.types import Message

from src import modloader


router = modloader.Router("settings")


@router.module()
class Settings(modloader.Module):
    @router.command(is_global=True)
    async def set_prefix(self, message: Message, args: str):
        if not args:
            await message.edit("No args!")
            return
        
        prefix = args[0]
        self.db.set(
            "general", "prefix", prefix
        )
        await message.edit(f"Prefix successfully changed to {prefix}")