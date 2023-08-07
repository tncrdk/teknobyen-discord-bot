from result import Err, Ok, Result
import quotes_database
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


def add():
    match quotes_database.format_quotes(quotes):
        case Err(err):
            print(err.msg)
            return
        case Ok((quotes_list, warnings)):
            pass

    reciepts, errors = quotes_database.add_quotes(quotes_list, database)
    for reciept in reciepts:
        print(reciept)
    for err in errors:
        print(err.msg)
    print(warnings)
    print(database)


add()
