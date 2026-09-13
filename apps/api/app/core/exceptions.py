class IntegrationNotConfiguredError(RuntimeError):
    """Raised when an external rail or data provider has not been configured."""


class UnsupportedAssetError(ValueError):
    """Raised when an asset is not in the official Sunrise allowlist."""
