from fastapi import APIRouter
from pydantic import Field

from app.core.exceptions import AppError
from app.schemas.common import APIModel, SolanaAddress

router = APIRouter()


class LaunchCreate(APIModel):
    wallet: SolanaAddress
    name: str = Field(min_length=1, max_length=32)
    symbol: str = Field(min_length=1, max_length=10, pattern=r"^[A-Za-z0-9]+$")
    description: str = Field(default="", max_length=500)
    metadata_uri: str = Field(min_length=1, max_length=200, pattern=r"^https://")
    quote_mint: SolanaAddress


@router.get("/capabilities")
async def capabilities() -> dict:
    return {
        "create_enabled": False,
        "reason": "Launch creation is not available yet.",
        "fee_lamports": None,
    }


@router.post("", status_code=503)
async def create_launch(request: LaunchCreate) -> None:
    # Fail closed until the official program, platform config, instruction layout,
    # and creation fee are verified. Never return a guessed signing payload.
    raise AppError("Launch creation is not available yet.", code="launch_creation_unavailable", status_code=503)
