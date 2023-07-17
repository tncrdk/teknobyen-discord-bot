from __future__ import annotations
from typing import Optional, Callable, TypeVar
from result import Result, Err, Ok
from dataclasses import dataclass

T = TypeVar("T")

KEY_SPECIFIER = "--"
FLAG_SPECIFIER = "-"


"""
Grammar
    command =
        name { command | args }  # Må se forskjell på rekursiv command-navn eller argument
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
        char{ symbols }
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

    leaves: Optional[list[str | Tree]] = None


class Kwarg(Tree):
    pass


class Flag(Tree):
    pass


class Value(Tree):
    pass


def parse(
    parser: Callable[[str], Result[tuple[Tree, str], str]], parse_string: str, *args
) -> Result[tuple[Tree, str], str]:
    """
    @param:
        parser: (parse-string) -> Result[ (Tree, parse-string tail) ]

    @returns:
        Result[ (Tree, parse_string tail) ]
    """
    parse_string = parse_string.strip()
    return parser(parse_string, *args)


def command_parser(command_string: str, subcommands: list[str]):
    pass


def value_parser(command_string: str) -> Result[tuple[Tree, str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Tree:Value { Optional [value] }, tail)

    value =
        | symbol{ symbols }
        | '(expr)'
    symbol = char | int | _
    """
    match check_if_value_surrounded_by_quotes(command_string):
        case Err(err):
            return Err(err)
        case Ok(result) if result is not None:
            content, _, second_index = result
            tree = Value([content])
            tail = command_string[second_index + 1 :]
            return Ok((tree, tail))

    if is_flags(command_string) or is_key(command_string):
        return Ok((Value(), command_string))

    match command_string.find(" "):
        case -1:
            return Ok((Value([command_string]), ""))
        case index:
            content = command_string[:index]
            tail = command_string[index + 1 :]

    if not is_symbol(content):
        return Ok((Value(), command_string))

    return Ok((Value([content]), tail))


def name_parser(command_string: str) -> Result[tuple[Tree, str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Tree { Optional [name] }, tail)

    name = char{ symbols }
    symbol = char | int | _
    """
    match command_string.find(" "):
        case -1:
            name = command_string
            tail = ""
        case index:
            name = command_string[:index]
            tail = command_string[index + 1 :]

    if is_symbol(name) and name[0].isalpha():
        return Ok((Tree([name]), tail))

    return Ok((Tree(), command_string))


def key_parser(command_string: str) -> Result[tuple[Tree, str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Tree { Optional [key] }, tail)

    key = symbol{ symbols }
    symbol = char | int | _
    """
    match command_string.find(" "):
        case -1:
            raw_key = command_string
            tail = ""
        case index:
            raw_key = command_string[:index]
            tail = command_string[index + 1 :]

    key = raw_key[len(KEY_SPECIFIER):]

    if is_symbol(key) and is_key(raw_key):
        return Ok((Tree([key]), tail))

    return Ok((Tree(), command_string))




def kwarg_parser(command_string: str) -> Result[tuple[Tree, str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Tree:Kwarg { Optional [key {Optional value}] }, tail)

    kwarg = '--'(key) { value }
    name = char{ symbols }
    symbol = char | int | _
    """
    match parse(key_parser, command_string):
        case Ok((Tree(content), tail)):
            if content is None:
                return Ok((Kwarg(), command_string))
            key = content[0]
        case other:
            return other

    match parse(value_parser, tail):
        case Ok((Value(content), updated_tail)):
            if content is None:
                return Ok((Kwarg([key]), tail))
            elif len(content) != 1:
                return Err("Len(value) != 1")
            value = content[0]
            tail= updated_tail
        case other:
            return other

    return Ok((Kwarg([key, value]), tail))


def flags_parser(command_string: str) -> Result[tuple[Tree, str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Tree:Kwarg { Optional [key {Optional value}] }, tail)

    flags = '-'(char{chars})
    """
    pass


def is_key(arg: str) -> bool:
    if arg[0:2] == KEY_SPECIFIER:
        return True
    return False


def is_flags(arg: str) -> bool:
    if arg[0] == FLAG_SPECIFIER:
        return True
    return False

def is_symbol(string: str) -> bool:
    # Sjekker om navnet bare består av alfanumeriske tegn + _
    if string.replace("-", "").isalnum():
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


def get_quote_pair_indexes(string: str) -> Result[Optional[tuple[int, int]], str]:
    """
    @param
        string: strengen som skal søkes i

    @return
        Result[Optional[tuple[int, int]], str]: Optional (first_index, second_index) | Err
    """
    first_quote_index = 0
    second_quote_index = 0

    first_single_quote_index = string.find("'")
    first_double_quote_index = string.find('"')

    match (first_single_quote_index, first_double_quote_index):
        case (-1, -1):
            return Ok(None)
        case (-1, index):
            first_quote_index = index
            quote_type = '"'
        case (index, -1):
            first_quote_index = index
            quote_type = "'"
        case (single_quote_index, double_quote_index):
            if single_quote_index > double_quote_index:
                first_quote_index = single_quote_index
                quote_type = "'"
            else:
                first_quote_index = double_quote_index
                quote_type = '"'

    match string.find(quote_type, first_quote_index + 1):
        case -1:
            return Err(f"Fant ( {quote_type} ), som ikke var lukket")
        case index:
            second_quote_index = index

    return Ok((first_quote_index, second_quote_index))


def check_if_value_surrounded_by_quotes(
    string: str,
) -> Result[Optional[tuple[str, int, int]], str]:
    """
    @returns
        Result {Optional (content, 0, second_quote_index) }
    """
    if string[0] == "'" or string[0] == '"':
        match get_quote_pair_indexes(string):
            case Err(err):
                return Err(err)
            case Ok((first_index, second_index)):
                pass
            case _:
                return Ok(None)

        match get_value_between_indexes(string, first_index, second_index):
            case Ok(content):
                return Ok((content, first_index, second_index))
            case other:
                return other

    return Ok(None)
