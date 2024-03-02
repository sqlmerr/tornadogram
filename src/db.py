import json

from pathlib import Path
from typing import Any, Dict
from src.types import JSON


class Database(dict):
    def __init__(self, location: str = "db.json"):
        super().__init__()
        self.location = Path(location)

        self.update(**self.load(self.location))

    def load(self, location: Path) -> Dict[str, Any]:
        if not location.exists():
            return {}

        with location.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self) -> None:
        with self.location.open("w", encoding="utf-8") as file:
            json.dump(self, file, ensure_ascii=True, indent=4)

    def get(self, path: str, key: str, defaut: JSON = None):
        try:
            return self[path][key]
        except KeyError:
            self.set(path, key, defaut)
            return defaut

    def set(self, path: str, key: str, value: JSON = None):
        self.setdefault(path, {})[key] = value
        return self.save()
