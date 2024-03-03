import yaml

from typing import Any

from src.types import LANGS


class Strings:
    def __init__(self, module, lang: LANGS) -> None:
        self.module = module
        self.lang = lang

    def __call__(self, name: str) -> Any:
        strings = getattr(
            self.module, f"strings_{self.lang}" if self.lang != "en" else "strings"
        )
        if not strings or not isinstance(strings, dict):
            return "not found"

        return strings.get(name, "not found")


def shortcut(name: str, lang: LANGS) -> str:
    with open("src/locals/shortcuts.yaml") as stream:
        try:
            shortcuts = yaml.safe_load(stream)
        except yaml.YAMLError:
            return "error"

    try:
        return shortcuts[lang][name]
    except KeyError:
        return "error"
