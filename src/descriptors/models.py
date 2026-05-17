from typing import Any, TypeAlias
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JSON: TypeAlias = dict[str, Any]


class Model:
    def __init__(self, payload: JSON):
        self.payload = payload


class Field:
    def __init__(self, path: str) -> None:
        if not path:
            raise ValueError("Empty path")
        self.keys = path.split(".")

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, obj, owner=None):
        payload = getattr(obj, "payload")
        if len(self.keys) == 1:
            val = payload[self.keys[0]]
            return val
        current_val = payload
        for key in self.keys[:-1]:
            current_val = current_val.get(key)
        if current_val:
            return current_val[self.keys[-1]]
        else:
            return None

    def __set__(self, obj, value):
        payload = getattr(obj, "payload")
        current_val: dict = payload
        for key in self.keys[:-1]:
            current_val = current_val.setdefault(key, dict())
        current_val[self.keys[-1]] = value
        setattr(obj, self.private_name, value)
