from dataclasses import dataclass

from fastapi import Depends, Header

from app.core.config import Settings
from app.core.dependencies import settings_dependency
from app.core.exceptions import AuthenticationError
from app.core.validators import require_solana_address


@dataclass(frozen=True)
class WalletPrincipal:
    wallet: str
    provider: str


async def get_wallet_principal(
    authorization: str | None = Header(default=None),
    x_wallet_address: str | None = Header(default=None),
    settings: Settings = Depends(settings_dependency),
) -> WalletPrincipal:
    """Resolve a wallet boundary.

    Production must verify the Privy bearer token and derive the wallet from the
    verified relationship. The development header bypass is intentionally gated
    by AUTH_REQUIRED=false and must never be enabled in production.
    """
    if authorization:
        raise AuthenticationError("Privy token verification is not wired yet; no wallet action was authorized.")
    if settings.auth_required or settings.is_production:
        raise AuthenticationError()
    if not x_wallet_address:
        raise AuthenticationError("Provide X-Wallet-Address for local development.")
    return WalletPrincipal(wallet=require_solana_address(x_wallet_address, field="wallet"), provider="development")
