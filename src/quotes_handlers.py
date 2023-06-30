from __future__ import annotations
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
            if warnings is not None:
                await utils.send_iterable(warnings, message.channel)

    reciepts, errors = quotes.add_quotes(quotes_list)
    await utils.send_iterable(reciepts, message.author)
    await utils.send_iterable(errors, message.channel)


async def message_edit_handler(
    message_before: discord.Message, message_after: discord.Message
) -> None:
    # Sjekker om de nye sitatene er skikkelig formattert. Hvis ikke gjøres det ingeting
    # og brukeren får en feilmelding
    new_content = message_after.content
    match quotes.format_quotes(new_content):
        case Err(err):
            await utils.send_message(err, message_after.channel)
            return
        case Ok((new_quotes_list, warnings)):
            if warnings is not None:
                await utils.send_iterable(warnings, message_after.channel)

    # Den gamle meldingen kan godt være feil formattert. Det er kanskje derfor
    # vedkommende endret den. Denne delen bestemmer hvorvidt man må inn
    # i databasen og slette tidligere sitater
    old_content = message_before.content
    old_quotes_list = []
    match quotes.format_quotes(old_content):
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
            match quotes.get_quote_ID(quote):
                case Err(err):
                    quotes_not_found.append(err)
                case Ok(ID):
                    ID_list.append(ID)
        # TODO Finne ut hva som skal gjøres med quotes_not_found
        reciepts, errors = quotes.remove_quotes(ID_list)
        await utils.send_iterable(reciepts, message_after.author)
        await utils.send_iterable(errors, message_after.channel)
        await utils.send_iterable(quotes_not_found, message_after.author)

    # Legger til de nye modifiserte sitatene
    reciepts, errors = quotes.add_quotes(new_quotes_list)
    await utils.send_iterable(reciepts, message_after.author)
    await utils.send_iterable(errors, message_after.channel)


async def message_delete_handler(message: discord.Message) -> None:
    # Den gamle meldingen kan godt være feil formattert. Det er kanskje derfor
    # vedkommende endret den. Denne delen bestemmer hvorvidt man må inn
    # i databasen og slette tidligere sitater
    content = message.content
    quotes_list = []
    match quotes.format_quotes(content):
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
        match quotes.get_quote_ID(quote):
            case Err(err):
                quotes_not_found.append(err)
            case Ok(ID):
                ID_list.append(ID)
    # TODO Finne ut hva som skal gjøres med quotes_not_found
    reciepts, errors = quotes.remove_quotes(ID_list)
    await utils.send_iterable(reciepts, message.author)
    await utils.send_iterable(errors, message.channel)
    await utils.send_iterable(quotes_not_found, message.author)
