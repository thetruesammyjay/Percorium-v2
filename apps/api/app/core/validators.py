import re

from app.core.exceptions import AppError

_BASE58_ADDRESS = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
_BASE58_SIGNATURE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{64,96}$")
_HANDLE = re.compile(r"^@[a-z0-9_]{3,24}$")
_NAME = re.compile(r"^[a-z0-9-]+\.(?:sol|sns)$")


def is_solana_address(value: str) -> bool:
    return bool(_BASE58_ADDRESS.fullmatch(value))


def validate_solana_address(value: str) -> str:
    if not isinstance(value, str) or not is_solana_address(value):
        raise ValueError("must be a valid Solana base58 address")
    return value


def require_solana_address(value: str, *, field: str = "address") -> str:
    if not is_solana_address(value):
        raise AppError(
            f"{field} must be a valid Solana base58 address.",
            code="invalid_solana_address",
            status_code=422,
            details={"field": field},
        )
    return value


def require_solana_signature(value: str, *, field: str = "signature") -> str:
    if not isinstance(value, str) or not _BASE58_SIGNATURE.fullmatch(value):
        raise AppError(
            f"{field} must be a valid Solana transaction signature.",
            code="invalid_transaction_signature",
            status_code=422,
            details={"field": field},
        )
    return value


def require_recipient_reference(value: str) -> str:
    normalized = value.strip().lower()
    if _HANDLE.fullmatch(normalized) or _NAME.fullmatch(normalized) or is_solana_address(normalized):
        return normalized
    raise AppError(
        "recipient_reference must be an @handle, .sol/.sns name, or Solana wallet address.",
        code="invalid_recipient_reference",
        status_code=422,
        details={"field": "recipient_reference"},
    )
