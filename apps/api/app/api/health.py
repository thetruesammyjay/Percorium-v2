from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.core.dependencies import settings_dependency
from app.db.session import check_database

router = APIRouter()


@router.get("/health")
async def health(settings: Settings = Depends(settings_dependency)) -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "solana_first": True,
        "base_enabled": settings.base_enabled,
    }


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(response: Response) -> dict[str, str | bool]:
    try:
        await check_database()
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "database": False}
    return {"status": "ready", "database": True}
