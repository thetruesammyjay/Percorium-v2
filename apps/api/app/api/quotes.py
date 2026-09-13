from fastapi import APIRouter

from app.schemas.quotes import QuoteRequest, QuoteResponse
from app.services.quote_service import create_quote

router = APIRouter()


@router.post("", response_model=QuoteResponse)
async def quote(request: QuoteRequest) -> QuoteResponse:
    return await create_quote(request)
