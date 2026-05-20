"""add email verification fields

Revision ID: b19a4d2c7e11
Revises: 8f3c2b1a9d10
Create Date: 2026-05-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b19a4d2c7e11"
down_revision: Union[str, Sequence[str], None] = "8f3c2b1a9d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_code_hash", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_expires_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_sent_at", sa.DateTime(), nullable=True),
    )

    op.alter_column("users", "email_verified", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "email_verification_sent_at")
    op.drop_column("users", "email_verification_expires_at")
    op.drop_column("users", "email_verification_code_hash")
    op.drop_column("users", "email_verified")
