from pathlib import Path
from typing import Optional, TypeVar, Generic
import dill

from quote import Quote

T = TypeVar("T")


class Database(Generic[T]):
    def __init__(self, file_path: Path) -> None:
        if not file_path.is_file():
            raise FileNotFoundError(f"Finner ikke filen: {file_path}")
        self.file_path = file_path
        self.data = self.load_data()
        if type(self.data) != dict:
            raise Exception(f"Data needs to be of type {dict} not {type(self.data)}")

    def set_value(self, key: int, value: T) -> None:
        self.data[key] = value
        self.save_data()

    def get(self, key: int) -> Optional[T]:
        return self.data.get(key)

    def items(self) -> list[tuple[int, T]]:
        return [item for item in self.data.items()]

    def values(self) -> list[T]:
        return [value for value in self.data.values()]

    def keys(self) -> list[int]:
        return [key for key in self.data.keys()]

    def pop(self, key: int) -> T:
        value = self.data.pop(key)
        self.save_data()
        return value

    def load_data(self) -> dict[int, T]:
        with open(self.file_path, "rb") as db_file:
            try:
                return dill.load(db_file)
            except EOFError:
                self.data = {}
                self.save_data()
                return self.load_data()

    def save_data(self) -> None:
        with open(self.file_path, "wb") as db_file:
            dill.dump(self.data, db_file)

