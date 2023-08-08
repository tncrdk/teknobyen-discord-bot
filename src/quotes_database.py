from __future__ import annotations
from typing import Iterable, Optional
from result import Result, Err, Ok
from dataclasses import dataclass
from replit.database.database import Database
import dotenv
from error import (
    DatabaseError,
    FormatError,
    BaseError,
    create_error,
)
import re
import os

CONTACT_PERSON = "Thorbjørn Djupvik"
DOTENV_FILE = dotenv.find_dotenv()

def get_quote_IDs(quotes: list[Quote], database: Database) -> tuple[list[int], list[BaseError]]:
    """
    @return:
        ( [ID] , [Error] )
    """
    ID_list: list[int] = []
    errors: list[BaseError] = []

    for quote in quotes:
        match get_quote_ID(quote, database):
            case Err(err):
                errors.append(err)
            case Ok(ID):
                ID_list.append(ID)

    return ID_list, errors

def get_quote_ID(quote: Quote, database: Database) -> Result[int, BaseError]:
    database_entry = {
        "speaker": quote.speaker,
        "quote": quote.quote,
        "audience": quote.audience,
    }
    try:
        for ID, quote_entry in database.items():
            if quote_entry == database_entry:
                return Ok(int(ID))
        return create_error(f"Dette sitatet finnes ikke i databasen, {quote}")
    except Exception as err:
        error_message = f"{str(err)}.\nKontakt {CONTACT_PERSON}"
        return Err(DatabaseError(error_message))


def add_quotes(
    quotes: list[Quote], database: Database
) -> tuple[list[str], list[BaseError]]:
    """legge til flere sitater til databasen

    Args:
        quotes (list[Quote]): liste med sitat

    Returns:
        tuple[list[str], list[str]]: (Kvitteringer, Feilmeldinger)
    """
    errors: list[BaseError] = []
    reciepts: list[str] = []
    for quote in quotes:
        match add_quote_to_database(quote, database):
            case Err(err):
                error_message = f"{quote} ble ikke lagt til i databasen grunnet feil: {{\n    {err.msg}\n}}"
                error_type = type(err)
                errors.append(error_type(error_message))
                continue
            case Ok(reciept):
                reciepts.append(reciept)
    return reciepts, errors


def add_quote_to_database(quote: Quote, database: Database) -> Result[str, BaseError]:
    database_entry = {
        "speaker": quote.speaker,
        "quote": quote.quote,
        "audience": quote.audience,
    }
    try:
        if database_entry in database.values():
            return create_error(f"{quote} finnes allerede i databasen")

        match create_quote_ID():
            case Err(error_message):
                return Err(error_message)
            case Ok(ID):
                database[str(ID)] = database_entry
    except Exception as err:
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(DatabaseError(error_message))

    return Ok(f"Successfully added {quote} to the database")


def remove_quotes(
    quotes_IDs: list[int], database: Database
) -> tuple[list[str], list[BaseError]]:
    """Fjern flere sitat på en gang

    Args:
        quotes_IDs (list[int]): Sitat-IDer

    Returns:
        tuple[list[str], list[str]]: (Kvitteringer, Feilmeldinger)
    """
    errors: list[BaseError] = []
    reciepts: list[str] = []
    for quote_ID in quotes_IDs:
        match remove_quote_from_database(quote_ID, database):
            case Err(err):
                error_message = (
                    f"Kunne ikke slette sitat {quote_ID} grunnet: {{\n    {err.msg}\n}}"
                )
                error_type = type(err)
                errors.append(error_type(error_message))
                continue
            case Ok(reciept):
                reciepts.append(reciept)

    return reciepts, errors


def remove_quote_from_database(ID: int, database: Database) -> Result[str, BaseError]:
    """Sletter et sitat i databasen

    Args:
        ID (int): ID-en til sitatet som skal slettes

    Returns:
        Result[str, str]: Ok(Kvittering) | Err(Feilmelding)
    """
    try:
        if str(ID) not in database:
            return create_error(f"Entry {ID} doesn't exist in the database")
        deleted_quote = database.pop(str(ID))
    except Exception as err:
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(DatabaseError(error_message))
    return Ok(f"Successfully deleted {deleted_quote} from database.\nID: {ID}")


def update_quotes(
    quotes: Iterable[tuple[Quote, Quote]], database: Database
) -> tuple[list[str], list[BaseError]]:
    """Oppdaterer flere sitater samtidig

    Args:
        quotes (list[tuple[Quote, Quote]]): [ (gammelt sitat, nytt sitat) ]

    Returns:
        tuple[list[str], list[BaseError]]: (Kvitteringer, Feilmeldinger)
    """
    reciepts: list[str] = []
    errors: list[BaseError] = []
    for old_quote, new_quote in quotes:
        match get_quote_ID(old_quote, database):
            case Err(error):
                errors.append(error)
                continue
            case Ok(ID):
                quote_ID = ID

        match update_quote_in_database(quote_ID, new_quote, database):
            case Err(error):
                error_type = type(error)
                error = error_type(
                    f"Kunne ikke oppdatere sitat {old_quote} grunnet: {{\n    {error.msg}\n}}"
                )
                errors.append(error)
            case Ok(reciept):
                reciepts.append(reciept)
    return reciepts, errors


def update_quotes_by_ID(
    quotes: list[tuple[int, Quote]], database: Database
) -> tuple[list[str], list[BaseError]]:
    """oppdaterer flere sitat samtidig

    Args:
        quotes (list[tuple[int, Quote]]): [ (sitat-ID, nytt sitat) ]

    Returns:
        tuple[list[str], list[str]]: (Kvitteringer, Feilmeldinger)
    """
    reciepts: list[str] = []
    errors: list[BaseError] = []
    for ID, new_quote in quotes:
        match update_quote_in_database(ID, new_quote, database):
            case Err(error):
                error_message = f"Kunne ikke oppdatere sitat {new_quote} grunnet: {{\n    {error.msg}\n}}"
                errors.append(BaseError(error_message))
            case Ok(reciept):
                reciepts.append(reciept)
    return reciepts, errors


def update_quote_in_database(
    quote_ID: int, new_quote: Quote, database: Database
) -> Result[str, BaseError]:
    """Oppdater et sitat i databasen

    Args:
        quote_ID (int): ID-en til sitatet som skal endres
        new_quote (Quote): nytt sitat

    Returns:
        Result[str, str]: Ok(Kvittering) | Err(Feilmelding)
    """
    new_database_entry = {
        "speaker": new_quote.speaker,
        "audience": new_quote.audience,
        "quote": new_quote.quote,
    }
    try:
        match database.get(str(quote_ID)):
            case None:
                return create_error(f"Entry {quote_ID} doesn't exist in the database")
            case old_quote:
                database[str(quote_ID)] = new_database_entry
    except Exception as err:
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(DatabaseError(error_message))
    return Ok(f"Successfully updated {quote_ID}.\n{old_quote} ==>\n{new_quote}")


def format_quotes(
    raw_quotes: str,
) -> Result[tuple[list[Quote], list[BaseError]], BaseError]:
    """Formatterer sitatene

    Args:
        raw_quotes (str): hele rå-meldingen med sitater

    Returns:
        Result[tuple[list[Quote], list[BaseError]], BaseError]: Ok( [sitater], [advarsler] ) | Err(Feilmelding)
    """
    quotes_list: list[Quote] = []
    warnings: list[BaseError] = []
    raw_quotes_list = raw_quotes.strip().split("\n\n\n")
    for raw_quote in raw_quotes_list:
        quote = format_one_quote(raw_quote)
        match validate_quote(quote):
            case Err(err):
                error_message = create_validation_error_message(quote, raw_quote, err)
                return Err(FormatError(error_message))
            case Ok(new_warnings):
                warnings.extend(new_warnings)
                quotes_list.append(quote)
    return Ok((quotes_list, warnings))


def create_validation_error_message(
    quote: Quote, raw_quote: str, error: BaseError
) -> str:
    quote_print_formatted = "\n    ".join(quote.quote.split("\n"))
    raw_quote_print_formatted = "\n  ".join(raw_quote.split("\n"))
    if type(error) == BaseError:
        error_name = "Error"
    else:
        error_name = type(error).__name__

    error_message = (
        "-" * 10
        + f"\n{error_name}\n"
        + f'""\n{raw_quote_print_formatted}\n""\n'
        + "is not a valid quote.\n\n"
        + "[After formatting]\n"
        + f"Speaker: {quote.speaker}\n"
        + f"Audience: {quote.audience}\n"
        + f"Quote: {{\n    {quote_print_formatted}\n}}\n\n"
        + f"Error: {{\n    {error.msg}\n}}\n\n"
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


def validate_quote(quote_obj: Quote) -> Result[list[BaseError], BaseError]:
    """sjekker om et sitat er gyldig

    Args:
        speaker (str): forteller
        audience (list[str]): tilskuere
        quote (str): sitatet

    Returns:
        Result[list[BaseError], BaseError]: Ok(advarsel-flagg), Err(Feilmelding)
    """
    warnings: list[BaseError] = []
    speaker = quote_obj.speaker
    audience = quote_obj.audience
    quote = quote_obj.quote

    if speaker == "":
        return Err(FormatError("Speaker not found"))
    if quote == "":
        return Err(FormatError("Quote not found"))
    # TODO Legge til flere tilfeller av ugyldig input
    # TODO Legge til hjelpsomme flagg ved mistanke om skrivefeil; eks sitat uten hermetegn; er det egentlig et nytt sitat?
    return Ok(warnings)


def create_quote_ID() -> Result[int, BaseError]:
    """Genererer sitat-ID

    Returns:
        Result[int, str]: Ok(sitat-ID) | Err(Feilmelding)
    """
    dotenv.load_dotenv(override=True)

    env_name = "next_quote_id"
    ID_str = os.getenv(env_name)
    if ID_str is None or not ID_str.isalnum():
        return create_error(f"Kan ikke generere sitat-ID. Kontakt {CONTACT_PERSON}")
    ID = int(ID_str)
    dotenv.set_key(DOTENV_FILE, env_name, str(ID + 1))
    return Ok(ID)


@dataclass
class Quote:
    speaker: str
    audience: list[str]
    quote: str
