from __future__ import annotations
import discord
from typing import Callable, Optional
from utils import SupportedChannels, Response
import general_channel
import quotes_channel

#Tatt fra ChatGPT, imports for at koden i handle message skal virke...
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

MESSAGE_HANDLERS: dict[
    SupportedChannels, Callable[[discord.Message], Optional[Response]]
] = {
    SupportedChannels.general: general_channel.message_handler,
}

MESSAGE_EDIT_HANDLERS = {}
MESSAGE_DELETE_HANDLERS = {}
import handlers


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


def handle_member_join(member: discord.Member) -> Response:
    pass


def handle_member_join(member: discord.Member) -> Optional[Response]:
    #Baserer seg på at man velger ut en tilfeldig quote, men kan endres til annen implementasjon...
    random_quote = ""
    quote_person = ""
    channelID = 1074777709433077762
    welcome_channel = bot.get_channel(channelID)
    welcome_channel.send(f'Velkommen til serveren, {member.mention}! Eller som {quote_person} ville sagt: {random_quote}')
    return member


# TODO Gi et bedre navn. Kanskje flytte inn i run_bot
def event_handler(
    handlers: dict[SupportedChannels, Callable[[discord.Message], Response]],
    message: discord.Message,
) -> Optional[Response]:
    pass


async def send_message(response: Response) -> None:
    """send_message

    Args:
        response (Message): meldingen som skal sendes
    """
    response_channel = response.response_channel
    await response_channel.send(response.message)
