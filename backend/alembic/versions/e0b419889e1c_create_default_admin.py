"""create default admin

Revision ID: e0b419889e1c
Revises: 4df360ddb23b
Create Date: 2025-07-04 20:16:12.289654
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import enum

from core.config import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
from core.security import hash_password


# revision identifiers, used by Alembic.
revision: str = "e0b419889e1c"
down_revision: Union[str, Sequence[str], None] = "4df360ddb23b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define enum used in DB
class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    MAINTAINER = "MAINTAINER"
    REPORTER = "REPORTER"


def upgrade() -> None:
    if not DEFAULT_ADMIN_EMAIL or not DEFAULT_ADMIN_PASSWORD:
        raise RuntimeError(
            "DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD must be set in core.config"
        )

    hashed_password = hash_password(DEFAULT_ADMIN_PASSWORD)

    users_table = sa.table(
        "users",
        sa.column("email", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("role", sa.Enum(UserRole, name="userrole")),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "email": DEFAULT_ADMIN_EMAIL,
                "password_hash": hashed_password,
                "role": UserRole.ADMIN.value,
            }
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM users WHERE email = :email").bindparams(
            email=DEFAULT_ADMIN_EMAIL
        )
    )
