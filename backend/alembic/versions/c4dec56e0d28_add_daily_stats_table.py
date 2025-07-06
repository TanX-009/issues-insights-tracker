"""add daily_stats table

Revision ID: c4dec56e0d28
Revises: 1803a56e49c8
Create Date: 2025-07-06 09:00:43.191632
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4dec56e0d28"
down_revision: Union[str, Sequence[str], None] = "1803a56e49c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "daily_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.UniqueConstraint("status", "date", name="uix_status_date"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("daily_stats")
