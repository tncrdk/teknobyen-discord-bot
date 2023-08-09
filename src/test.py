from result import Err, Ok, Result
from quotes_database import create_quote_ID
from dotenv import load_dotenv, find_dotenv

dotenv_file = find_dotenv()
load_dotenv()


quotes = """



Eirik til gjengen Hans-Erik
Hallo der
men ikke


Thorbjørn til Hans, Ola, Per
hahah
hahha
asdef


hans
asdf
kjaskjadskjasdfjk


Per
adfasdfasdfasdf


Per
adfasdfasdfasdf
"""

database = {}

res = create_quote_ID()
print(res)
