import discord
import os
from .bot import run_bot

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)
    # server = client.guilds[0]
    TOKEN = os.getenv("token")

    if TOKEN is None:
        raise KeyError("Fant ikke TOKEN i env-variablene")

    run_bot(client, TOKEN)
