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
        save_dir = Path(__file__).parent
    else:
        save_dir = Path("/persistent_database")
    database_path = save_dir / ".database.pkl"
    id_path = save_dir / ".ID"

    database = Database(database_path, id_path)

    run_bot(client, TOKEN, database)


if __name__ == "__main__":
    args = sys.argv
    if len(args) <= 1 or args[1] in ("debug", "dev"):
        debug = True
    elif args[1] in ("release", "prod"):
        debug = False
    else:
        print(f"{args[1:]} is not a valid argument")
        sys.exit()
    main(debug)
