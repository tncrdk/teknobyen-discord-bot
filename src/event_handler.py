from __future__ import annotations
import discord
from typing import Optional, Callable
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


def handle_message(message: discord.Message) -> Optional[Response]:
    channel = str(message.channel)

    message_handler = MESSAGE_HANDLERS.get(SupportedChannels(channel))
    if message_handler == None:
        return
    response = message_handler(message)
    return response


def handle_message_edit(
    message_before: discord.Message, message_after: discord.Message
) -> Optional[Response]:
    pass


def handle_message_delete(message: discord.Message) -> Optional[Response]:
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


async def send_message(message: Response) -> None:
    """send_message

    Args:
        response (Message): meldingen som skal sendes
    """
    pass
