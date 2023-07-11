from __future__ import annotations
from typing import Optional, Callable, Type, TypeVar
from result import Result, Err, Ok
from dataclasses import dataclass
from .io import log_error

T = TypeVar("T")

KWARG_SPECIFIER = "--"
FLAG_SPECIFIER = "-"


"""
Grammar
    command =
        name { command | args }
    arguments =
        | arg { arguments }
        | kwarg { kwargs }
    arg =
        value | flags
    flags =
        '-'(char{chars})
    kwarg =
        '--'(key) { value }  # må sjekke hvert argument
    kwargs =
        kwarg { kwargs }
    name =
        char{ chars }
    value =
        | symbol{ symbols }
        | '(expr)'
    key =
        symbol{ symbols }
    symbol =
         char | int | _
"""


@dataclass
class Tree:
    """
    (Ex)
    Tree: leaves = [
            command: leaves = [
                value, value, flag, value, kwarg
            ]
    ]
    """

    leaves: list = []


class Kwarg(Tree):
    def __init__(self, leaves: list) -> None:
        if not (1 <= len(leaves) <= 2):
            err = ValueError(
                f"Kwarg med leaves: {leaves} er ikke gyldig. Leaves skal ha lengde innenfor [1, 2]"
            )
            log_error(err)
            raise err
        self.leaves = leaves


class Flag(Tree):
    def __init__(self, leaves: list) -> None:
        if not len(leaves) == 1:
            err = ValueError(
                f"Flag med leaves: {leaves} er ikke gyldig. Leaves skal ha lengde 1."
            )
            log_error(err)
            raise err
        self.leaves = leaves


class Value(Tree):
    def __init__(self, leaves: list) -> None:
        if not len(leaves) == 1:
            err = ValueError(
                f"Value med leaves: {leaves} er ikke gyldig. Leaves skal ha lengde 1."
            )
            log_error(err)
            raise err
        self.leaves = leaves


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


def value_parser(command_string: str) -> Result[tuple[Tree, str], str]:
    # TODO Denne funksjonen er for grov. Ta hensyn til "foo" i strengen
    next_quote = 0
    match command_string[0]:
        case "'":
            next_quote = command_string.find("'", 1)
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


def name_parser(command_string: str) -> tuple[Tree, str]:
    match command_string.split():
        case [head, *tail] if head.isalpha():
            return (Tree([head]), "".join(tail))
        case _:
            return (Tree(), command_string)


def kwarg_parser(command_string: str) -> tuple[Tree, str]:
    match command_string.split():
        case [first, second, *tail] if starts_with_keyword_specifier(first):
            possible_match = [first, second]
        case _:
            return (Tree(), command_string)

    match parse(name_parser, " ".join(possible_match)):
        case (Tree(leaves, ""), tail) if len(leaves) == 1:
            key = leaves[0]
        case _:
            return (Tree(), command_string)

    match parse(value_parser, tail):
        case (Tree(leaves, []), "") if len(leaves) == 1:
            value = leaves[0]
        case _:
            return (Tree(), command_string)

    return (Tree([key, value]), "")


def is_kwarg(arg: str) -> bool:
    if arg[0:2] == KWARG_SPECIFIER:
        return True
    return False


def is_flags(arg: str) -> bool:
    if arg[0] == FLAG_SPECIFIER:
        return True
    return False


def get_value_between_indexes(
    string: str, first_quote_index: int, last_quote_index: int
) -> Result[str, str]:
    if first_quote_index > last_quote_index:
        return Err(f"Start: {first_quote_index} er større en end: {last_quote_index}")
    if len(string) <= last_quote_index:
        return Err(
            f"Strengen er ikke lang nok: length = {len(string)} | end = {last_quote_index}"
        )
    return Ok(string[first_quote_index + 1 : last_quote_index])


def get_next_quote_pair_indexes(string: str) -> Result[Optional[tuple[int, int]], str]:
    """
    Antar første " er ved indeks 0
    """
    second_quote_index = 0
    first_quote_index = 0

    match string[0]:
        case "'":
            quote_type = "'"
            second_quote_index = string.find("'", 1)
        case '"':
            quote_type = '"'
            second_quote_index = string.find('"', 1)
        case _:
            return Ok(None)

    match second_quote_index:
        case -1:
            return Err(f"Fant ( {quote_type} ), som ikke var lukket")
        case _:
            return Ok((first_quote_index, second_quote_index))
