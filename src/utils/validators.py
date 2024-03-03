from typing import Optional
from abc import ABC, abstractmethod


class ValidationError(Exception):
    msg: str


class Validator(ABC):
    @abstractmethod
    def validate(self, value: str) -> Optional[bool]:
        raise NotImplementedError


class Integer(Validator):
    def __init__(
        self, minimum: Optional[int] = None, maximum: Optional[int] = None
    ) -> None:
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value: str) -> Optional[int]:
        try:
            value = int(value.strip())
        except ValueError:
            raise ValidationError("Value must be integer!")

        if self.minimum and value < self.minimum:
            raise ValidationError(f"Integer value must be less than {self.minimum}")

        if self.maximum and value > self.maximum:
            raise ValidationError(f"Integer value must be greater than {self.maximum}")

        return value


class String(Validator):
    def __init__(
        self, min_len: Optional[int] = None, max_len: Optional[int] = None
    ) -> None:
        self.min_len = min_len
        self.max_len = max_len

    def validate(self, value: str) -> Optional[str]:
        if not isinstance(value, str):
            value = str(value)

        if self.min_len and len(value) < self.min_len:
            raise ValidationError(
                f"String value length must be less than {self.min_len}"
            )

        if self.max_len and len(value) > self.max_len:
            raise ValidationError(
                f"String value length must be greater than {self.max_len}"
            )

        return value


class Boolean(Validator):
    def validate(self, value: str) -> Optional[bool]:
        true = ["true", "t", "1", "yes", "y"]
        false = ["false", "f", "0", "no", "n"]
        value = value.lower()
        if not (value in true or value in false):
            raise ValidationError("Value must be valid boolean")

        if value in true:
            return True
        return False
