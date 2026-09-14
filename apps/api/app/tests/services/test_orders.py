import pytest
from pydantic import ValidationError

from app.schemas.orders import OrderCreate

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGkZwyTDt1v"
WALLET = "11111111111111111111111111111111"


def test_limit_order_requires_a_limit_price() -> None:
    with pytest.raises(ValidationError):
        OrderCreate(
            wallet=WALLET,
            input_mint=USDC_MINT,
            output_mint=SOL_MINT,
            amount="1000000",
            order_type="limit",
        )


def test_dca_order_requires_schedule() -> None:
    with pytest.raises(ValidationError):
        OrderCreate(
            wallet=WALLET,
            input_mint=USDC_MINT,
            output_mint=SOL_MINT,
            amount="1000000",
            order_type="dca",
        )


def test_dca_order_accepts_valid_schedule() -> None:
    order = OrderCreate(
        wallet=WALLET,
        input_mint=USDC_MINT,
        output_mint=SOL_MINT,
        amount="1000000",
        order_type="dca",
        interval_seconds=3600,
        occurrences=12,
    )
    assert order.amount == "1000000"
