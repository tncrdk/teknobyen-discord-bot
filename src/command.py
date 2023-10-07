from __future__ import annotations
import discord
import parse_command as pc
from abc import ABC
from typing import Any, Generic, Optional, Type, Protocol, TypeAlias, TypeVar
from result import Result, Err, Ok
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class Command(ABC):
    subcommands: list[Command]
    pos_args: list[PositionalArgument]
    flags: dict[str, FlagArgument]
    kwargs: dict[str, KwargArgument]
    # Initialize command with arguments in __init__()

    def main(self, command_tree, context: Context):
        ...

    def invoke_command(self, parse_tree: pc.Tree, context: Context) -> Result[Any, str]:
        match self.initialize_arguments(parse_tree):
            case Err(err):
                return Err(err)
            case Ok(some):
                pass

    def initialize_arguments(self, parse_tree: pc.Tree) -> Result[str, str]:
        pass

    def create_help(self) -> None:
        pass


class Context:
    pass


class Argument(Generic[T]):
    def __init__(self, value_type: Type[T], default: Optional[T]) -> None:
        if default is not None and isinstance(default, value_type):
            raise ValueError(
                f"Default kan ikke være {default}, med type {type(default).__name__}. Den skal være av type {value_type}"
            )


class PositionalArgument(Argument, Generic[T]):
    def __init__(
        self, name: str, value_type: Type[T], description: str, default: Optional[T]
    ) -> None:
        super().__init__(value_type, default)
        self.name = name
        self.value_type = value_type
        self.description = description
        self.default = default


class FlagArgument(Argument, Generic[T]):
    def __init__(self, flag_name: str, description: str) -> None:
        self.flag_name = flag_name
        self.description = description


class KwargArgument(Argument, Generic[T]):
    def __init__(
        self, key: str, value_type: Type[T], description: str, default: Optional[T]
    ) -> None:
        super().__init__(value_type, default)
        self.key = key
        self.value_type = value_type
        self.description = description
        self.default = default
