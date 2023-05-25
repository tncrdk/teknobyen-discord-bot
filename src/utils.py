from __future__ import annotations
from enum import Enum
import discord
from dataclasses import dataclass


class SupportedChannels(Enum):
    general = 1074777709433077762
    quotes = 1108439178489905222
    announcements = 1074809460880588920
    geoguesser_invites = 1108439882164084796


@dataclass
class Response:
    message: str
    response_channel: discord.abc.MessageableChannel
