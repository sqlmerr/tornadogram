from pyrogram.types import Message

from src import modloader


router = modloader.Router("help", author="tornadogram")


@router.module()
class Help(modloader.Module):
    @router.command(is_global=True)
    async def help(self, message: Message): ...
