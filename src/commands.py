from __future__ import annotations
from typing import Type, Protocol, TypeAlias
from result import Result, Err, Ok
from dataclasses import dataclass
from parse_command import Tree, Value, Kwarg, Flags


class Command(Protocol):
    # Initialize command with arguments in __init__()

    def initialize_arguments(self, parse_tree: Tree) -> Result[str, str]:
        ...

    def invoke_command(self) -> None:
        ...

class Argument:
    def __init__(self, name: str, annotation: Type, default) -> None:
        self.name = name
        self.annotation = annotation
        if default is not None and type(default) != self.annotation:
            raise ValueError(f"Default kan ikke være {default}, med type {type(default)}. Den skal være av type {self.annotation}")
        self.default = default

