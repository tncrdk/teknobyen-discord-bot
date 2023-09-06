import discord
import os
from dotenv import load_dotenv

load_dotenv()
from bot import run_bot
from database import Database
from pathlib import Path
from keep_alive import keep_alive


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)
    keep_alive()

    TOKEN = os.getenv("TOKEN")

    if TOKEN is None:
        raise KeyError("Fant ikke TOKEN i env-variablene")

    DATABASE_PATH = Path("src") / ".database.pkl"
    database = Database(DATABASE_PATH)

    run_bot(client, TOKEN, database)
