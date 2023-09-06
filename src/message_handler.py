from abc import ABC
from dataclasses import dataclass
from result import Ok, Err
from database import Database
from quote import Quote
import os
import discord
import quotes_database
import commands as cmd
import output

Message = discord.Message
COMMAND_PREFIX = "!"


class MessageHandler(ABC):
    """
    channel: str
    ID: int
    commands = list[Command]
    """

    channel: str
    ID: int
    commands: list[cmd.Command]

    def __init__(self) -> None:
        self.ID = self.get_channel_ID()

    def get_channel_ID(self) -> int:
        ID = os.getenv(self.channel)
        if ID is None:
            raise ValueError(f"Finner ingen ID tilknyttet {self.channel}.")
        if not ID.isnumeric():
            raise ValueError(f"ID-en til {self.channel} er ikke et tall.")
        return int(ID)

    async def on_new_message(self, message: Message, database: Database[Quote]) -> None:
        ...

    async def on_edit_message(
        self, old_message: Message, new_message: Message, database: Database[Quote]
    ) -> None:
        ...

    async def on_delete_message(self, message: Message, database: Database[Quote]) -> None:
        ...


class QuotesHandler(MessageHandler):
    channel = "quotes"
    ID: int
    commands = []

    async def on_new_message(self, message: Message, database: Database[Quote]) -> None:
        content = message.content
        quotes_list = []
        match quotes_database.format_quotes(content, message.id):
            case Err(err):
                await output.send_message(err.msg, message.channel)
                return
            case Ok((quotes_list, warnings)):
                if len(warnings) != 0:
                    await output.send_errors(warnings, message.channel)

        reciepts, errors = quotes_database.add_quotes(quotes_list, database)
        await output.send_iterable(reciepts, message.author)
        await output.send_errors(errors, message.channel)

    async def on_edit_message(
        self, old_message: Message, new_message: Message, database: Database[Quote]
    ) -> None:
        # Sjekker om de nye sitatene er skikkelig formattert. Hvis ikke gjøres det ingeting
        # og brukeren får en feilmelding
        new_content = new_message.content
        channel = new_message.channel
        match quotes_database.format_quotes(new_content, new_message.id):
            case Err(err):
                await output.send_message(err.msg, channel)
                return
            case Ok((new_quotes_list, warnings)):
                if len(warnings) != 0:
                    await output.send_errors(warnings, channel)

        # Den gamle meldingen kan godt være feil sitat. Det er kanskje derfor
        # vedkommende endret den. Denne delen bestemmer hvorvidt man må inn
        # i databasen og slette tidligere sitater. Hvis de ikke ble formattert ble de aldri lagt inn
        old_content = old_message.content
        old_quotes_list = []
        match quotes_database.format_quotes(old_content, old_message.id):
            case Err(_):
                old_quotes_list = []
            case Ok((old_quotes_list, _)):
                pass

        # Hvis de gamle sitatene kanskje finnes i databasen,
        # må de fjernes før de nye kan legges til
        ID_list, errors = quotes_database.get_quote_IDs(old_quotes_list, database)
        # TODO: Finne ut hva som skal gjøres med quotes_not_found
        await output.send_errors(errors, new_message.author)

        new_quotes_list = []
        reciepts, errors = quotes_database.remove_quotes(ID_list, database)
        await output.send_iterable(reciepts, new_message.author)
        await output.send_errors(errors, new_message.channel)

        # Legger til de nye modifiserte sitatene
        reciepts, errors = quotes_database.add_quotes(new_quotes_list, database)
        await output.send_iterable(reciepts, new_message.author)
        await output.send_errors(errors, new_message.channel)

    async def on_delete_message(self, message: Message, database: Database[Quote]) -> None:
        # Den gamle meldingen kan godt være feil formattert. Det er kanskje derfor vedkommende endret den. Denne delen bestemmer hvorvidt man må inn
        # i databasen og slette tidligere sitater
        content = message.content
        quotes_list = []
        match quotes_database.format_quotes(content, message.id):
            case Err(_):
                # Grunnet logikken når sitat blir lest, vil ikke en feilformattert
                # melding bli lagt til i databasen
                return
            case Ok((quotes_list, _)):
                pass

        # Hvis de gamle sitatene finnes i databasen, må de fjernes
        ID_list, errors = quotes_database.get_quote_IDs(quotes_list, database)
        # TODO: Finne ut hva som skal gjøres med quotes_not_found
        await output.send_errors(errors, message.author)
        #
        reciepts, errors = quotes_database.remove_quotes(ID_list, database)
        await output.send_iterable(reciepts, message.author)
        await output.send_errors(errors, message.channel)


@dataclass
class GeneralHandler(MessageHandler):
    channel = "general"
    commands = []

    async def on_new_message(self, message: Message) -> None:
        return
        content = message.content
        if content[0] != COMMAND_PREFIX:
            return
        content = content[1:]
        context = Context()
        match cmd.parse_command(content, context, self.commands):
            case Err(err):
                await output.send_message(err, message.channel)
            case Ok(output):
                await output.send_message(output, message.channel)


@dataclass
class QuotesInteractiveHandler(MessageHandler):
    channel = "quotes-interactive"
    commands = []

    async def on_new_message(self, message: Message) -> None:
        pass

    async def on_edit_message(self, old_message: Message, new_message: Message) -> None:
        pass

    async def on_delete_message(self, message: Message) -> None:
        pass
