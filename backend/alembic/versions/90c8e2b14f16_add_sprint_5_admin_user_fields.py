"""add sprint 5 admin user fields

Revision ID: 90c8e2b14f16
Revises: 6885b52d7316
Create Date: 2026-07-23 10:43:24.544322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90c8e2b14f16'
down_revision: Union[str, Sequence[str], None] = '6885b52d7316'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "is_locked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "failed_login_attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "last_login_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "password_changed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_is_active",
        "users",
        ["is_active"],
    )

    op.create_index(
        "ix_users_is_locked",
        "users",
        ["is_locked"],
    )

    op.create_index(
        "ix_users_is_deleted",
        "users",
        ["is_deleted"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_users_is_deleted",
        table_name="users",
    )

    op.drop_index(
        "ix_users_is_locked",
        table_name="users",
    )

    op.drop_index(
        "ix_users_is_active",
        table_name="users",
    )

    op.drop_column(
        "users",
        "deleted_at",
    )

    op.drop_column(
        "users",
        "password_changed_at",
    )

    op.drop_column(
        "users",
        "last_login_at",
    )

    op.drop_column(
        "users",
        "failed_login_attempts",
    )

    op.drop_column(
        "users",
        "is_deleted",
    )

    op.drop_column(
        "users",
        "is_locked",
    )

    op.drop_column(
        "users",
        "is_active",
    )