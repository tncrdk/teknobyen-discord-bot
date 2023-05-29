from __future__ import annotations
from typing import Optional
from result import Err, Ok, Result
import discord
import quotes
import utils


async def message_handler(message: discord.Message) -> None:
    content = message.content
    match quotes.format_quotes(content):
        case Err(err):
            await utils.send_message(err, message.channel)
            return
        case Ok((quotes_list, warnings)):
            if warnings != None:
                await utils.send_iterable(warnings, message.channel)

    reciepts, errors = quotes.add_quotes(quotes_list)
    if len(reciepts) != 0:
        await utils.send_iterable(reciepts, message.author)
    if len(errors) != 0:
        await utils.send_iterable(errors, message.channel)


async def message_edit_handler(
    message_before: discord.Message, message_after: discord.Message
) -> None:
    response = "Quotes will not be edited by changing the message they were created from. If you want to change the quotes you have to manually change them by using the command"
    await utils.send_message(response, message_before.channel)


async def message_delete_handler(message: discord.Message) -> None:
    response = "Quotes will not be deleted by deleting the message they were created from. If you want to delete the quotes you have to manually delete them by using the command"
    await utils.send_message(response, message.channel)
    # Kanskje det skal gå an. Alle sitat som blir lagt til i databasen har kommet fra et riktig formattert sitat.
