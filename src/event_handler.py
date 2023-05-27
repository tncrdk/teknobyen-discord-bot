from __future__ import annotations
import discord
from typing import Callable, Optional
from utils import SupportedChannels, Response
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


async def send_message(response: Response) -> None:
    """send_message

    Args:
        response (Message): meldingen som skal sendes
    """
    response_channel = response.response_channel
    await response_channel.send(response.message)
