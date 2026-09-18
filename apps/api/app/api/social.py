from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import database_session
from app.schemas.social import LeaderboardResponse
from app.services.social_service import SocialService

router = APIRouter()


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def leaderboard(
    period: Literal["24h", "7d"] = Query(default="24h"),
    tab: Literal["stocks", "new"] = Query(default="stocks"),
    session: AsyncSession = Depends(database_session),
) -> LeaderboardResponse:
    return await SocialService(session).leaderboard(period, tab)
