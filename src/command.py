from __future__ import annotations
from dataclasses import dataclass
import parse_command as pc
from database import Database
from abc import ABC
from typing import Optional, Type
from result import Result, Err, Ok
from textwrap import indent


T = str | int | float


class Command(ABC):
    name: str
    description: str
    subcommands: dict[str, Command]
    values: list[AbstractPositionalArgument]
    flags: dict[str, AbstractFlagArgument]
    kwargs: dict[str, AbstractKwargArgument]

    def __init__(
        self,
    ) -> None:
        self.create_help_text()
        self.required_pos_args = 0
        for arg in self.values:
            if not arg.optional:
                self.required_pos_args += 1

    def run(
        self,
        arguments: Arguments,
        context: Context,
        database: Database,
    ) -> Result[None, str]:
        """Define what a command should do when called. This function needs to be implemented by inherited classes.
        @attrs
        arguments (Arguments): Contains all arguments passed to the command
        context (Context): Contains all context the command was called in.
        database (Database): Database for data etc.

        @returns
        Ok( None )
        Err( error_message )
        """
        ...

    def clean_tree(self, parse_tree: pc.Tree) -> Result[tuple[Command, Arguments], str]:
        """Clean the syntax tree returned from the parser. Check if arguments match specifications.

        @attrs
        parse_tree: parse_command.Tree

        @Returns
        Ok( command, arguments )
        Err( error_message )
        """

        if parse_tree.leaves is None:
            return Err("parse_tree is `None`, and is not valid.")

        num_args = 0
        value_args = []
        flag_args = []
        kwarg_args = dict()

        # TODO: Separate into cleaning-functions

        # Iterate through every passed arg
        for index, leaf in enumerate(parse_tree.leaves):
            if type(leaf) == pc.Value:
                # Check if first arg is a subcommand. In that case clean the rest of the args
                # with the subcommand
                subcommand = self.subcommands.get(leaf.root)
                # A subcommand needs to exist and it needs to be the first argument
                if subcommand is not None and index == 0:
                    match subcommand.clean_tree(
                        pc.Tree(leaf.root, parse_tree.leaves[1:])
                    ):
                        case Err(err):
                            err = (
                                f"Command: {subcommand.name} {{\n"
                                + indent(str(err), " " * 4)
                                + "\n}"
                            )
                            return Err(err)
                        case Ok(value):
                            return Ok(value)

                # If we have gotten too many values, try to parse the rest and the too-many error will be handled at the end of the function
                if index >= len(self.values):
                    num_args += 1
                    continue

                # If the value is positioned correctly check if we can convert it to the correct type
                match self.convert_value(leaf, self.values[index].value_type):
                    case Err(err):
                        return Err(err)
                    case Ok(new_value):
                        value_args.append(new_value)
                num_args += 1

            elif type(leaf) == pc.Flag:
                # Check if it is a valid flag and append it to all the passed flags
                if not leaf.root in self.flags:
                    return Err(
                        f"{leaf.root} is not a valid flag of command {parse_tree.root}."
                    )
                flag_args.append(leaf.root)

            elif type(leaf) == pc.Kwarg:
                # Check if it is a valid kwarg
                if not leaf.root in self.kwargs:
                    return Err(
                        f"{leaf.root} is not a valid kwarg of command {parse_tree.root}."
                    )
                # Check for duplicates
                if leaf.root in kwarg_args:
                    return Err(f"Duplicate of kwarg: {leaf.root}.")

                if leaf.leaves is None:
                    # If leaves is None, check if that is a valid option. Add to kwarg dict
                    if self.kwargs[leaf.root].value_type is not None:
                        return Err(f"Key {leaf.root} can not take a value of `None`.")
                    kwarg_args[leaf.root] = None
                    continue

                # Convert argument to the proper type
                match self.convert_value(
                    leaf.leaves[0], self.kwargs[leaf.root].value_type
                ):
                    case Err(err):
                        return Err(err)
                    case Ok(key_value):
                        kwarg_args[leaf.root] = key_value

        # Handle wrong number of values
        if num_args > len(self.values):
            return Err(
                f"Too many arguments were passed. Excpected {len(self.values)}. Got {num_args}"
            )
        if num_args < self.required_pos_args:
            return Err(
                f"Too few arguments were passed. Expected {self.required_pos_args}. Got {num_args}"
            )

        return Ok((self, Arguments(value_args, flag_args, kwarg_args)))

    def invoke_command(
        self, parse_tree: pc.Tree, context: Context, database: Database
    ) -> Result[None, str]:
        """Is used by the program to clean the arguments and run the command.

        @attrs
        parse_tree (parse_command.Tree): The tree returned from the parser
        context (Context): Context of where the command was called
        database (Database): Database for data

        @returns
        Ok( None )
        Err( error_message )
        """
        match self.clean_tree(parse_tree):
            case Err(err):
                err = f"Command: {self.name} {{\n" + indent(str(err), " " * 4) + "\n}"
                return Err(err)
            case Ok((command, args)):
                print(command)
        return command.run(args, context, database)

    def convert_value(self, value: pc.Tree, conversion_type: Type[T]) -> Result[T, str]:
        if not type(value) == pc.Value:
            # Unrecoverable error
            return Err(
                f"{value} is not of type `Value`, but {type(value)}. Contact Thorbjørn Djupvik."
            )
        # Try to convert, if not return error
        try:
            # TODO: Check if int() does some funky stuff to strings.
            new_value = conversion_type(value.root)
        except:
            return Err(f"{value.root} can not be converted to type {conversion_type}.")
        return Ok(new_value)

    def create_help_text(self) -> None:
        """Generates the help text for the command."""
        self.help_txt = (
            f"{self.name} {{args}} -{{flags}} --{{kwarg-key}} kwarg-value\n"
            + self.description
            + "\n"
            + "-" * 10
            + "\n"
            + "Subcommands:\n"
        )
        for command in self.subcommands.values():
            self.help_txt += f"{command.name}: {command.description}\n"
        self.help_txt += 10 * "-"
        for arg in self.values:
            self.help_txt += f"{arg.name} : {arg.description}\n"
        self.help_txt += 10 * "-"
        for flag in self.flags.values():
            self.help_txt += f"{flag.flag_name} : {flag.description}\n"
        self.help_txt += 10 * "-"
        for kwarg in self.kwargs.values():
            self.help_txt += f"{kwarg.key} : {kwarg.description}\n"


@dataclass
class Arguments:
    values: list[T]
    flags: list[str]
    kwargs: dict[str, T]


class Context:
    pass


class AbstractArgument(ABC):
    def __init__(
        self, value_type: Type[T], default: Optional[T], optional: bool = False
    ) -> None:
        if default is not None and not isinstance(default, value_type):
            raise ValueError(
                f"Default kan ikke være {default}, med type {type(default).__name__}. Den skal være av type {value_type}"
            )
        self.optional = optional


class AbstractPositionalArgument(AbstractArgument):
    def __init__(
        self,
        name: str,
        value_type: Type[T],
        description: str,
        default: Optional[T] = None,
    ) -> None:
        super().__init__(value_type, default)
        self.name = name
        self.value_type = value_type
        self.description = description
        self.default = default

    def bind_value(self, value: T):
        self.value = value


class AbstractFlagArgument(AbstractArgument):
    def __init__(self, flag_name: str, description: str) -> None:
        if not flag_name.isalnum():
            raise ValueError(f"Flagg-navnet må være alfanumerisk, ikke {flag_name}.")
        self.flag_name = flag_name
        self.description = description


class AbstractKwargArgument(AbstractArgument):
    def __init__(
        self, key: str, value_type: Type[T], description: str, default: Optional[T]
    ) -> None:
        super().__init__(value_type, default)
        self.key = key
        self.value_type = value_type
        self.description = description
        self.default = default
