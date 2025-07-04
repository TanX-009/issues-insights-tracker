"""create initial tables

Revision ID: 4df360ddb23b
Revises:
Create Date: 2025-07-04 11:54:29.656612

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import models.user as user_model
import models.issue as issue_model


# revision identifiers, used by Alembic.
revision: str = "4df360ddb23b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.Enum(user_model.UserRole), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "issues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("severity", sa.Enum(issue_model.Severity), nullable=False),
        sa.Column("status", sa.Enum(issue_model.Status), nullable=False),
        sa.Column("reporter_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"]),
    )


def downgrade():
    op.drop_table("issues")
    op.drop_table("users")
