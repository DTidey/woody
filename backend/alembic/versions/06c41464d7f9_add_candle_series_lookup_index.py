"""add candle series lookup index

Revision ID: 06c41464d7f9
Revises: 9432bd90373a
Create Date: 2026-03-18 15:20:00.000000
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "06c41464d7f9"
down_revision = "9432bd90373a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS candle_series_lookup_idx
        ON public.candle (exchange, symbol, timeframe, timestamp DESC)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.candle_series_lookup_idx")
