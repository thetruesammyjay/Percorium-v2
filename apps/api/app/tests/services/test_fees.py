from app.services.trade_service import calculate_fee


def test_fee_is_50_bps_and_rounds_up() -> None:
    assert calculate_fee(100_000) == 500
    assert calculate_fee(1) == 1
