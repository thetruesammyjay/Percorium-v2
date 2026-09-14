"""Persist discovery tabs on trade and order intents.

Revision ID: 0002_intent_tabs
Revises: 0001_initial
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_intent_tabs"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "trade_intents",
        sa.Column("tab", sa.String(length=16), nullable=False, server_default="stocks"),
    )
    op.add_column(
        "order_intents",
        sa.Column("tab", sa.String(length=16), nullable=False, server_default="stocks"),
    )
    op.alter_column("trade_intents", "tab", server_default=None)
    op.alter_column("order_intents", "tab", server_default=None)


def downgrade() -> None:
    op.drop_column("order_intents", "tab")
    op.drop_column("trade_intents", "tab")