"""add conversation archive fields

Revision ID: 6885b52d7316
Revises: baea32080349
Create Date: 2026-07-18 14:19:23.809027
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6885b52d7316"
down_revision: Union[str, Sequence[str], None] = "baea32080349"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add archived_at to conversations."""

    op.add_column(
        "conversations",
        sa.Column(
            "archived_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove archived_at from conversations."""

    op.drop_column(
        "conversations",
        "archived_at",
    )