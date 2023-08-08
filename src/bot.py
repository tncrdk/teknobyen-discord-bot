from __future__ import annotations
import discord
from replit.database.database import Database
from channels import get_botchannel_by_ID


def run_bot(client: discord.Client, token: str, database: Database):
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

    @client.event
    async def on_message_delete(message: discord.Message) -> None:
        if message.author == client.user:
            return

    @client.event
    async def on_member_join(member: discord.Member) -> None:
        pass

    client.run(token)
