from __future__ import annotations
from typing import Optional
from result import Result, Err, Ok
from dataclasses import dataclass
import re


def get_quotes(args: str):
    pass


def add_quotes(quotes: str) -> Result[None, str]:
    pass


def add_one_quote(quote: str) -> Result[str, str]:
    pass


def remove_quotes() -> Result[str, str]:
    pass


def update_quote():
    pass


def sort_quotes(flags: str) -> list[str]:
    pass


def format_quotes(raw_quotes: str) -> Result[list[Quote], str]:
    """Formatterer sitatene

    Args:
        quotes (list[str]): _description_

    Returns:
        Optional[str]: _description_
    """
    quotes_list: list[Quote] = []
    raw_quotes_list = raw_quotes.strip().split("\n\n")
    for raw_quote in raw_quotes_list:
        speaker, audience, quote = format_one_quote(raw_quote)
        validation_result = validate_quote(speaker, audience, quote)
        if validation_result.is_err():
            return Err(
                f"{raw_quote} is not formatted properly:\n{validation_result.err()}"
            )

        quotes_list.append(Quote(speaker, audience, quote))
    return Ok(quotes_list)


def format_one_quote(raw_quote: str) -> tuple[str, list[str], str]:
    """formatterer et sitat fra en streng

    Args:
        quote (str): en streng med sitatet

    Returns:
        tuple[str, str, str]: [avsender , publikumet , sitat]
    """
    header, *quote = raw_quote.strip().split("\n")
    result = re.findall(r"\b(?!til|og)\b\w+", header)
    if len(result) == 0:
        speaker, audience = "", []
    else:
        speaker, *audience = result
    return speaker, audience, "\n".join(quote)


def validate_quote(speaker: str, audience: list[str], quote: str) -> Result[None, str]:
    pass


@dataclass
class Quote:
    speaker: str
    audience: list[str]
    quote: str
