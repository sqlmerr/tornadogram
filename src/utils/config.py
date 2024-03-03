from contextlib import suppress
from typing import Union, Any

from dataclasses import dataclass
from . import validators


class Config(dict):
    def __init__(self, *values: "ConfigValue"):
        self.values = {value.name: value for value in values}
        super().__init__()

    def __setitem__(self, option: str, value: Any) -> None:
        self.values[option].value = self.values[option].validator.validate(str(value))
        super().__setitem__(option, value)

    def __getitem__(self, option: str) -> None:
        with suppress(KeyError):
            return self.values[option].value

    def load(self):
        for name, value in self.values.items():
            self[name] = value.value


@dataclass
class ConfigValue:
    name: str
    value: Union[str, int, float, bool]
    description: str
    validator: validators.Validator
