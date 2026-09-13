from fastapi import APIRouter

router = APIRouter()


@router.get("/leaderboard")
async def leaderboard() -> dict[str, list[object]]:
    return {"items": []}
