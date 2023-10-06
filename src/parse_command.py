from __future__ import annotations
from typing import Iterable, Optional, Callable
from result import Result, Err, Ok
from dataclasses import dataclass
from textwrap import indent


KEY_SPECIFIER = "--"
FLAG_SPECIFIER = "-"


"""
Grammar
    command =
        name { args } { kwargs }
        # En subkommando blir lagt inn som argument, tolket som value, og blir håndtert i kommando-funksjonen
    arg =
        value | flags
    flags =
        '-'(char{chars})
    kwarg =
        key { value }  # må sjekke hvert argument
    name =
        char{ symbols }
    value =
        | symbol{ symbols }
        | expr
    expr =
        '(characters)'
    key =
        '--'(symbol){ symbols }
    symbol =
         char | int | _
"""


@dataclass
class Tree:
    """
    Abstrakt syntakstre for parseren

    @attrs
    root: str
    leaves: Optional[list[Tree]]

    @Example
    Tree {
            root: str
            leaves: [
                Value, Value, Flag, Falue, Kwarg
            ]
        }
    """

    root: str
    leaves: Optional[list[Tree]] = None

    def add_subtree(self, tree: Tree) -> None:
        """
        Legger til et subtre til @self ved mutasjon

        @params
        tree: Tree

        @returns
        None
        """
        if self.leaves is None:
            self.leaves = [tree]
        else:
            self.leaves.append(tree)

    def add_subtrees(self, trees: Iterable[Tree]) -> None:
        """
        Legger til flere subtrær til @self ved mutasjon

        @params
        trees: Iterable[Tree]

        @returns
        None
        """
        for tree in trees:
            self.add_subtree(tree)

    def __str__(self) -> str:
        string = f"{type(self).__name__}: {self.root}"
        if self.leaves is None:
            return string
        string += " {\n"
        for subtree in self.leaves:
            string += indent(str(subtree), " " * 4) + "\n"
        string += "}"
        return string


class Command(Tree):
    pass


class Kwarg(Tree):
    pass


class Flag(Tree):
    pass


class Value(Tree):
    pass


class Expr(Tree):
    pass


def parse(
    parser: Callable[[str], Result[tuple[Optional[Tree], str], str]],
    parse_string: str,
) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param:
        parser: (parse-string) -> Result (Optional Tree, tail)
        parse_string: str

    @returns:
        Result[ (Tree, parse_string tail) ]
    """
    parse_string = parse_string.strip()
    if len(parse_string) == 0:
        return Ok((None, ""))
    return parser(parse_string)


def exhaust_parser(
    parser: Callable[[str], Result[tuple[Optional[Tree], str], str]],
    parse_string: str,
) -> Result[tuple[list[Tree], str], str]:
    """
    @param:
        parser: (parse-string) -> Result (Optional Tree, tail)
        parse_string: str

    @returns:
        Result ([Tree], tail)
    """
    tree_list = []
    while True:
        match parse(parser, parse_string):
            case Err(err):
                return Err(err)
            case Ok((None, _)):
                parse_tail = parse_string
                break
            case Ok((tree, tail)):
                tree_list.append(tree)
                parse_string = tail

    return Ok((tree_list, parse_tail))


def command_parser(string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree { command_name, Optional [args] }, tail)

    @grammar
        command = name { arguments } { kwargs }
    # Hvis en subkommando blir lagt inn som argument, blir den håndtert som value og blir håndtert i kommando-funksjonen
    """
    match parse(name_parser, string):
        case Err(err):
            return Err(err)
        case Ok((None, _)):
            return Ok((None, string))
        case Ok((name_tree, command_tail)) if name_tree is not None:
            command_tree = Command(name_tree.root)
        # For å blidgjøre typechecker
        case other:
            return other

    match exhaust_parser(arg_parser, command_tail):
        case Err(err):
            return Err(err)
        case Ok((arg_trees, arg_tail)):
            pass

    match exhaust_parser(kwarg_parser, arg_tail):
        case Err(err):
            return Err(err)
        case Ok((kwarg_trees, tail)):
            pass

    command_tree.add_subtrees(arg_trees)
    command_tree.add_subtrees(kwarg_trees)
    return Ok((command_tree, tail))


def value_parser(string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree:Value { value }, tail)

    @grammar
        value =
            | symbol{ symbols }
            | '(expr)'
        symbol = char | int | _
    """
    match get_surrounding_quotes(string):
        case Err(err):
            return Err(err)
        case Ok(result) if result is not None:
            content, _, second_index = result
            tree = Expr(content)
            tail = string[second_index + 1 :]
            return Ok((tree, tail))

    if is_flag(string) or is_key(string):
        return Ok((None, string))

    match string.find(" "):
        case -1:
            content = string
            tail = ""
        case index:
            content = string[:index]
            tail = string[index + 1 :]

    if not is_symbol(content):
        return Ok((None, string))

    return Ok((Value(content), tail))


def name_parser(command_string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree { name }, tail)

    @grammar
        name = char{ symbols }
        symbol = char | int | _
    """
    first_space = command_string.find(" ")
    if first_space == -1:
        name = command_string
        tail = ""
    else:
        name = command_string[0:first_space]
        tail = command_string[first_space + 1 :]

    if is_symbol(name) and name[0].isalpha():
        return Ok((Tree(name), tail))

    return Ok((None, command_string))


def key_parser(command_string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree { key }, tail)

    @grammar
        key = symbol{ symbols }
        symbol = char | int | _
    """
    if not is_key(command_string):
        return Ok((None, command_string))
    new_command_string = command_string[len(KEY_SPECIFIER) :]

    first_space = new_command_string.find(" ")
    if first_space == -1:
        key = new_command_string
        tail = ""
    else:
        key = new_command_string[0:first_space]
        tail = new_command_string[first_space + 1 :]

    if is_symbol(key):
        return Ok((Tree(key), tail))
    return Ok((None, command_string))


def kwarg_parser(command_string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree:Kwarg { key, Optional value }, tail)

    @grammar
        kwarg = key { value }
        key = symbol{ symbols }
        symbol = char | int | _
    """
    match parse(key_parser, command_string):
        case Err(err):
            return Err(err)
        case Ok((None, _)):
            return Ok((None, command_string))
        case Ok((key_tree, key_tail)) if key_tree is not None:
            key = key_tree.root
        # For å hjelpe type-checkeren
        case other:
            return other

    match parse(value_parser, key_tail):
        case Err(err):
            return Err(err)
        case Ok((None, _)):
            return Ok((Kwarg(key), key_tail))
        case Ok((value_tree, value_tail)) if value_tree is not None:
            pass
        # For å hjelpe type-checkeren
        case other:
            return other

    return Ok((Kwarg(key, [value_tree]), value_tail))


def flag_parser(command_string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree:Flags { flags }, tail)

    @grammar
        flags = '-'(char{chars})
    """
    if not is_flag(command_string):
        return Ok((None, command_string))

    # et eventuelt flagg er på formatet '-rf'.
    # Da ønsker vi å hente ut r; vi parser kun ett flagg om gangen
    flag = command_string[1]

    # Hvis det er et mellomrom etter flagget, eks: "-r somearg"
    # Da trenger vi ikke ta vare på '-' tegnet
    # Ellers tar vi vare på det slik at vi kan parse flere flagg senere
    if command_string[2] == " ":
        tail = command_string[3:]
    else:
        tail = command_string[0] + command_string[2:]
    if flag.isalnum():
        return Ok((Flag(flag), tail))
    return Ok((None, command_string))


def arg_parser(command_string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree:{Value|Flag} { value | flags }, tail)

    @grammar
        arg = value | flags
    """
    # Flags take priority over values. If the flag-parser is unable to parse any flags, we try to parse values.
    match parse(flag_parser, command_string):
        case Ok((flag_tree, tail)) if flag_tree is not None:
            return Ok((flag_tree, tail))
        case Err(err):
            return Err(err)

    match parse(value_parser, command_string):
        case Ok((value_tree, tail)) if value_tree is not None:
            return Ok((value_tree, tail))
        case Err(err):
            return Err(err)

    return Ok((None, command_string))


def is_key(arg: str) -> bool:
    if len(arg) < 2:
        return False
    if arg[0:2] == KEY_SPECIFIER:
        return True
    return False


def is_flag(arg: str) -> bool:
    if len(arg) == 0:
        return False
    if arg[0] == FLAG_SPECIFIER:
        return True
    return False


def is_symbol(string: str) -> bool:
    # Sjekker om navnet bare består av alfanumeriske tegn + '_'
    if len(string) == 0:
        return False
    if string.replace("_", "").isalnum():
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


def get_surrounding_quotes(
    string: str,
) -> Result[Optional[tuple[str, int, int]], str]:
    """
    @returns
        Result {Optional (content, 0, second_quote_index) }
    """
    if len(string) < 2:
        return Ok(None)
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
