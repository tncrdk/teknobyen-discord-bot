from __future__ import annotations
from typing import Type
from result import Result, Err, Ok
from utils import Context, Command

commands: dict[str,
               Command]  # str: navnet på kommandoen , Callable: kommandoen

KEYWORD_ARGUMENT_SPECIFIER = "--"
FLAG_SPECIFIER = "-"


def parse_command(
    raw_command_str: str,
    context: Context,
    commands: dict[str, Type[Command]],
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

    command = command_type(positional_arguments, flags, keyword_arguments,
                           context)
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
