import dill
import math
import random
from pathlib import Path
from typing import Optional, TypeVar, Generic
from result import Result, Err, Ok
from error import BaseError, create_error
from output import log_error

T = TypeVar("T")


class Database(Generic[T]):
    def __init__(self, database_file_path: Path, ID_path: Path) -> None:
        self.CONTACT_PERSON = "Thorbjørn Djupvik"
        if not database_file_path.is_file():
            database_file_path.touch()
        if not ID_path.is_file():
            ID_path.touch()

        self.file_path = database_file_path
        self.ID_path = ID_path
        data = self.load_data()
        if type(data) != dict:
            raise Exception(f"Data needs to be of type {dict} not {type(self.data)}")
        self.data = data

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

    def load_data(self) -> Optional[dict[int, T]]:
        with open(self.file_path, "rb") as db_file:
            try:
                return dill.load(db_file)
            except EOFError:
                self.data = {}
                self.save_data()
                return self.load_data()
            except Exception as err:
                log_error(err)

    def save_data(self) -> None:
        try:
            with open(self.file_path, "wb") as db_file:
                dill.dump(self.data, db_file)
        except Exception as err:
            log_error(err)

    def load_ID(self) -> Result[int, BaseError]:
        if Path.is_file(self.ID_path):
            try:
                with open(self.ID_path, "r+") as file:
                    ID_str = file.read().strip()

                if ID_str == "":
                    ID = 0
                elif not ID_str.isdigit():
                    return create_error(
                        f"Kan ikke generere sitat-ID. {ID_str} er ikke et heltall. Kontakt {self.CONTACT_PERSON}"
                    )
                else:
                    ID = int(ID_str)
                return Ok(ID)

            except Exception as err:
                return create_error(str(err))
        return create_error(f"Filen eksisterer ikke: {self.ID_path.absolute()}")

    def save_ID(self, ID: int) -> Result[None, BaseError]:
        try:
            with open(self.ID_path, "w") as file:
                file.write(str(ID))
        except Exception as err:
            return create_error(str(err))
        return Ok(None)

    def create_new_quote_ID(self) -> Result[int, BaseError]:
        """Genererer sitat-ID

        Returns:
            Result[int, str]: Ok(sitat-ID) | Err(Feilmelding)
        """
        match self.load_ID():
            case Ok(ID_value):
                ID = ID_value + 1
            case Err(err):
                return Err(err)

        match self.save_ID(ID):
            case Err(err):
                return Err(err)

        return Ok(ID)

    def get_random_element(self) -> Optional[T]:
        if len(self.data) == 0:
            return
        return random.choice(list(self.data.values()))
