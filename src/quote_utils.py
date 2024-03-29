from __future__ import annotations
from result import Result, Err, Ok
from database import Database
from quote import Quote
from error import (
    DatabaseError,
    DuplicateQuoteError,
    FormatError,
    BaseError,
    create_error,
)

CONTACT_PERSON = "Thorbjørn Djupvik"


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
        match database.create_new_quote_ID():
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
    raw_quotes_list = []
    acc_raw_quote = []
    for i in raw_quotes.strip().split("\n"):
        if i.strip() == "":
            raw_quotes_list.append("\n".join(acc_raw_quote))
            acc_raw_quote = []
        else:
            acc_raw_quote.append(i)
    raw_quotes_list.append("\n".join(acc_raw_quote))

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
        + f"Error: {{\n    {error.msg}\n}}"
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
    header, *quote_elements = raw_quote.strip().split("\n")
    header_names = (
        remove_quotation_marks(header)
        .replace(" til ", " , ", 1)
        .replace(", og ", " og ")
        .replace(",og ", " og ")
        .replace(" og ", " , ")
        .replace("  ", " ")
        .split(",")
    )
    header_names = [header.strip() for header in header_names]
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

    for audience_member in audience:
        if audience_member == "":
            return Err(FormatError("Audience-member can not be an empty string"))

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


def remove_quotation_marks(raw_string: str) -> str:
    chars = [
        "'",
        '"',
        "«",
        "»",
        "‹",
        "›",
        "„",
        "“",
        "‟",
        "”",
        "’",
        "❝",
        "❞",
        "⹂",
        "‚",
        "‘",
        "‛",
        "❛",
        "❜",
        "❟",
    ]
    for char in chars:
        raw_string = raw_string.strip(char)
    return raw_string


def present_quote(quote: Quote) -> str:
    message = ""
    message += f"{quote.quote}\n[{quote.speaker}"
    for i in range(len(quote.audience)):
        if i == 0:
            message += f" til {quote.audience[i]}"
        elif i == len(quote.audience) - 1:
            message += f" og {quote.audience[i]}"
        else:
            message += f", {quote.audience[i]}"
    message += "]"

    return message
