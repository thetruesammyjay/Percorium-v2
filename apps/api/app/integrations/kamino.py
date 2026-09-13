"""Kamino market-discovery boundary.

The adapter is kept separate from portfolio and trade code so unsupported assets
can be hidden instead of represented as empty lending promises.
"""


class KaminoClient:
    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        self.api_url = api_url
        self.api_key = api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_url and self.api_key)
