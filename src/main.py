import discord
import os
from bot import run_bot
from dotenv import load_dotenv
from database import Database
from pathlib import Path


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)

    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    if TOKEN is None:
        raise KeyError("Fant ikke TOKEN i env-variablene")

    DATABASE_PATH = Path(".database.pkl")
    database = Database(DATABASE_PATH)

    run_bot(client, TOKEN, database)
