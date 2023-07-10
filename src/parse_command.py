from __future__ import annotations
from typing import Optional, Callable, TypeVar
from result import Result, Err, Ok
from dataclasses import dataclass

T = TypeVar("T")

KEYWORD_SPECIFIER = "--"
IFLAG_SPECIFIER = "-"


"""
Grammar:
    command =
        name {command | args}
    args = 
        [value | flag | i-flags] {args}
        | kwarg {fkwargs}
    i-flags =
        '-'(flag_letter {i-flags})
    flag =
        '--'(name)
    fkwargs =
        [flag | i-flags | kwarg] {fkwargs}
    kwarg =
        '--'(name) value
    kwargs =
        kwarg {kwargs}
    name =
        alphanumeric string
    value = 
        {'}Any{'}

Grammar
    command =
        name { command| args }
    args =
        arg { args }
    arg =
        value | kwarg | flags
    flags =
        '-'(char{chars})
    kwarg =
        '--'key { value }  # må sjekke hvert argument
"""


class Context:
    pass


@dataclass
class Tree:
    leaves: list = []
    subtrees: list[Tree] = []


def parse(
    parser: Callable[[str], Result[tuple[Tree, str], str]],
    parse_string: str,
) -> Result[tuple[Tree, str], str]:
    """
    @param:
        parser: (parse-string) -> Result[ (Tree, parse-string tail) ]

    @returns:
        Result[ (Tree, parse_string tail) ]
    """
    parse_string = parse_string.strip()
    return parser(parse_string)


def value_expr(command_string: str) -> Result[tuple[Tree, str], str]:
    # TODO Denne funksjonen er for grov. Ta hensyn til "foo" i strengen
    command_string = command_string.strip()
    next_quote = 0
    match command_string[0]:
        case "'":
            next_quote = command_string.find("''", 1)
        case '"':
            next_quote = command_string.find('"', 1)
    if next_quote == -1:
        return Err("Fant '' som ikke var lukket")
    if next_quote != 0:
        return Ok(
            (Tree([command_string[1:next_quote], []]), command_string[next_quote + 1 :])
        )

    match command_string.split():
        case "":
            return (Tree(), command_string)
        case [head, *tail]:
            return (Tree([head]), tail)
    return (Tree(), "")


def name_expr(command_string: str) -> tuple[Tree, str]:
    match command_string.split():
        case [head, *tail] if head.isalpha():
            return (Tree([head]), "".join(tail))
        case _:
            return (Tree(), command_string)


def kwarg_expr(command_string: str) -> tuple[Tree, str]:
    match command_string.split():
        case [first, second, *tail] if starts_with_keyword_specifier(first):
            possible_match = [first, second]
        case _:
            return (Tree(), command_string)

    match parse(name_expr, " ".join(possible_match)):
        case (Tree(leaves, ""), tail) if len(leaves) == 1:
            key = leaves[0]
        case _:
            return (Tree(), command_string)

    match parse(value_expr, tail):
        case (Tree(leaves, []), "") if len(leaves) == 1:
            value = leaves[0]
        case _:
            return (Tree(), command_string)

    return (Tree([key, value]), "")


# class Command(Protocol):
#     name: str
#     arguments: list[str]
#     subcommands: list[Command]
#     flag_options: list[str]
#     kwarg_options: list[str]
#
#     def __init__(self) -> None:
#         ...
#
#     def invoke_command(
#         self,
#         positional_arguments: list[str],
#         flags: list[str],
#         kwargs: list[tuple[str, str]],
#         context: Context,
#     ) -> Result[str, str]:
#         ...
#
#     def validate(self) -> Result[None, str]:
#         ...


# def parse_command(
#     raw_command_str: str,
#     context: Context,
#     commands: list[Command],
# ) -> Result[str, str]:
#     command_str, *raw_arguments = raw_command_str.split(" ")
#     command_type = commands.get(command_str)
#     if command_type is None:
#         return Err("Kommandoen eksisterer ikke")
#
#     i = 0
#     positional_arguments = []
#     keyword_arguments = []
#     flags = []
#     while i < len(raw_arguments):
#         arg = raw_arguments[i]
#         if is_kwarg(arg):
#             keyword_arguments.append((arg[2:], raw_arguments[i + 1]))
#             i += 2
#         elif is_flag(arg):
#             flags.append(arg[1:])
#             i += 1
#         else:
#             positional_arguments.append(arg)
#             i += 1
#
#     command = command_type(positional_arguments, flags, keyword_arguments, context)
#     match command.validate():
#         case Err(str):
#             return Err(str)
#         case Ok():
#             return command.invoke_command()
#
#
def starts_with_keyword_specifier(arg: str) -> bool:
    if arg[0:2] == KEYWORD_SPECIFIER:
        return True
    return False


#
#
# def is_flag(arg: str) -> bool:
#     if arg[0] == FLAG_SPECIFIER:
#         return True
#     return False
