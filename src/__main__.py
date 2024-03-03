import asyncio
import logging
import configparser
from typing import Tuple

from pyrogram import Client
from pyrogram import idle

from src.manager import Manager


def get_credentials() -> Tuple[int, str, configparser.ConfigParser]:
    config = configparser.ConfigParser()
    if not config.read("settings.ini"):
        config["credentials"] = {
            "api_id": input("Enter api id: "),
            "api_hash": input("Enter api hash: "),
        }
        config["bot"] = {"token": None}

        with open("settings.ini", "w") as f:
            config.write(f)

    return (
        int(config["credentials"]["api_id"]),
        config["credentials"]["api_hash"],
        config,
    )


async def main():
    logging.basicConfig(level=logging.INFO)  # for development and debug
    api_id, api_hash, config = get_credentials()
    app = Client("../tornadogram", api_id, api_hash)
    manager = Manager(app, config)

    print(
        """
  _                        _                          
 | |_ ___ _ _ _ _  __ _ __| |___  __ _ _ _ __ _ _ __  
 |  _/ _ \ '_| ' \/ _` / _` / _ \/ _` | '_/ _` | '  \ 
  \__\___/_| |_||_\__,_\__,_\___/\__, |_| \__,_|_|_|_|
                                 |___/
    """
    )

    await manager.start()
    await idle()

    await manager.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
