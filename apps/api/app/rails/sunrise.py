"""Sunrise official asset-list adapter boundary."""


class SunriseClient:
    def __init__(self, base_url: str | None, api_key: str | None) -> None:
        self.base_url = base_url
        self.api_key = api_key

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key)
