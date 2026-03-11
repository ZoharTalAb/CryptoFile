"""add user security tables and fields

Revision ID: 8f3c2b1a9d10
Revises: dac704679662
Create Date: 2026-03-11 09:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f3c2b1a9d10"
down_revision: Union[str, Sequence[str], None] = "dac704679662"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------
    # users table - new security fields
    # -----------------------------
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column(
        "users", sa.Column("password_changed_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "users", sa.Column("password_expires_at", sa.DateTime(), nullable=True)
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
        "users", sa.Column("last_failed_login_at", sa.DateTime(), nullable=True)
    )
    op.add_column("users", sa.Column("locked_until", sa.DateTime(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    # Fill existing rows safely
    op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")
    op.execute(
        "UPDATE users SET password_changed_at = created_at WHERE password_changed_at IS NULL"
    )
    op.execute(
        "UPDATE users SET password_expires_at = created_at WHERE password_expires_at IS NULL"
    )

    op.alter_column("users", "updated_at", nullable=False)
    op.alter_column("users", "password_changed_at", nullable=False)
    op.alter_column("users", "password_expires_at", nullable=False)

    op.alter_column("users", "failed_login_attempts", server_default=None)
    op.alter_column("users", "token_version", server_default=None)

    # -----------------------------
    # password_history
    # -----------------------------
    op.create_table(
        "password_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_password_history_id"), "password_history", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_password_history_user_id"),
        "password_history",
        ["user_id"],
        unique=False,
    )

    # -----------------------------
    # password_reset_tokens
    # -----------------------------
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_password_reset_tokens_id"),
        "password_reset_tokens",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_tokens_user_id"),
        "password_reset_tokens",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_tokens_token_hash"),
        "password_reset_tokens",
        ["token_hash"],
        unique=False,
    )

    # -----------------------------
    # auth_audit_logs
    # -----------------------------
    op.create_table(
        "auth_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("reason_code", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_auth_audit_logs_id"),
        "auth_audit_logs",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_audit_logs_user_id"),
        "auth_audit_logs",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_audit_logs_email"),
        "auth_audit_logs",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_audit_logs_event_type"),
        "auth_audit_logs",
        ["event_type"],
        unique=False,
    )


def downgrade() -> None:
    # -----------------------------
    # auth_audit_logs
    # -----------------------------
    op.drop_index(op.f("ix_auth_audit_logs_event_type"), table_name="auth_audit_logs")
    op.drop_index(op.f("ix_auth_audit_logs_email"), table_name="auth_audit_logs")
    op.drop_index(op.f("ix_auth_audit_logs_user_id"), table_name="auth_audit_logs")
    op.drop_index(op.f("ix_auth_audit_logs_id"), table_name="auth_audit_logs")
    op.drop_table("auth_audit_logs")

    # -----------------------------
    # password_reset_tokens
    # -----------------------------
    op.drop_index(
        op.f("ix_password_reset_tokens_token_hash"),
        table_name="password_reset_tokens",
    )
    op.drop_index(
        op.f("ix_password_reset_tokens_user_id"),
        table_name="password_reset_tokens",
    )
    op.drop_index(
        op.f("ix_password_reset_tokens_id"),
        table_name="password_reset_tokens",
    )
    op.drop_table("password_reset_tokens")

    # -----------------------------
    # password_history
    # -----------------------------
    op.drop_index(op.f("ix_password_history_user_id"), table_name="password_history")
    op.drop_index(op.f("ix_password_history_id"), table_name="password_history")
    op.drop_table("password_history")

    # -----------------------------
    # users table - remove security fields
    # -----------------------------
    op.drop_column("users", "token_version")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "last_failed_login_at")
    op.drop_column("users", "failed_login_attempts")
    op.drop_column("users", "password_expires_at")
    op.drop_column("users", "password_changed_at")
    op.drop_column("users", "updated_at")
