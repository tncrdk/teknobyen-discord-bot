from typing import Optional
import message_handler

welcome_handler = message_handler.WelcomeHandler()
CHANNELS = [message_handler.QuotesHandler(), welcome_handler]


def get_botchannel_by_ID(ID: int) -> Optional[message_handler.MessageHandler]:
    for channel in CHANNELS:
        if channel.ID == ID:
            return channel
    return None
