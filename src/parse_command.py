from __future__ import annotations
from typing import Type, Protocol
from result import Result, Err, Ok


KEYWORD_ARGUMENT_SPECIFIER = "--"
FLAG_SPECIFIER = "-"


"""
name: str:bokstaver
value: str

Grammar:
    command: name | name + command | name + args
    args: fvarg | fkwargs | fvarg args
    fvarg: value | flag
    fkwargs: fkwarg | fkwarg fkwargs
    fkwarg: flag | kwarg
    kwarg: --name value
    flag: --name | -name
"""


class Context:
    pass


class Command(Protocol):
    name: str
    arguments: list[str]
    subcommands: list[Command]
    flag_options: list[str]
    kwarg_options: list[str]

    def __init__(self) -> None:
        ...

    def invoke_command(
        self,
        positional_arguments: list[str],
        flags: list[str],
        kwargs: list[tuple[str, str]],
        context: Context,
    ) -> Result[str, str]:
        ...

    def validate(self) -> Result[None, str]:
        ...


def parse_command(
    raw_command_str: str,
    context: Context,
    commands: list[Command],
) -> Result[str, str]:
    command_str, *raw_arguments = raw_command_str.split(" ")
    command_type = commands.get(command_str)
    if command_type is None:
        return Err("Kommandoen eksisterer ikke")

    i = 0
    positional_arguments = []
    keyword_arguments = []
    flags = []
    while i < len(raw_arguments):
        arg = raw_arguments[i]
        if is_kwarg(arg):
            keyword_arguments.append((arg[2:], raw_arguments[i + 1]))
            i += 2
        elif is_flag(arg):
            flags.append(arg[1:])
            i += 1
        else:
            positional_arguments.append(arg)
            i += 1

    command = command_type(positional_arguments, flags, keyword_arguments, context)
    match command.validate():
        case Err(str):
            return Err(str)
        case Ok():
            return command.invoke_command()


def is_kwarg(arg: str) -> bool:
    if arg[0:2] == KEYWORD_ARGUMENT_SPECIFIER:
        return True
    return False


def is_flag(arg: str) -> bool:
    if arg[0] == FLAG_SPECIFIER:
        return True
    return False
