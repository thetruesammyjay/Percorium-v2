from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IdentityRecord, TradeIntentRecord
from app.schemas.social import LeaderboardItem, LeaderboardResponse


class SocialService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def leaderboard(
        self, period: Literal["24h", "7d"] = "24h", tab: Literal["stocks", "new"] = "stocks"
    ) -> LeaderboardResponse:
        hours = 24 if period == "24h" else 24 * 7
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = await self.session.execute(
            select(TradeIntentRecord)
            .where(
                TradeIntentRecord.status == "confirmed",
                TradeIntentRecord.tab == tab,
                TradeIntentRecord.is_private.is_(False),
                TradeIntentRecord.created_at >= cutoff,
            )
            .order_by(TradeIntentRecord.created_at.desc())
            .limit(10_000)
        )
        totals: dict[str, list[Decimal | int]] = defaultdict(lambda: [0, Decimal(0)])
        for trade in result.scalars().all():
            totals[trade.wallet][0] += 1
            totals[trade.wallet][1] += Decimal(trade.sell_amount)

        wallets = list(totals)
        identities: dict[str, IdentityRecord] = {}
        if wallets:
            identity_result = await self.session.execute(
                select(IdentityRecord).where(IdentityRecord.wallet.in_(wallets))
            )
            identities = {record.wallet: record for record in identity_result.scalars().all()}

        ranked = sorted(totals.items(), key=lambda pair: (-int(pair[1][0]), -pair[1][1]))
        items = [
            LeaderboardItem(
                rank=rank,
                handle=identities[wallet].handle,
                fills=int(values[0]),
                volume=str(values[1]),
                period=period,
            )
            for rank, (wallet, values) in enumerate(ranked, start=1)
            if wallet in identities
        ]
        return LeaderboardResponse(
            tab=tab,
            items=items[:100],
            period=period,
            message=None if items else "No public fills for this period.",
        )
