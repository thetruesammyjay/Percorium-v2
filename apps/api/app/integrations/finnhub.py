"""Finnhub-only news client boundary."""


class FinnhubClient:
    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key
