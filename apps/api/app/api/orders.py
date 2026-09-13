from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_orders() -> dict[str, list[object]]:
    return {"items": []}
