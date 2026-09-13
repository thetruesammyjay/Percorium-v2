from fastapi import APIRouter

router = APIRouter()


@router.get("/manifest")
async def manifest() -> dict[str, list[str]]:
    return {"tools": ["list", "quote", "swap", "gift", "basket", "copy_once", "balances"]}
