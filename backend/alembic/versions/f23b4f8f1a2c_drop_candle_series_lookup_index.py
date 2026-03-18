"""drop candle series lookup index

Revision ID: f23b4f8f1a2c
Revises: 06c41464d7f9
Create Date: 2026-03-18 16:40:00.000000
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "f23b4f8f1a2c"
down_revision = "06c41464d7f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.candle_series_lookup_idx")


def downgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS candle_series_lookup_idx
        ON public.candle (exchange, symbol, timeframe, timestamp DESC)
        """
    )
