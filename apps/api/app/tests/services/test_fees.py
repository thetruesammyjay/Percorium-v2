import pytest

from app.services.fee_service import breakdown, calculate_fee


def test_fee_is_50_bps_and_rounds_up() -> None:
    assert calculate_fee(100_000) == 500
    assert calculate_fee(1) == 1


def test_copy_master_receives_ten_percent_of_platform_fee() -> None:
    result = breakdown(100_000, fee_bps=50, copy_master=True)
    assert result.platform_fee == 500
    assert result.copy_master_fee == 50
    assert result.percorium_fee == 450


def test_fee_rejects_negative_amounts() -> None:
    with pytest.raises(ValueError):
        calculate_fee(-1)
