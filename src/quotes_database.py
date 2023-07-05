from __future__ import annotations
from typing import Optional
from result import Result, Err, Ok
from dataclasses import dataclass
import re
import os
import random

CONTACT_PERSON = "Thorbjørn"

# TODO Må tilpasses databasen i replit; fungerer veldig likt som en dictionary


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
        error_message = f"{str(err)}.\nKontakt {CONTACT_PERSON}"
        return Err(error_message)


def add_quotes(quotes: list[Quote]) -> tuple[list[str], list[str]]:
    """legge til flere sitater til databasen

    Args:
        quotes (list[Quote]): liste med sitat

    Returns:
        tuple[list[str], list[str]]: (Kvitteringer, Feilmeldinger)
    """
    errors = []
    reciepts = []
    for quote in quotes:
        match add_quote_to_database(quote):
            case Err(err):
                error_message = f"{quote} ble ikke lagt til i databasen grunnet feil: {{\n    {err}\n}}"
                errors.append(error_message)
                continue
            case Ok(reciept):
                reciepts.append(reciept)

    return reciepts, errors


def add_quote_to_database(quote: Quote) -> Result[str, str]:
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
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(error_message)

    return Ok(f"Successfully added {quote} to the database")


def remove_quotes(quotes_IDs: list[int]) -> tuple[list[str], list[str]]:
    """Fjern flere sitat på en gang

    Args:
        quotes_IDs (list[int]): Sitat-IDer

    Returns:
        tuple[list[str], list[str]]: (Kvitteringer, Feilmeldinger)
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
                continue
            case Ok(reciept):
                reciepts.append(reciept)

    return reciepts, errors


def remove_quote_from_database(ID: int) -> Result[str, str]:
    """Sletter et sitat i databasen

    Args:
        ID (int): ID-en til sitatet som skal slettes

    Returns:
        Result[str, str]: Ok(Kvittering) | Err(Feilmelding)
    """
    database: dict[int, dict] = {}  # Med innhold når det er databasen
    try:
        if ID not in database:
            return Err(f"Entry {ID} doesn't exist in the database")
        deleted_quote = database.pop(ID)
    except Exception as err:
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(error_message)
    return Ok(f"Successfully deleted {deleted_quote} from database.\nID: {ID}")


def update_raw_quotes(quotes: list[tuple[Quote, Quote]]) -> tuple[list[str], list[str]]:
    """Oppdaterer flere sitater samtidig

    Args:
        quotes (list[tuple[Quote, Quote]]): [ (gammelt sitat, nytt sitat) ]

    Returns:
        tuple[list[str], list[str]]: (Kvitteringer, Feilmeldinger)
    """
    reciepts = []
    errors = []
    for old_quote, new_quote in quotes:
        match get_quote_ID(old_quote):
            case Err(error_message):
                errors.append(error_message)
                continue
            case Ok(ID):
                old_quote_ID = ID

        match update_quote_in_database(old_quote_ID, new_quote):
            case Err(error):
                error_message = f"Kunne ikke oppdatere sitat {old_quote} grunnet: {{\n    {error}\n}}"
                errors.append(error_message)
            case Ok(reciept):
                reciepts.append(reciept)
    return reciepts, errors


def update_quotes(quotes: list[tuple[int, Quote]]) -> tuple[list[str], list[str]]:
    """oppdaterer flere sitat samtidig

    Args:
        quotes (list[tuple[int, Quote]]): [ (sitat-ID, nytt sitat) ]

    Returns:
        tuple[list[str], list[str]]: (Kvitteringer, Feilmeldinger)
    """
    reciepts = []
    errors = []
    for ID, new_quote in quotes:
        match update_quote_in_database(ID, new_quote):
            case Err(error):
                error_message = f"Kunne ikke oppdatere sitat {new_quote} grunnet: {{\n    {error}\n}}"
                errors.append(error_message)
            case Ok(reciept):
                reciepts.append(reciept)
    return reciepts, errors


def update_quote_in_database(quote_ID: int, new_quote: Quote) -> Result[str, str]:
    """Oppdater et sitat i databasen

    Args:
        quote_ID (int): ID-en til sitatet som skal endres
        new_quote (Quote): nytt sitat

    Returns:
        Result[str, str]: Ok(Kvittering) | Err(Feilmelding)
    """
    database: dict[int, dict] = {}
    new_database_entry = {
        "speaker": new_quote.speaker,
        "audience": new_quote.audience,
        "quote": new_quote.quote,
    }
    try:
        match database.get(quote_ID):
            case None:
                return Err(f"Entry {quote_ID} doesn't exist in the database")
            case old_quote:
                database[quote_ID] = new_database_entry
    except Exception as err:
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(error_message)
    return Ok(f"Successfully updated {quote_ID}.\n{old_quote} ==> {new_quote}")


def format_quotes(
    raw_quotes: str,
) -> Result[tuple[list[Quote], Optional[list[str]]], str]:
    """Formatterer sitatene

    Args:
        raw_quotes (str): hele rå-meldingen med sitater

    Returns:
        Result[tuple[list[Quote], str], str]: Ok( liste med sitat, advarsler ) | Err(Feilmeldinger)
    """
    quotes_list: list[Quote] = []
    warnings: list[str] = []
    raw_quotes_list = raw_quotes.strip().split("\n\n")
    for raw_quote in raw_quotes_list:
        quote = format_one_quote(raw_quote)
        match validate_quote(quote):
            case Err(err):
                error_message = create_validation_error_message(quote, raw_quote, err)
                return Err(error_message)
            case Ok(potential_warnings):
                if potential_warnings is not None:
                    warnings.extend(potential_warnings)
                quotes_list.append(quote)
    if len(warnings) == 0:
        return Ok((quotes_list, None))
    return Ok((quotes_list, warnings))


def create_validation_error_message(quote: Quote, raw_quote: str, error: str) -> str:
    quote_print_formatted = "\n    ".join(quote.quote.split("\n"))
    raw_quote_print_formatted = "\n  ".join(raw_quote.split("\n"))
    error_message = (
        "ERROR\n"
        + f'""{raw_quote_print_formatted}\n""'
        + "is not a valid quote.\n\n"
        + "[After formatting]\n"
        + f"Speaker: {quote.speaker}\n"
        + f"Audience: {quote.audience}\n"
        + f"Quote: {{\n    {quote_print_formatted}\n}}\n"
        + f"Error: {{\n    {error}\n}}\n\n"
        + "-" * 10
        + "\n\n"
    )
    return error_message


def format_one_quote(raw_quote: str) -> Quote:
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
    quote_obj = Quote(speaker, audience, "\n".join(quote))
    return quote_obj


def validate_quote(quote_obj: Quote) -> Result[Optional[list[str]], str]:
    """sjekker om et sitat er gyldig

    Args:
        speaker (str): forteller
        audience (list[str]): tilskuere
        quote (str): sitatet

    Returns:
        Result[Optional[str], str]: Ok(advarsel-flagg | None), Err(Feilmelding)
    """
    warnings: list[str] = []
    speaker = quote_obj.speaker
    audience = quote_obj.audience
    quote = quote_obj.quote

    if speaker == "":
        return Err("Speaker not found")
    if quote == "":
        return Err("Quote found")
    # TODO Legge til flere tilfeller av ugyldig input
    # TODO Legge til hjelpsomme flagg ved mistanke om skrivefeil; eks sitat uten hermetegn; er det egentlig et nytt sitat?
    if len(warnings) == 0:
        return Ok()
    return Ok(warnings)


def create_quote_ID() -> Result[int, str]:
    """Genererer sitat-ID

    Returns:
        Result[int, str]: Ok(sitat-ID) | Err(Feilmelding)
    """
    ID_str = os.getenv("next_quote_id")
    if ID_str is None or not ID_str.isalnum():
        return Err(f"Kan ikke generere sitat-ID. Kontakt {CONTACT_PERSON}")
    ID = int(ID_str)
    os.environ["next_quote_id"] = str(ID + random.randint(1, 10))
    return Ok(ID)


@dataclass
class Quote:
    speaker: str
    audience: list[str]
    quote: str
