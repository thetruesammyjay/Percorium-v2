from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class AssetRecord(Base):
    __tablename__ = "assets"
    __table_args__ = (Index("ix_assets_symbol", "symbol"), Index("ix_assets_kind", "kind"))

    mint: Mapped[str] = mapped_column(String(64), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(24), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tradable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class TradeIntentRecord(Base):
    __tablename__ = "trade_intents"
    __table_args__ = (
        UniqueConstraint("wallet", "idempotency_key", name="uq_trade_wallet_idempotency"),
        Index("ix_trade_intents_status", "status"),
        Index("ix_trade_intents_wallet_created", "wallet", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    wallet: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    rail: Mapped[str] = mapped_column(String(16), nullable=False)
    tab: Mapped[str] = mapped_column(String(16), nullable=False, default="stocks")
    sell_mint: Mapped[str] = mapped_column(String(64), nullable=False)
    buy_mint: Mapped[str] = mapped_column(String(64), nullable=False)
    sell_amount: Mapped[str] = mapped_column(String(128), nullable=False)
    expected_buy_amount: Mapped[str | None] = mapped_column(String(128))
    price_impact_bps: Mapped[int | None] = mapped_column(Integer)
    fee_bps: Mapped[int] = mapped_column(Integer, nullable=False)
    platform_fee: Mapped[str] = mapped_column(String(128), nullable=False)
    copy_master_fee: Mapped[str] = mapped_column(String(128), nullable=False, default="0")
    percorium_fee: Mapped[str] = mapped_column(String(128), nullable=False, default="0")
    network_fee: Mapped[str | None] = mapped_column(String(128))
    total_debit: Mapped[str] = mapped_column(String(128), nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="awaiting_signature")
    transaction_payload: Mapped[str | None] = mapped_column(Text)
    tx_signature: Mapped[str | None] = mapped_column(String(128))
    external_id: Mapped[str | None] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class OrderIntentRecord(Base):
    __tablename__ = "order_intents"
    __table_args__ = (
        UniqueConstraint("wallet", "idempotency_key", name="uq_order_wallet_idempotency"),
        Index("ix_order_intents_wallet_created", "wallet", "created_at"),
        Index("ix_order_intents_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    wallet: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    rail: Mapped[str] = mapped_column(String(16), nullable=False)
    tab: Mapped[str] = mapped_column(String(16), nullable=False, default="stocks")
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    input_mint: Mapped[str] = mapped_column(String(64), nullable=False)
    output_mint: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[str] = mapped_column(String(128), nullable=False)
    limit_price: Mapped[str | None] = mapped_column(String(64))
    interval_seconds: Mapped[int | None] = mapped_column(Integer)
    occurrences: Mapped[int | None] = mapped_column(Integer)
    fee_bps: Mapped[int] = mapped_column(Integer, nullable=False)
    platform_fee: Mapped[str] = mapped_column(String(128), nullable=False)
    total_debit: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="awaiting_signature")
    transaction_payload: Mapped[str | None] = mapped_column(Text)
    provider_order_id: Mapped[str | None] = mapped_column(String(255))
    tx_signature: Mapped[str | None] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class BasketRecord(Base):
    __tablename__ = "baskets"
    __table_args__ = (Index("ix_baskets_public_created", "is_public", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_wallet: Mapped[str | None] = mapped_column(String(64))
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    items_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class GiftClaimRecord(Base):
    __tablename__ = "gift_claims"
    __table_args__ = (
        UniqueConstraint("sender_wallet", "idempotency_key", name="uq_gift_sender_idempotency"),
        Index("ix_gift_claims_status_expires", "status", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    claim_code: Mapped[str] = mapped_column(String(96), unique=True, nullable=False)
    sender_wallet: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_mint: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class IdentityRecord(Base):
    __tablename__ = "identities"

    wallet: Mapped[str] = mapped_column(String(64), primary_key=True)
    handle: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    sns_name: Mapped[str | None] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class WatchlistRecord(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (
        UniqueConstraint("wallet", "mint", name="uq_watchlist_wallet_mint"),
        Index("ix_watchlist_wallet_created", "wallet", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    wallet: Mapped[str] = mapped_column(String(64), nullable=False)
    mint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class NewsCacheRecord(Base):
    __tablename__ = "news_cache"

    cache_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(24), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
