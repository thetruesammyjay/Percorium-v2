from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_identity() -> dict[str, None]:
    return {"handle": None, "sns": None}
