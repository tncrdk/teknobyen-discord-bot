import discord
import os
import sys
from dotenv import load_dotenv
from bot import run_bot
from database import Database
from pathlib import Path



def main(debug: bool):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)
    load_dotenv()

    TOKEN = os.getenv("TOKEN")
    if TOKEN is None:
        raise KeyError("Fant ikke TOKEN i env-variablene")

    if debug:
        SAVE_DIR = Path(__file__).parent
    else:
        SAVE_DIR = Path("/persistent-database")
    DATABASE_PATH = SAVE_DIR / ".database.pkl" 
    ID_PATH = SAVE_DIR / ".ID"

    database = Database(DATABASE_PATH, ID_PATH)

    run_bot(client, TOKEN, database)

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2 or args[1] == "debug":
        debug=True
    elif args[1] == "release":
        debug = False
    else:
        print(f"{args[1:]} is not a valid argument")
        debug = True
    main(debug)
