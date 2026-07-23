"""create audit logs table

Revision ID: 863ff98c15f3
Revises: 90c8e2b14f16
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "863ff98c15f3"
down_revision: str | None = "90c8e2b14f16"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_audit_logs_id"),
        "audit_logs",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_user_id"),
        "audit_logs",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_action"),
        "audit_logs",
        ["action"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_resource"),
        "audit_logs",
        ["resource"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_created_at"),
        "audit_logs",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_audit_logs_created_at"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_resource"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_action"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_user_id"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_id"),
        table_name="audit_logs",
    )

    op.drop_table("audit_logs")