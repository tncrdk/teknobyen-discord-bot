from __future__ import annotations
from typing import Optional
from result import Result, Err, Ok


def get_quotes(args: str):
    pass


def add_quotes(quotes: str) -> Optional[ValueError]:
    pass


def add_one_quote(quote: str) -> Result[str, str]:
    pass


def remove_quotes() -> Result[str, str]:
    pass


def update_quote():
    pass


def sort_quotes(flags: str) -> list[str]:
    pass


def format_quotes(quotes: str) -> Result[dict[str, list[str]], str]:
    """Formatterer sitatene

    Args:
        quotes (list[str]): _description_

    Returns:
        Optional[str]: _description_
    """
    quotes_list = quotes.strip().split("\n\n")
    trimmed_quotes_list = [i.strip() for i in quotes_list]
