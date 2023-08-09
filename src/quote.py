from dataclasses import dataclass

@dataclass
class Quote:
    speaker: str
    audience: list[str]
    quote: str
    message_id: int

    def __str__(self) -> str:
        return f"Quote(speaker='{self.speaker}', audience={self.audience}, quote='{self.quote}')"
