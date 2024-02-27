import asyncio
import logging

from pyrogram import Client, filters
from pyrogram import idle

from src.manager import Manager


async def main():
    logging.basicConfig(level=logging.INFO) # for development and debug
    app = Client("../tornadogram", 28624580, "0d42a048f01d160ec0750b222434d2ab")
    manager = Manager(app)

    await manager.start()
    await idle()


if __name__ == '__main__':
    asyncio.run(main())
