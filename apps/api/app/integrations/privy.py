"""Privy identity and wallet authentication boundary."""


class PrivyClient:
    def __init__(self, app_id: str | None, app_secret: str | None) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
