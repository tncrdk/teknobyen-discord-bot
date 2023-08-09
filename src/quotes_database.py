from __future__ import annotations
from typing import Iterable, Optional
from result import Result, Err, Ok
from database import Database
from pathlib import Path
from quote import Quote
from error import (
    DatabaseError,
    DuplicateQuoteError,
    FormatError,
    BaseError,
    create_error,
)
import re

CONTACT_PERSON = "Thorbjørn Djupvik"
ID_FILE = Path(".ID")


def get_quote_IDs(
    quotes: list[Quote], database: Database[Quote]
) -> tuple[list[int], list[BaseError]]:
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


def get_quote_ID(quote: Quote, database: Database[Quote]) -> Result[int, BaseError]:
    try:
        for ID, quote_entry in database.items():
            if quote_entry == quote:
                return Ok(ID)
        return create_error(f"Dette sitatet finnes ikke i databasen, {quote}")
    except Exception as err:
        error_message = f"{str(err)}.\nKontakt {CONTACT_PERSON}"
        return Err(DatabaseError(error_message))


def add_quotes(
    quotes: list[Quote], database: Database[Quote]
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


def add_quote_to_database(
    quote: Quote, database: Database[Quote]
) -> Result[str, BaseError]:
    match validate_quote(quote, database):
        case Err(err):
            return Err(err)
        case Ok(None):
            pass

    try:
        match create_quote_ID():
            case Err(error_message):
                return Err(error_message)
            case Ok(ID):
                database.set_value(ID, quote)
    except Exception as err:
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(DatabaseError(error_message))

    return Ok(f"Successfully added {quote} to the database")


def remove_quotes(
    quotes_IDs: list[int], database: Database[Quote]
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


def remove_quote_from_database(
    ID: int, database: Database[Quote]
) -> Result[str, BaseError]:
    """Sletter et sitat i databasen

    Args:
        ID (int): ID-en til sitatet som skal slettes

    Returns:
        Result[str, str]: Ok(Kvittering) | Err(Feilmelding)
    """
    try:
        if ID not in database.keys():
            return create_error(f"Entry {ID} doesn't exist in the database")
        deleted_quote = database.pop(ID)
    except Exception as err:
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(DatabaseError(error_message))
    return Ok(f"Successfully deleted {deleted_quote} from database.\nID: {ID}")


def update_quotes(
    quotes: Iterable[tuple[Quote, Quote]], database: Database[Quote]
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
    quotes: list[tuple[int, Quote]], database: Database[Quote]
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
    quote_ID: int, new_quote: Quote, database: Database[Quote]
) -> Result[str, BaseError]:
    """Oppdater et sitat i databasen

    Args:
        quote_ID (int): ID-en til sitatet som skal endres
        new_quote (Quote): nytt sitat

    Returns:
        Result[str, str]: Ok(Kvittering) | Err(Feilmelding)
    """
    match validate_quote(new_quote, database):
        case Err(err):
            return Err(err)
        case Ok(None):
            pass

    try:
        match database.get(quote_ID):
            case None:
                return create_error(f"Entry {quote_ID} doesn't exist in the database")
            case old_quote:
                database.set_value(quote_ID, new_quote)
    except Exception as err:
        error_message = f"{str(err)}\nKontakt {CONTACT_PERSON}"
        return Err(DatabaseError(error_message))
    return Ok(f"Successfully updated {quote_ID}.\n{old_quote} ==>\n{new_quote}")


def format_quotes(
    raw_quotes: str, message_id: int
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
        quote = format_one_quote(raw_quote, message_id)
        match validate_quote_format(quote):
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


def format_one_quote(raw_quote: str, message_id: int) -> Quote:
    """formatterer et sitat fra en streng

    Args:
        quote (str): en streng med sitatet

    Returns:
        tuple[str, list[str], str]: [avsender , publikumet , sitat]
    """
    # TODO: Fjerne dobbel mellomrom o.l.
    header, *quote_elements = raw_quote.strip().split("\n")
    header_names = re.findall(r"\b(?!til|og)\b[\w\-_]+", header)
    if len(header_names) == 0:
        speaker, audience = "", []
    else:
        speaker, *audience = header_names
    quote_elements = [elem.strip() for elem in quote_elements]
    quote_obj = Quote(speaker, audience, "\n".join(quote_elements), message_id)
    return quote_obj


def validate_quote_format(quote_obj: Quote) -> Result[list[BaseError], BaseError]:
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

    # TODO: Legge til flere tilfeller av ugyldig input
    # TODO: Legge til hjelpsomme flagg ved mistanke om skrivefeil; eks sitat uten hermetegn; er det egentlig et nytt sitat?
    return Ok(warnings)


def validate_quote(quote: Quote, database: Database) -> Result[None, BaseError]:
    if quote_is_in_database(quote, database):
        return Err(DuplicateQuoteError(f"{quote} finnes allerede i databasen"))
    return Ok(None)


def quote_is_in_database(quote: Quote, database: Database[Quote]) -> bool:
    for quote_entry in database.values():
        if (
            quote.speaker == quote_entry.speaker
            and quote.audience == quote_entry.audience
            and quote.quote == quote_entry.quote
        ):
            return True
    return False


def create_quote_ID() -> Result[int, BaseError]:
    """Genererer sitat-ID

    Returns:
        Result[int, str]: Ok(sitat-ID) | Err(Feilmelding)
    """
    ID = 0
    match read_quote_ID(ID_FILE):
        case Ok(ID_value) if ID_value is not None:
            ID = ID_value
        case Err(err):
            return Err(err)

    match update_next_quote_ID(ID_FILE, ID):
        case Err(err):
            return Err(err)

    return Ok(ID)


def read_quote_ID(file_path: Path) -> Result[Optional[int], BaseError]:
    if Path.is_file(file_path):
        try:
            with open(file_path, "r+") as file:
                ID_str = file.read().strip()

            if ID_str is None or not ID_str.isdigit():
                return create_error(
                    f"Kan ikke generere sitat-ID. Kontakt {CONTACT_PERSON}"
                )
            return Ok(int(ID_str))
        except Exception as err:
            return create_error(str(err))
    return Ok(None)


def update_next_quote_ID(filepath: Path, current_ID: int) -> Result[None, BaseError]:
    try:
        with open(filepath, "w+") as file:
            file.write(str(current_ID + 1))
    except Exception as err:
        return create_error(str(err))
    return Ok(None)
