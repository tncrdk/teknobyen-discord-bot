from __future__ import annotations
from typing import Optional
import discord
import quotes
from utils import Response


def message_handler(message: discord.Message) -> Optional[Response]:
    content = message.content


def message_edit_handler(
    message_before: discord.Message, message_after: discord.Message
) -> Optional[Response]:
    pass


def message_delete_handler(message: discord.Message) -> Optional[Response]:
    pass
