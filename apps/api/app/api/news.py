from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def news() -> dict[str, list[object]]:
    return {"items": []}
