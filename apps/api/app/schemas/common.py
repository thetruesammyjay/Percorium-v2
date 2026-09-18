from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StrictStr

from app.core.validators import validate_solana_address


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True, extra="forbid")


class RailName(StrEnum):
    SOLANA = "solana"
    BASE = "base"


class AssetKind(StrEnum):
    STOCK = "stock"
    ETF = "etf"
    PREIPO = "pre-ipo"
    MEMESTOCK = "memestock"


class TradeStatus(StrEnum):
    AWAITING_SIGNATURE = "awaiting_signature"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"


class OrderStatus(StrEnum):
    AWAITING_SIGNATURE = "awaiting_signature"
    SUBMITTED = "submitted"
    ACTIVE = "active"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"
    EXPIRED = "expired"


def normalize_atomic_amount(value: str) -> str:
    if not value.isascii() or not value.isdecimal():
        raise ValueError("amount must be a positive integer string in atomic units")
    normalized = value.lstrip("0") or "0"
    if normalized == "0":
        raise ValueError("amount must be greater than zero")
    if len(normalized) > 78:
        raise ValueError("amount is too large")
    return normalized


AtomicAmount = Annotated[StrictStr, AfterValidator(normalize_atomic_amount)]
SolanaAddress = Annotated[str, AfterValidator(validate_solana_address)]


class ApiStatus(APIModel):
    status: str
    message: str | None = None


class Pagination(APIModel):
    next_cursor: str | None = None
    limit: int = Field(default=50, ge=1, le=100)
