from enum import Enum
from result import Err
from dataclasses import dataclass


class ErrorLevel(Enum):
    ERROR = 0
    WARNING = 1


@dataclass
class BaseError:
    msg: str
    level: ErrorLevel = ErrorLevel.ERROR


class FormatError(BaseError):
    pass


class DatabaseError(BaseError):
    pass

class DuplicateQuoteError(BaseError):
    pass


def create_error(msg: str) -> Err[BaseError]:
    return Err(BaseError(msg))

def create_warning(msg: str) -> Err[BaseError]:
    return Err(BaseError(msg, ErrorLevel.WARNING))
