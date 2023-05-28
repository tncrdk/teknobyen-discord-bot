from __future__ import annotations
import discord
from typing import Callable, Optional
from utils import SupportedChannels, Response
import handlers

# Tatt fra ChatGPT, imports for at koden i handle message skal virke...
# TODO gi det inn som et argument heller fra even-funksjonen. Det er bedre hvis alt av server-variabler er definert der
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def handle_message(message: discord.Message) -> Optional[Response]:
    channel_id = message.channel.id
    channel_key = SupportedChannels(channel_id)
    message_handler = handlers.MESSAGE_HANDLERS.get(channel_key)
    if message_handler == None:
        print(channel_key)
        return
    response = message_handler(message)
    return response


def handle_message_edit(
    message_before: discord.Message, message_after: discord.Message
) -> Optional[Response]:
    channel_id = message_after.channel.id
    channel_key = SupportedChannels(channel_id)
    handler = handlers.MESSAGE_EDIT_HANDLERS.get(channel_key)
    if handler == None:
        print(channel_key)
        return
    response = handler(message_before, message_after)
    return response


def handle_message_delete(message: discord.Message) -> Optional[Response]:
    channel_id = message.channel.id
    channel_key = SupportedChannels(channel_id)
    handler = handlers.MESSAGE_DELETE_HANDLERS.get(channel_key)
    if handler == None:
        print(channel_key)
        return
    response = handler(message)
    return response


def handle_member_join(member: discord.Member) -> Optional[Response]:
    # Baserer seg på at man velger ut en tilfeldig quote, men kan endres til annen implementasjon...
    random_quote = ""
    quote_person = ""
    channelID = 1074777709433077762  # TODO Bruk os.getenv() for sikkerhet
    welcome_channel = bot.get_channel(
        channelID
    )  # TODO General channel kan legges inn som et argument. Det er sikrere; se kommentar over
    if welcome_channel == None:
        print("Kanal-iden er feil")
        return
    welcome_channel.send(
        f"Velkommen til serveren, {member.mention}! Eller som {quote_person} ville sagt: {random_quote}"
    )
    return member


async def send_message(response: Response) -> None:
    """send_message

    Args:
        response (Message): meldingen som skal sendes
    """
    response_channel = response.response_channel
    await response_channel.send(response.message)
