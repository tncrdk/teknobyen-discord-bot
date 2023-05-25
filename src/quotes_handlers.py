from __future__ import annotations
import discord
from utils import Response
from typing import Optional


def message_handler(message: discord.Message) -> Optional[Response]:
    pass


def message_edit_handler(
    message_before: discord.Message, message_after: discord.Message
) -> Optional[Response]:
    pass


def message_delete_handler(message: discord.Message) -> Optional[Response]:
    pass
