from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel, AtomicAmount


class GiftCreate(APIModel):
    sender_wallet: str = Field(min_length=32, max_length=64)
    asset_mint: str = Field(min_length=1, max_length=64)
    amount: AtomicAmount
    recipient_reference: str = Field(min_length=2, max_length=255)


class GiftResponse(APIModel):
    claim_code: str
    asset_mint: str
    amount: AtomicAmount
    recipient_reference: str
    status: str
    expires_at: datetime
