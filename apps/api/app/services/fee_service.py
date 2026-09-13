from dataclasses import dataclass


@dataclass(frozen=True)
class FeeBreakdown:
    fee_bps: int
    platform_fee: int
    copy_master_fee: int = 0
    percorium_fee: int = 0


def calculate_fee(amount_minor: int, fee_bps: int = 50) -> int:
    """Calculate an integer-denominated fee and round up to avoid undercharging."""
    if amount_minor < 0:
        raise ValueError("amount_minor must be non-negative")
    if not 0 <= fee_bps <= 10_000:
        raise ValueError("fee_bps must be between 0 and 10000")
    return (amount_minor * fee_bps + 9_999) // 10_000


def breakdown(amount_minor: int, fee_bps: int = 50, copy_master: bool = False) -> FeeBreakdown:
    platform_fee = calculate_fee(amount_minor, fee_bps)
    copy_master_fee = calculate_fee(platform_fee, 1_000) if copy_master else 0
    return FeeBreakdown(
        fee_bps=fee_bps,
        platform_fee=platform_fee,
        copy_master_fee=copy_master_fee,
        percorium_fee=platform_fee - copy_master_fee,
    )
