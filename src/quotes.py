from __future__ import annotations
from typing import Optional
from result import Result, Err, Ok
from dataclasses import dataclass
import re
import os
import random


def get_quote_ID(quote: Quote) -> Result[int, str]:
    database: dict[int, dict] = {}
    database_entry = {
        "speaker": quote.speaker,
        "quote": quote.quote,
        "audience": quote.audience,
    }
    try:
        items = database.items()
        for ID, quote_entry in items:
            if quote_entry == database_entry:
                return Ok(ID)
        return Err(f"Dette sitatet finnes ikke i databasen, {quote}")
    except Exception as err:
        error_message = f"{str(err)}.\nKontakt Thorbjørn"
        return Err(error_message)


def add_quotes(quotes: list[Quote]) -> tuple[list[str], Result[None, list[str]]]:
    errors = []
    reciepts = []
    for quote in quotes:
        match add_quote_to_database(quote):
            case Err(err):
                error_message = f"{quote} ble ikke lagt til i databasen grunnet feil: {{\n    {err}\n}}"
                errors.append(error_message)
            case Ok(reciept):
                reciepts.append(reciept)

    return reciepts, Err(errors)


def add_quote_to_database(quote: Quote) -> Result[str, str]:
    # TODO Må tilpasses databasen i replit; fungerer veldig likt som en dictionary
    database: dict[int, dict] = {}  # Med innhold når det er databasen
    database_entry = {
        "speaker": quote.speaker,
        "quote": quote.quote,
        "audience": quote.audience,
    }
    try:
        if database_entry in database.values():
            return Err(f"{quote} finnes allerede i databasen")

        match create_quote_ID():
            case Err(error_message):
                return Err(error_message)
            case Ok(ID):
                database[ID] = database_entry
    except Exception as err:
        error_message = f"{str(err)}\nKontakt Thorbjørn"
        return Err(error_message)

    return Ok(f"Successfully added {quote} to the database")


def remove_quotes(quotes_IDs: list[int]) -> tuple[list[str], Result[None, list[str]]]:
    """Fjern flere sitat på en gang

    Args:
        quotes_IDs (list[int]): Sitat-IDer

    Returns:
        tuple[list[str], Result[None, list[str]]]: (Kvitteringer, None | Feilmeldinger)
    """
    errors = []
    reciepts = []
    for quote_ID in quotes_IDs:
        match remove_quote_from_database(quote_ID):
            case Err(err):
                error_message = (
                    f"Kunne ikke slette sitat {quote_ID} grunnet: {{\n    {err}\n}}"
                )
                errors.append(error_message)
            case Ok(reciept):
                reciepts.append(reciept)

    return reciepts, Err(errors)


def remove_quote_from_database(ID: int) -> Result[str, str]:
    database: dict[int, dict] = {}  # Med innhold når det er databasen
    try:
        if not ID in database:
            return Err(f"Entry {id} doesn't exist in the database")
        deleted_quote = database.pop(ID)
    except Exception as err:
        error_message = f"{str(err)}\nKontakt Thorbjørn"
        return Err(error_message)
    return Ok(f"Successfully deleted {deleted_quote} from database.\nID: {ID}")


def update_quotes(quotes: list[int]) -> tuple[list[str], Result[None, list[str]]]:
    pass


def format_quotes(raw_quotes: str) -> Result[list[Quote], str]:
    """Formatterer sitatene

    Args:
        raw_quotes (str): hele rå-meldingen med sitater

    Returns:
        Result[list[Quote], str]: En liste av sitatene eller en feilmelding
    """
    quotes_list: list[Quote] = []
    raw_quotes_list = raw_quotes.strip().split("\n\n")
    for raw_quote in raw_quotes_list:
        speaker, audience, quote = format_one_quote(raw_quote)
        validation_result = validate_quote(speaker, audience, quote)
        if validation_result.is_err():
            return Err(
                f"""{raw_quote} is not a valid quote.
                After formatting:
                Speaker: {speaker}
                Audience: {audience}
                Quote: {quote}
                
                {validation_result.err()}"""
            )

        quotes_list.append(Quote(speaker, audience, quote))
    return Ok(quotes_list)


def format_one_quote(raw_quote: str) -> tuple[str, list[str], str]:
    """formatterer et sitat fra en streng

    Args:
        quote (str): en streng med sitatet

    Returns:
        tuple[str, list[str], str]: [avsender , publikumet , sitat]
    """
    header, *quote = raw_quote.strip().split("\n")
    header_names = re.findall(r"\b(?!til|og)\b[\w\-_]+", header)
    if len(header_names) == 0:
        speaker, audience = "", []
    else:
        speaker, *audience = header_names
    return speaker, audience, "\n".join(quote)


def validate_quote(speaker: str, audience: list[str], quote: str) -> Result[None, str]:
    if speaker == "":
        return Err("Speaker not found")
    if quote == "":
        return Err("Quote found")
    # TODO Legge til flere tilfeller av ugyldig input
    return Ok()


def create_quote_ID() -> Result[int, str]:
    ID_str = os.getenv("next_quote_id")
    if ID_str == None or not ID_str.isalnum():
        return Err("Kan ikke generere sitat-ID. Kontakt Thorbjørn")
    ID = int(ID_str)
    os.environ["next_quote_id"] = str(ID + random.randint(1, 10))
    return Ok(ID)


@dataclass
class Quote:
    speaker: str
    audience: list[str]
    quote: str
