import dill
from pathlib import Path

from database import Database

database_path = Path(".database.pkl")

database = Database(database_path)

print(database.data)
