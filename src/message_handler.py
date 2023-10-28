from abc import ABC
from dataclasses import dataclass
from result import Ok, Err
from database import Database
from quote import Quote
import os
import discord
import quote_utils
import command as cmd
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

    async def on_delete_message(
        self, message: Message, database: Database[Quote]
    ) -> None:
        ...


class QuotesHandler(MessageHandler):
    channel = "quotes"
    ID: int
    commands = []

    async def on_new_message(self, message: Message, database: Database[Quote]) -> None:
        content = message.content
        quotes_list = []
        match quote_utils.format_quotes(content, message.id):
            case Err(err):
                await output.send_message(err.msg, message.channel)
                return
            case Ok((quotes_list, warnings)):
                if len(warnings) != 0:
                    await output.send_errors(warnings, message.channel)

        reciepts, errors = quote_utils.add_quotes(quotes_list, database)
        await output.send_iterable(reciepts, message.channel)
        await output.send_errors(errors, message.channel)

    async def on_edit_message(
        self, old_message: Message, new_message: Message, database: Database[Quote]
    ) -> None:
        # Finner IDen til alle sitatene i databasen som hører til meldingen som ble endret
        old_quote_ids: list[int] = []
        for id, quote in database.items():
            if quote.message_id == old_message.id:
                old_quote_ids.append(id)

        # Sletter alle sitatene som ble laget av den gamle meldingen
        reciepts, errors = quote_utils.remove_quotes(old_quote_ids, database)
        await output.send_iterable(reciepts, old_message.channel)
        await output.send_errors(errors, old_message.channel)

        # Formatterer nye sitater
        new_content = new_message.content
        match quote_utils.format_quotes(new_content, new_message.id):
            case Err(err):
                await output.send_message(err.msg, new_message.channel)
                return
            case Ok((quotes_list, warnings)):
                if len(warnings) != 0:
                    await output.send_errors(warnings, new_message.channel)

        # Legger til nye sitater
        reciepts, errors = quote_utils.add_quotes(quotes_list, database)
        await output.send_iterable(reciepts, new_message.channel)
        await output.send_errors(errors, new_message.channel)

    async def on_delete_message(
        self, message: Message, database: Database[Quote]
    ) -> None:
        # Finner IDen til alle sitatene i databasen som laget av den gamle meldingen
        old_quote_ids: list[int] = []
        for id, quote in database.items():
            if quote.message_id == message.id:
                old_quote_ids.append(id)

        # Sletter alle sitatene som ble laget av den gamle meldingen
        reciepts, errors = quote_utils.remove_quotes(old_quote_ids, database)
        await output.send_iterable(reciepts, message.channel)
        await output.send_errors(errors, message.author)


class GeneralHandler(MessageHandler):
    channel = "general"
    ID: int
    commands = []

    # Ved testing kan funksjonen endres til on_new_message
    async def on_new_message(
        self, member: discord.Member, database: Database[Quote]
    ) -> None:
        pass

    async def on_new_member_join(
        self, member: discord.Member, database: Database[Quote]
    ) -> None:
        server_channels = member.guild.text_channels
        general_channel = None
        for channel in server_channels:
            if channel.id == self.ID:
                general_channel = channel
                break
        if general_channel is None:
            return

        message = f"@everyone Look who it is! {member.mention} finally decided to join us here at {member.guild.name}!!\nWelcome! It is fair to say you have come to the right place!\n"

        quote = database.get_random_element()
        if quote is None:
            message += "Let Thorbjørn demonstrate our greatest qualities with a quote:\n\n'*!¤%#!! Eg sletta heile databasen med velkomst-sitater!'\nThorbjørn"
        else:
            message += (
                f"Let {quote.speaker} demonstrate our greatest qualities with a quote:\n\n'{quote.quote}'\n{quote.speaker}"
            )
            if len(quote.audience) != 0:
                message += f" til {', '.join(quote.audience)}"
        await output.send_message(message, general_channel)

    async def send_weekly_quote(self, server: discord.Guild, database: Database[Quote]) -> None:
        server_channels = server.text_channels
        general_channel = None
        for channel in server_channels:
            if channel.id == self.ID:
                general_channel = channel
                break
        if general_channel is None:
            return
        
        quote = database.get_random_element()
        message = f"@everyone Here comes the weekly quote\n"

        if quote is None:
            message += "Let Thorbjørn demonstrate our greatest qualities with a quote:\n\n'*!¤%#!! Eg sletta heile databasen med velkomst-sitater!'\nThorbjørn"
        else:
            message += (
                f"Let {quote.speaker} demonstrate our greatest qualities with a quote:\n\n'{quote.quote}'\n{quote.speaker}"
            )
            if len(quote.audience) != 0:
                message += f" til {', '.join(quote.audience)}"
        await output.send_message(message, general_channel)

class QuotesInteractiveHandler(MessageHandler):
    channel = "quotes-interactive"
    ID: int
    commands = []

    async def on_new_message(self, message: Message) -> None:
        pass

    async def on_edit_message(self, old_message: Message, new_message: Message) -> None:
        pass

    async def on_delete_message(self, message: Message) -> None:
        pass
