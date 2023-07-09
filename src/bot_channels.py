import os
import discord
import quotes_database
import commands as cmd
from typing import Callable, Optional
from abc import ABC
from dataclasses import dataclass
from result import Result, Ok, Err
from . import io

Message = discord.Message
COMMAND_PREFIX = "!"


class BotChannel(ABC):
    """
    name: str
    ID: int
    commands = list[Command]
    """

    name: str
    ID: int
    commands: list[cmd.Command]

    def __init__(self) -> None:
        self.ID = self.get_channel_ID()

    def get_channel_ID(self) -> int:
        ID = os.getenv(self.name)
        if ID is None:
            raise ValueError(f"Finner ingen ID tilknyttet {self.name}.")
        if not ID.isnumeric():
            raise ValueError(f"ID-en til {self.name} er ikke et tall.")
        return int(ID)

    async def on_new_message(self, message: Message) -> None:
        # Do nothing
        pass

    async def on_edit_message(self, old_message: Message, new_message: Message) -> None:
        # Do nothing
        pass

    async def on_delete_message(self, message: Message) -> None:
        # Do nothing
        pass


@dataclass(frozen=True)
class QuotesChannel(BotChannel):
    name = "quotes"
    commands = []

    async def on_new_message(self, message: Message) -> None:
        content = message.content
        match quotes_database.format_quotes(content):
            case Err(err):
                await io.send_message(err, message.channel)
                return
            case Ok((quotes_list, warnings)):
                if warnings is not None:
                    await io.send_iterable(warnings, message.channel)

        reciepts, errors = quotes_database.add_quotes(quotes_list)
        await io.send_iterable(reciepts, message.author)
        await io.send_iterable(errors, message.channel)

    async def on_edit_message(self, old_message: Message, new_message: Message) -> None:
        # Sjekker om de nye sitatene er skikkelig formattert. Hvis ikke gjøres det ingeting
        # og brukeren får en feilmelding
        new_content = new_message.content
        match quotes_database.format_quotes(new_content):
            case Err(err):
                await io.send_message(err, new_message.channel)
                return
            case Ok((new_quotes_list, warnings)):
                if warnings is not None:
                    await io.send_iterable(warnings, new_message.channel)

        # Den gamle meldingen kan godt være feil sitat. Det er kanskje derfor
        # vedkommende endret den. Denne delen bestemmer hvorvidt man må inn
        # i databasen og slette tidligere sitater. Hvis de ikke ble formattert ble de aldri lagt inn
        old_content = old_message.content
        old_quotes_list = []
        match quotes_database.format_quotes(old_content):
            case Err(_):
                possibly_exists_in_database = False
            case Ok((old_quotes_list, _)):
                possibly_exists_in_database = True

        # Hvis de gamle sitatene kanskje finnes i databasen,
        # må de fjernes før de nye kan legges til
        if possibly_exists_in_database:
            ID_list = []
            quotes_not_found = []
            for quote in old_quotes_list:
                match quotes_database.get_quote_ID(quote):
                    case Err(err):
                        quotes_not_found.append(err)
                    case Ok(ID):
                        ID_list.append(ID)
            # TODO Finne ut hva som skal gjøres med quotes_not_found
            reciepts, errors = quotes_database.remove_quotes(ID_list)
            await io.send_iterable(reciepts, new_message.author)
            await io.send_iterable(errors, new_message.channel)
            await io.send_iterable(quotes_not_found, new_message.author)

        # Legger til de nye modifiserte sitatene
        reciepts, errors = quotes_database.add_quotes(new_quotes_list)
        await io.send_iterable(reciepts, new_message.author)
        await io.send_iterable(errors, new_message.channel)

    async def on_delete_message(self, message: Message) -> None:
        # Den gamle meldingen kan godt være feil formattert. Det er kanskje derfor vedkommende endret den. Denne delen bestemmer hvorvidt man må inn
        # i databasen og slette tidligere sitater
        content = message.content
        quotes_list = []
        match quotes_database.format_quotes(content):
            case Err(_):
                # Grunnet logikken når sitat blir lest, vil ikke en feilformattert
                # melding bli lagt til i databasen
                return
            case Ok((quotes_list, _)):
                pass
        # Hvis de gamle sitatene finnes i databasen, må de fjernes
        ID_list = []
        quotes_not_found = []
        for quote in quotes_list:
            match quotes_database.get_quote_ID(quote):
                case Err(err):
                    quotes_not_found.append(err)
                case Ok(ID):
                    ID_list.append(ID)
        # TODO Finne ut hva som skal gjøres med quotes_not_found
        reciepts, errors = quotes_database.remove_quotes(ID_list)
        await io.send_iterable(reciepts, message.author)
        await io.send_iterable(errors, message.channel)
        await io.send_iterable(quotes_not_found, message.author)


@dataclass(frozen=True)
class GeneralChannel(BotChannel):
    name = "general"
    commands: list[cmd.Command] = []

    async def on_new_message(self, message: Message) -> None:
        content = message.content
        if content[0] != COMMAND_PREFIX:
            return
        content = content[1:]
        context = cmd.Context()
        match cmd.parse_command(content, context, self.commands):
            case Err(err):
                await io.send_message(err, message.channel)
            case Ok(output):
                await io.send_message(output, message.channel)


@dataclass(frozen=True)
class QuotesInteractiveChannel(BotChannel):
    name = "quotes-interactive"
    commands = []

    async def on_new_message(self, message: Message) -> None:
        pass

    async def on_edit_message(self, old_message: Message, new_message: Message) -> None:
        pass

    async def on_delete_message(self, message: Message) -> None:
        pass
