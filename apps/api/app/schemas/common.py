from typing import Literal

from pydantic import BaseModel

RailName = Literal["solana", "base"]
AssetKind = Literal["stock", "etf"]


class ApiStatus(BaseModel):
    status: str
    message: str | None = None
