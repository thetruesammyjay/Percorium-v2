"""Hidden Base rail boundary retained for later re-enablement."""


class BaseRail:
    name = "base"

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled
