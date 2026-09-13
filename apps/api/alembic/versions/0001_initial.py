"""Create the initial Percorium API schema.

Revision ID: 0001_initial
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("mint", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=24), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("tradable", sa.Boolean(), nullable=False),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("mint"),
    )
    op.create_index("ix_assets_symbol", "assets", ["symbol"])
    op.create_index("ix_assets_kind", "assets", ["kind"])

    op.create_table(
        "trade_intents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("wallet", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("rail", sa.String(length=16), nullable=False),
        sa.Column("sell_mint", sa.String(length=64), nullable=False),
        sa.Column("buy_mint", sa.String(length=64), nullable=False),
        sa.Column("sell_amount", sa.String(length=128), nullable=False),
        sa.Column("expected_buy_amount", sa.String(length=128), nullable=True),
        sa.Column("price_impact_bps", sa.Integer(), nullable=True),
        sa.Column("fee_bps", sa.Integer(), nullable=False),
        sa.Column("platform_fee", sa.String(length=128), nullable=False),
        sa.Column("copy_master_fee", sa.String(length=128), nullable=False),
        sa.Column("percorium_fee", sa.String(length=128), nullable=False),
        sa.Column("network_fee", sa.String(length=128), nullable=True),
        sa.Column("total_debit", sa.String(length=128), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("transaction_payload", sa.Text(), nullable=True),
        sa.Column("tx_signature", sa.String(length=128), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("wallet", "idempotency_key", name="uq_trade_wallet_idempotency"),
    )
    op.create_index("ix_trade_intents_status", "trade_intents", ["status"])
    op.create_index("ix_trade_intents_wallet_created", "trade_intents", ["wallet", "created_at"])

    op.create_table(
        "order_intents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("wallet", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("rail", sa.String(length=16), nullable=False),
        sa.Column("order_type", sa.String(length=16), nullable=False),
        sa.Column("input_mint", sa.String(length=64), nullable=False),
        sa.Column("output_mint", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.String(length=128), nullable=False),
        sa.Column("limit_price", sa.String(length=64), nullable=True),
        sa.Column("interval_seconds", sa.Integer(), nullable=True),
        sa.Column("occurrences", sa.Integer(), nullable=True),
        sa.Column("fee_bps", sa.Integer(), nullable=False),
        sa.Column("platform_fee", sa.String(length=128), nullable=False),
        sa.Column("total_debit", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("transaction_payload", sa.Text(), nullable=True),
        sa.Column("provider_order_id", sa.String(length=255), nullable=True),
        sa.Column("tx_signature", sa.String(length=128), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("wallet", "idempotency_key", name="uq_order_wallet_idempotency"),
    )
    op.create_index("ix_order_intents_wallet_created", "order_intents", ["wallet", "created_at"])
    op.create_index("ix_order_intents_status", "order_intents", ["status"])

    op.create_table(
        "baskets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_wallet", sa.String(length=64), nullable=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("items_json", sa.Text(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_baskets_public_created", "baskets", ["is_public", "created_at"])

    op.create_table(
        "gift_claims",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("claim_code", sa.String(length=96), nullable=False),
        sa.Column("sender_wallet", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("recipient_reference", sa.String(length=255), nullable=False),
        sa.Column("asset_mint", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("claim_code"),
        sa.UniqueConstraint("sender_wallet", "idempotency_key", name="uq_gift_sender_idempotency"),
    )
    op.create_index("ix_gift_claims_status_expires", "gift_claims", ["status", "expires_at"])

    op.create_table(
        "identities",
        sa.Column("wallet", sa.String(length=64), nullable=False),
        sa.Column("handle", sa.String(length=32), nullable=False),
        sa.Column("sns_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("wallet"),
        sa.UniqueConstraint("handle"),
        sa.UniqueConstraint("sns_name"),
    )

    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("wallet", sa.String(length=64), nullable=False),
        sa.Column("mint", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("wallet", "mint", name="uq_watchlist_wallet_mint"),
    )
    op.create_index("ix_watchlist_wallet_created", "watchlist_items", ["wallet", "created_at"])

    op.create_table(
        "news_cache",
        sa.Column("cache_key", sa.String(length=255), nullable=False),
        sa.Column("symbol", sa.String(length=24), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("cache_key"),
    )


def downgrade() -> None:
    op.drop_table("news_cache")
    op.drop_index("ix_watchlist_wallet_created", table_name="watchlist_items")
    op.drop_table("watchlist_items")
    op.drop_table("identities")
    op.drop_index("ix_gift_claims_status_expires", table_name="gift_claims")
    op.drop_table("gift_claims")
    op.drop_index("ix_baskets_public_created", table_name="baskets")
    op.drop_table("baskets")
    op.drop_index("ix_order_intents_status", table_name="order_intents")
    op.drop_index("ix_order_intents_wallet_created", table_name="order_intents")
    op.drop_table("order_intents")
    op.drop_index("ix_trade_intents_wallet_created", table_name="trade_intents")
    op.drop_index("ix_trade_intents_status", table_name="trade_intents")
    op.drop_table("trade_intents")
    op.drop_index("ix_assets_kind", table_name="assets")
    op.drop_index("ix_assets_symbol", table_name="assets")
    op.drop_table("assets")
