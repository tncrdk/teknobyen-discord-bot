from __future__ import annotations
from enum import Enum
from typing import Iterable
import discord
import os
import time


class SupportedChannels(Enum):
    general = os.getenv("general")
    quotes = os.getenv("quotes")
    announcements = os.getenv("announcements")
    geoguesser_invites = os.getenv("geoguesser_invites")


async def send_iterable(iter: Iterable[str], channel: discord.abc.Messageable) -> None:
    message = "\n\n".join(iter)  # For å skape mellomrom mellom meldingene
    await send_message(message, channel)


async def send_message(message: str, response_channel: discord.abc.Messageable) -> None:
    """send_message

    Args:
        response (Message): meldingen som skal sendes
    """
    try:
        response_channel = response_channel
        await response_channel.send(message)
    except Exception as err:
        log_error(err, message)


def log_error(err: Exception, *args):
    with open("log.txt", "a") as log_file:
        date = time.ctime()
        message = f"[{date}]  {str(type(err))}\n{str(err)}\n"
        log_file.write(message)
        for arg in args:
            log_file.write("\n")
            log_file.write(arg)
        log_file.write("\n\n" + "-" * 10 + "\n\n")
