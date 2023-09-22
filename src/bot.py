from __future__ import annotations
import discord
import random
import math
from channels import get_botchannel_by_ID, general_handler
from database import Database
from quote import Quote
from output import send_message


def run_bot(client: discord.Client, token: str, database: Database[Quote]):
    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return
        channel_id = message.channel.id
        botchannel = get_botchannel_by_ID(channel_id)
        if botchannel is None:
            print(channel_id)
            return
        await botchannel.on_new_message(message, database)

    @client.event
    async def on_message_edit(
        message_before: discord.Message, message_after: discord.Message
    ) -> None:
        if message_before.author == client.user:
            return
        channel_id = message_before.channel.id
        botchannel = get_botchannel_by_ID(channel_id)
        if botchannel is None:
            print(channel_id)
            return
        await botchannel.on_edit_message(message_before, message_after, database)

    @client.event
    async def on_message_delete(message: discord.Message) -> None:
        if message.author == client.user:
            return
        channel_id = message.channel.id
        botchannel = get_botchannel_by_ID(channel_id)
        if botchannel is None:
            print(channel_id)
            return
        await botchannel.on_delete_message(message, database)

    @client.event
    async def on_member_join(member: discord.Member) -> None:
        await general_handler.on_new_member_join(member, database)


    client.run(token)
