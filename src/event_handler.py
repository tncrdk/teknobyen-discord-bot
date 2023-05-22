from __future__ import annotations
import discord
from typing import Optional, Callable
from utils import SupportedChannels, Response
import general_channel
import quotes_channel

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
    pass


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
