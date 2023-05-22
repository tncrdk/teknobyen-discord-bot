from __future__ import annotations
from enum import Enum
import discord
from dataclasses import dataclass


class SupportedChannels(Enum):
    general = "General"
    quotes = "Quotes"


@dataclass
class Response:
    message: str
    response_channel: discord.abc.MessageableChannel
