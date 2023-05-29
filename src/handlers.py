import discord
import general_handlers
import quotes_handlers
from utils import SupportedChannels
from typing import Callable, Coroutine

MESSAGE_HANDLERS: dict[SupportedChannels, Callable[[discord.Message], Coroutine]] = {
    SupportedChannels.general: general_handlers.message_handler,
    SupportedChannels.quotes: quotes_handlers.message_handler,
}

MESSAGE_EDIT_HANDLERS: dict[
    SupportedChannels, Callable[[discord.Message, discord.Message], Coroutine]
] = {
    SupportedChannels.quotes: quotes_handlers.message_edit_handler,
}

MESSAGE_DELETE_HANDLERS: dict[
    SupportedChannels, Callable[[discord.Message], Coroutine]
] = {
    SupportedChannels.quotes: quotes_handlers.message_delete_handler,
}
