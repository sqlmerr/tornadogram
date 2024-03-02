import logging
import os
import sys

from importlib.util import spec_from_file_location, module_from_spec

from types import FunctionType
from typing import Optional, Dict, List
from src import manager, db, utils

from pyrogram import Client


async def example_cmd(msg):
    await msg.edit("Hi")

class Module:
    _name: str
    author: str
    version: str
    router: "Router"
    db: "db.Database"
    manager: "manager.Manager"
    strings: utils.Strings

    @property
    def name(self) -> str:
        return self._name if self._name != (None,) else self.router.name

    async def on_load(self, app: Client):
        logging.info(
            f"Module {self.name if self.name != (None,) else self.router.name} loaded"
        )


class Router:
    def __init__(
        self, name: str, version: Optional[str] = None, author: Optional[str] = None
    ) -> None:
        self.name = name.lower()
        self.version = version
        self.author = author
        self.modules: List[Module] = []

    def module(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        author: Optional[str] = None,
    ):
        def decorator(instance: Module):
            if not issubclass(instance, Module):
                logging.warning(
                    f"module {name} of router {self.name} isn't subclass of `modloader.Module`"
                )
                return instance

            instance._name = (name,)
            instance.version = version
            instance.author = author
            instance.router = self
            self.modules.append(instance)
            return instance

        return decorator

    def command(self, doc: Optional[str] = None, is_global: bool = False):
        def decorator(func: FunctionType):
            if doc:
                func.__doc__ = doc
            func.is_command = True
            func.is_global = is_global

            return func

        return decorator

    def watcher(self):
        def decorator(func: FunctionType):
            func.is_watcher = True

            return func

        return decorator


def get_commands(module: Module) -> Dict[str, FunctionType]:
    return {
        method.lower(): getattr(module, method)
        for method in dir(module)
        if (
            callable(getattr(module, method))
            and getattr(getattr(module, method), "is_command", False) is True
        )
    }

def get_watchers(module: Module) -> List[FunctionType]:
    return [
        getattr(module, method)
        for method in dir(module)
        if (
            callable(getattr(module, method))
            and getattr(getattr(module, method), "is_watcher", False) is True
        )
    ]


class Loader:
    def __init__(self, app: "manager.Manager"):
        self.manager = app
        
        self.routers: List[Router] = []
        self.commands: dict = {"global": {"example": example_cmd}}
        self.watchers: list = []

    async def load_modules(self):
        self.routers = self.find_all_routers()
        for router_index, router in enumerate(self.routers):
            commands = await self.load_router(router)
            self.routers[router_index] = router
            self.commands[router.name] = commands

    def find_all_routers(self):
        routers = []
        for mod in filter(
            lambda filename: filename.endswith(".py") and not filename.startswith("_"),
            os.listdir("src/modules/"),
        ):
            module_name = mod[:-3]
            module_path = os.path.join(os.path.abspath("."), "src/modules", mod)

            spec = spec_from_file_location(module_name, module_path)
            module = module_from_spec(spec)
            sys.modules[module.__name__] = module
            spec.loader.exec_module(module)

            if hasattr(module, "router"):
                routers.append(getattr(module, "router"))

        return routers

    async def load_router(self, router: Router) -> Dict[str, FunctionType]:
        commands = {}
        for index, module in enumerate(router.modules):
            module.db = self.manager.db
            module.app = self.manager.app
            module.manager = self.manager

            strings = utils.Strings(
                module, self.manager.db.get("general", "lang", "en")
            )
            module = module()
            module.strings = strings
            router.modules[index] = module
            for cmd, func in get_commands(module).items():
                if getattr(func, "is_global", False) is True:
                    self.commands["global"][cmd] = func
                commands[cmd] = func
            self.watchers.extend(get_watchers(module))

            await module.on_load(self.manager.app)

        return commands
