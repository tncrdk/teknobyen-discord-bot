import discord
import os
from bot import run_bot
from replit import db
from dotenv import load_dotenv


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)

    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    if TOKEN is None:
        raise KeyError("Fant ikke TOKEN i env-variablene")

    if db is None:
        raise Exception("Fant ikke databasen")

    run_bot(client, TOKEN, db)
