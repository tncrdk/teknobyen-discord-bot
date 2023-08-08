import time
import discord
from typing import Iterable

from error import BaseError


async def send_iterable(iter: Iterable[str], channel: discord.abc.Messageable) -> None:
    message = "\n\n".join(iter)  # For å skape mellomrom mellom meldingene
    if message == "":
        return
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


async def send_errors(errors: list[BaseError], response_channel: discord.abc.Messageable) -> None:
    error_messages = [err.msg for err in errors]
    await send_iterable(error_messages, response_channel)


def log_error(err: Exception, *args):
    with open("log.txt", "a") as log_file:
        date = time.ctime()
        message = f"[{date}]  {str(type(err))}\n{str(err)}\n"
        log_file.write(message)
        for arg in args:
            log_file.write("\n")
            log_file.write(arg)
        log_file.write("\n\n" + "-" * 10 + "\n\n")
