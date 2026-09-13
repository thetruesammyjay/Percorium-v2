from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_baskets() -> dict[str, list[object]]:
    return {"items": []}


@router.post("")
async def create_basket() -> dict[str, str]:
    return {"status": "not_configured", "message": "Basket persistence is not configured yet."}
