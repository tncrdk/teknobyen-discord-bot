from __future__ import annotations
from typing import Optional, Callable
from result import Result, Err, Ok
from dataclasses import dataclass


KEY_SPECIFIER = "--"
FLAG_SPECIFIER = "-"


"""
Grammar
    command =
        name arguments   
        # En subkommando blir lagt inn som argument, tolket som value, og blir håndtert i kommando-funksjonen
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

    def add_subtree(self, tree: Tree) -> Tree:
        """
        @params
        tree: Tree

        @returns
        Tree

        Legger et tre til som et subtre av @self
        """
        if self.leaves is None:
            return Tree(self.root, [tree])
        return Tree(self.root, self.leaves.append(tree))

    def add_leaves(self, leaves: list[Tree]) -> Tree:
        if self.leaves is None:
            return Tree(self.root, leaves)
        return Tree(self.root, self.leaves + leaves)

    def __str__(self) -> str:
        string = f"Root: {self.root}"
        if self.leaves is None:
            return string
        string += " {\n"
        for subtree in self.leaves:
            string += " " * 3 + str(subtree) + "\n"
        string += "\n}"
        return string


class Kwarg(Tree):
    pass


class Flags(Tree):
    pass


class Value(Tree):
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
                parse_string_tail = parse_string
                break
            case Ok((tree, tail)):
                tree_list.append(tree)
                parse_string = tail

    if len(tree_list) > 0:
        return Ok((tree_list, parse_string_tail))
    return Ok(([], parse_string))


def command_parser(string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree { command_name, Optional [args] }, tail)

    @grammar
        command = name arguments
    # Hvis en subkommando blir lagt inn som argument, blir den håndtert som value og blir håndtert i kommando-funksjonen
    """
    match parse(name_parser, string):
        case Err(err):
            return Err(err)
        case Ok((None, _)):
            return Ok((None, string))
        case Ok((command_tree, command_tail)):
            pass

    match parse(arguments_parser, command_tail):
        case Ok((arg_tree, tail)):
            pass
        case other:
            return other

    if arg_tree is not None:
        command_tree = command_tree.add_subtree(arg_tree)
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
            tree = Value(content)
            tail = string[second_index + 1 :]
            return Ok((tree, tail))

    if is_flags(string) or is_key(string):
        return Ok((None, string))

    match string.find(" "):
        case -1:
            return Ok((Value(string), ""))
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
    match command_string.find(" "):
        case -1:
            raw_key = command_string
            tail = ""
        case index:
            raw_key = command_string[:index]
            tail = command_string[index + 1 :]

    key = raw_key[len(KEY_SPECIFIER) :]

    if is_symbol(key) and is_key(raw_key):
        return Ok((Tree([key]), tail))

    return Ok((Tree(), command_string))


def kwarg_parser(command_string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree:Kwarg { key, Optional value }, tail)

    @grammar
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
            tail = updated_tail
        case other:
            return other

    return Ok((Kwarg([key, value]), tail))


def flags_parser(command_string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree:Flags { flags }, tail)
 
    @grammar
        flags = '-'(char{chars})
    """
    match command_string.find(" "):
        case -1:
            potential_flags = command_string
            tail = ""
        case index:
            potential_flags = command_string[:index]
            tail = command_string[index + 1 :]
    if is_flags(potential_flags) and potential_flags.replace("-", "").isalpha():
        return Ok((Flags([*potential_flags[1:]]), tail))
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
    match parse(flags_parser, command_string):
        case Ok((Flags(flags), tail)) if flags is not None:
            return Ok((Flags(flags), tail))
        case Err(err):
            return Err(err)

    match parse(value_parser, command_string):
        case Ok((Value(value), tail)) if value is not None:
            return Ok((Value(value), tail))
        case Err(err):
            return Err(err)

    return Ok((None, command_string))


def arguments_parser(command_string: str) -> Result[tuple[Optional[Tree], str], str]:
    """
    @param
        command_string: strengen som skal tolkes
    @return
        Result (Optional Tree { Tree:{Kwarg, Arg} }, tail)

    @grammar
        arguments =
            | arg { arguments }
            | kwarg { kwargs }
    """
    match exhaust_parser(arg_parser, command_string):
        case Ok((arg_tree, tail)):
            pass
        case other:
            return other

    match exhaust_parser(kwarg_parser, tail):
        case Ok((kwarg_tree, tail)):
            pass
        case other:
            return other

    return Ok((arg_tree.combine_tree(kwarg_tree), tail))


def is_key(arg: str) -> bool:
    if len(arg) < 2:
        return False
    if arg[0:2] == KEY_SPECIFIER:
        return True
    return False


def is_flags(arg: str) -> bool:
    if len(arg) == 0:
        return False
    if arg[0] == FLAG_SPECIFIER:
        return True
    return False


def is_symbol(string: str) -> bool:
    # Sjekker om navnet bare består av alfanumeriske tegn + _
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
