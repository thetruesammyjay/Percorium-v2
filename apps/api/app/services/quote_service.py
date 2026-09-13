from app.core.config import get_settings
from app.schemas.quotes import QuoteRequest, QuoteResponse


async def create_quote(request: QuoteRequest) -> QuoteResponse:
    settings = get_settings()
    return QuoteResponse(
        status="not_configured",
        rail=request.rail,
        input_mint=request.input_mint,
        output_mint=request.output_mint,
        amount=request.amount,
        fee_bps=settings.percorium_fee_bps,
        message="Quote execution is scaffolded; configure Sunrise and Solana RPC credentials.",
    )
