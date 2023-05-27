from __future__ import annotations
from enum import Enum
import discord
from dataclasses import dataclass
import os


class SupportedChannels(Enum):
    general = os.getenv("general")
    quotes = os.getenv("quotes")
    announcements = os.getenv("announcements")
    geoguesser_invites = os.getenv("geoguesser_invites")


@dataclass
class Response:
    message: str
    response_channel: discord.abc.MessageableChannel
