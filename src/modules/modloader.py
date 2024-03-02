import tempfile

from pyrogram.types import Message

from src import modloader


router = modloader.Router("modloader")


@router.module()
class Modloader(modloader.Module):
    strings = {
        "no_document": "<emoji id=5240241223632954241>🚫</emoji> <b>No document!</b>",
        "encoding": "Incorrect file encoding",
        "success": "<emoji id=5206607081334906820>✔️</emoji> <b>Module successfully loaded</b>"
    }
    strings_ru = {
        "no_document": "<emoji id=5240241223632954241>🚫</emoji> <b>Нет документа!</b>",
        "encoding": "Неверная кодировка файла",
        "success": "<emoji id=5206607081334906820>✔️</emoji> <b>Модуль успешно загружен</b>"
    }

    @router.command(is_global=True)
    async def loadmod(self, message: Message):
        reply = message.reply_to_message
        
        if not reply:
            await message.edit(self.shortcut("no_shortcut"))
            return
        
        if not reply.document:
            await message.edit(self.strings("no_document"))
            return
        
        temp_file = tempfile.NamedTemporaryFile("w")
        await reply.download(temp_file.name)
        
        try:
            with open(temp_file.name, "r", encoding="utf-8") as f:
                source = f.read()
        except UnicodeDecodeError:
            temp_file.close()
            await message.edit(self.shortcut("error").format(self.strings("encoding")))
        
        is_loaded, name = await self.manager.modloader.load_third_party_module(source)
        if is_loaded:
            with open(f"src/modules/_{name}.py", "w") as f:
                f.write(source)
            
            await message.edit(self.strings("success"))
        else:
            await message.edit(self.shortcut("error").format("Module not loaded"))

        temp_file.close()
