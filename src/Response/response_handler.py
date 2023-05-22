from __future__ import annotations
import discord
from typing import Optional, Callable
from utils import SupportedChannels, Response
import general_channel
import quotes_channel

CHANNEL_HANDLERS: dict[SupportedChannels, Callable[[discord.Message], Response]] = {
    SupportedChannels.general: general_channel.handler,
}


def handle_message(message: discord.Message) -> Optional[Response]:
    channel = str(message.channel)

    message_handler = CHANNEL_HANDLERS.get(SupportedChannels(channel))
    if message_handler == None:
        return
    response = message_handler(message)
    return response


async def send_message(response: Response) -> None:
    """send_message

    Args:
        response (Response): responsen som skal sendes
    """
    pass
