import discord
import general_handlers
import quotes_handlers
from utils import SupportedChannels, Response
from typing import Optional, Callable

MESSAGE_HANDLERS: dict[
    SupportedChannels, Callable[[discord.Message], Optional[Response]]
] = {
    SupportedChannels.general: general_handlers.message_handler,
    SupportedChannels.quotes: quotes_handlers.message_handler,
}

MESSAGE_EDIT_HANDLERS: dict[
    SupportedChannels, Callable[[discord.Message, discord.Message], Optional[Response]]
] = {
    SupportedChannels.quotes: quotes_handlers.message_edit_handler,
}

MESSAGE_DELETE_HANDLERS: dict[
    SupportedChannels, Callable[[discord.Message], Optional[Response]]
] = {
    SupportedChannels.quotes: quotes_handlers.message_delete_handler,
}
