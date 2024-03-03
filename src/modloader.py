import logging
import os
import random
import sys

from importlib.util import spec_from_file_location, module_from_spec
from importlib.abc import SourceLoader
from importlib.machinery import ModuleSpec

from types import FunctionType, LambdaType
from typing import Any, Optional, Dict, List
from src import manager, db, utils
from src.types import JSON
from src.utils import ConfigValue, validators, Config

from pyrogram import Client


__all__ = ("ConfigValue", "validators", "Config")


async def example_cmd(msg):
    await msg.edit("Hi")


class Module:
    _name: str
    author: str
    version: str
    router: "Router"
    db: "db.Database"
    app: Client
    manager: "manager.Manager"
    strings: utils.Strings
    shortcut: LambdaType
    config: Optional[Config] = None

    @property
    def name(self) -> str:
        return self._name if self._name is not None else self.router.name

    async def on_load(self, app: Client):
        logging.info(f"Module {self.name} loaded")

    def set(self, key: str, value: JSON):
        return self.db.set(f"modules.{self.name}", key, value)

    def get(self, key: str, default: JSON = None):
        return self.db.get(f"modules.{self.name}", key, default)


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

            instance._name = name
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


class StringLoader(SourceLoader):
    """Загружает модуль со строки"""

    def __init__(self, data: str, origin: str) -> None:
        self.data = data.encode("utf-8")
        self.origin = origin

    def get_code(self, full_name: str) -> Optional[Any]:
        source = self.get_source(full_name)
        if not source:
            return None

        return compile(source, self.origin, "exec", dont_inherit=True)

    def get_filename(self, _: str) -> str:
        return self.origin

    def get_data(self, _: str) -> str:
        return self.data


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
            lambda filename: filename.endswith(".py"),
            os.listdir("src/modules/"),
        ):
            module_name = mod[:-3]
            module_path = os.path.join(os.path.abspath("."), "src/modules", mod)

            router = self.register_module(module_name, module_path)
            if isinstance(router, Router):
                routers.append(router)

        return routers

    def register_module(
        self, name: str, path: str = "", spec: Optional[ModuleSpec] = None
    ) -> Router:
        spec = spec or spec_from_file_location(name, path)
        module = module_from_spec(spec)
        sys.modules[module.__name__] = module
        spec.loader.exec_module(module)

        if hasattr(module, "router"):
            return getattr(module, "router")

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
            self.load_config(module)
            module.strings = strings
            module.shortcut = lambda name: utils.shortcut(
                name, self.manager.db.get("general", "lang", "en")
            )
            router.modules[index] = module
            for cmd, func in get_commands(module).items():
                if getattr(func, "is_global", False) is True:
                    self.commands["global"][cmd] = func
                commands[cmd] = func
            self.watchers.extend(get_watchers(module))

            await module.on_load(self.manager.app)

        return commands

    async def load_third_party_module(
        self, source: str, origin: str = "<string>"
    ) -> bool:
        module_name = f"tornadogram.modules.{random.randint(1, 99999)}"

        try:
            spec = ModuleSpec(module_name, StringLoader(source, origin), origin=origin)

            router = self.register_module(module_name, spec=spec)
            commands = await self.load_router(router)
            self.routers.append(router)
            self.commands[router.name] = commands
        except Exception as e:
            return logging.exception(e)

        return True, router.name

    def find_module(self, module_name: str):
        for router in self.routers:
            for module in router.modules:
                if module.name.strip().lower() == module_name.strip().lower():
                    return module

    def load_config(self, module: Module):
        if module.config is None:
            return

        if module.get("__config__") is None:
            module.config.load()
            module.set("__config__", module.config)
            return

        module.config.update(module.get("__config__", {}))

    def save_config(self):
        for router in self.routers:
            for module in router.modules:
                if module.config is None:
                    continue

                module.set("__config__", module.config)
