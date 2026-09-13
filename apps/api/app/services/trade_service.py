from app.core.config import get_settings
from app.schemas.trades import TradeCreate, TradeResponse


def calculate_fee(amount_minor: int, fee_bps: int = 50) -> int:
    """Calculate a fee in the same minor unit, rounding up to avoid undercharging."""
    if amount_minor < 0 or fee_bps < 0:
        raise ValueError("amount_minor and fee_bps must be non-negative")
    return (amount_minor * fee_bps + 9_999) // 10_000


async def create_trade_intent(request: TradeCreate) -> TradeResponse:
    settings = get_settings()
    return TradeResponse(
        status="not_configured",
        rail=request.rail,
        fee_bps=settings.percorium_fee_bps,
        wallet=request.wallet,
        message="Trade intent created in scaffold mode; the wallet must sign the Sunrise transaction.",
    )
