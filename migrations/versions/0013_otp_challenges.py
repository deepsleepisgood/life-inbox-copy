"""One-time codes (OTP) for forgot-password.

Stores only a keyed hash of each code, plus attempt counts and expiry, so a
code is single-use, short-lived and can't be brute-forced.

Revision ID: 0013_otp_challenges
Revises: 0012_password_auth
"""

from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0013_otp_challenges"
down_revision: Optional[str] = "0012_password_auth"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "otp_challenges" in set(inspector.get_table_names()):
        return
    op.create_table(
        "otp_challenges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("purpose", sa.Text(), nullable=False),
        # HMAC of the normalized email: rate limits work even for unknown
        # emails without storing the address itself.
        sa.Column("identifier_hash", sa.Text(), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("code_hash", sa.Text(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "max_attempts", sa.Integer(), nullable=False, server_default="5"
        ),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.Text(), nullable=False),
        sa.Column("consumed_at", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_otp_identifier_purpose_created",
        "otp_challenges",
        ["identifier_hash", "purpose", "created_at"],
    )


def downgrade() -> None:
    raise RuntimeError(
        "Downgrade is disabled to preserve security history. "
        "Restore from backup instead."
    )
