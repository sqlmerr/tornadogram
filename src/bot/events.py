from aiogram.types import Message


class Events:
    async def message_handler(self, message: Message):
        await message.answer("hi")
