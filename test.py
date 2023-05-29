import time

err = Exception("Foo")
raw_quote = "Olav\nHello World\nHade"
quote = "Hello World\nHade"
speaker = "Olav"
audience = ["Gjengen"]

with open("test.txt", "a") as log_file:
    quote_print_formatted = "\n    ".join(quote.split("\n"))
    raw_quote_print_formatted = "\n  ".join(raw_quote.split("\n"))
    message = (
        f"ERROR\n"
        + f'""{raw_quote_print_formatted}\n""'
        + f"is not a valid quote.\n\n"
        + f"[After formatting]\n"
        + f"Speaker: {speaker}\n"
        + f"Audience: {audience}\n"
        + f"Quote: {{\n    {quote_print_formatted}\n}}\n"
        + f"Err: {{\n    {err}\n}}\n\n"
        + "-" * 10
        + "\n\n"
    )
    log_file.write(message)
