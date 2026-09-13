from fastapi import APIRouter

router = APIRouter()


@router.get("/{claim_id}")
async def get_gift(claim_id: str) -> dict[str, str]:
    return {"claim_id": claim_id, "status": "not_configured"}
