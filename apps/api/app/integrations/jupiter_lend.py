"""Jupiter Lend market-discovery boundary.

Lend/borrow availability is intentionally exposed only when a configured provider
returns a supported market. No market is inferred from an asset ticker.
"""


class JupiterLendClient:
    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        self.api_url = api_url
        self.api_key = api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_url and self.api_key)
