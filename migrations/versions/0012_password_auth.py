"""Password login and server-side sessions.

Adds password and account-lifecycle columns to ``users`` and a new
``auth_sessions`` table so logout revokes a session immediately.

Revision ID: 0012_password_auth
Revises: 0011_multi_user_ownership
"""

from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0012_password_auth"
down_revision: Optional[str] = "0011_multi_user_ownership"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


USER_COLUMNS = (
    ("password_hash", sa.Column("password_hash", sa.Text(), nullable=True)),
    (
        "password_changed_at",
        sa.Column("password_changed_at", sa.Text(), nullable=True),
    ),
    (
        "status",
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
    ),
    (
        "failed_password_attempts",
        sa.Column(
            "failed_password_attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    ),
    ("locked_until", sa.Column("locked_until", sa.Text(), nullable=True)),
    ("last_login_at", sa.Column("last_login_at", sa.Text(), nullable=True)),
    (
        "email_verified_at",
        sa.Column("email_verified_at", sa.Text(), nullable=True),
    ),
    (
        "adult_confirmed_at",
        sa.Column("adult_confirmed_at", sa.Text(), nullable=True),
    ),
    (
        "terms_accepted_at",
        sa.Column("terms_accepted_at", sa.Text(), nullable=True),
    ),
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {column["name"] for column in inspector.get_columns("users")}

    with op.batch_alter_table("users") as batch:
        for name, column in USER_COLUMNS:
            if name not in existing:
                batch.add_column(column)

    if "auth_sessions" not in set(inspector.get_table_names()):
        op.create_table(
            "auth_sessions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("token_hash", sa.Text(), nullable=False),
            sa.Column("auth_method", sa.Text(), nullable=False),
            sa.Column("created_at", sa.Text(), nullable=False),
            sa.Column("last_seen_at", sa.Text(), nullable=False),
            sa.Column("idle_expires_at", sa.Text(), nullable=False),
            sa.Column("absolute_expires_at", sa.Text(), nullable=False),
            sa.Column("revoked_at", sa.Text(), nullable=True),
            sa.Column("revoked_reason", sa.Text(), nullable=True),
            sa.Column("device_label", sa.Text(), nullable=True),
            sa.UniqueConstraint(
                "token_hash", name="uq_auth_sessions_token_hash"
            ),
        )
        op.create_index(
            "ix_auth_sessions_user_id", "auth_sessions", ["user_id"]
        )


    _scope_topic_names_per_owner(bind)


def _scope_topic_names_per_owner(bind) -> None:
    """Topic names were unique across all users (0007); make them per owner.

    Without this, a second user's default topics ("Work", ...) collide with
    the first user's and registration fails.
    """
    inspector = sa.inspect(bind)
    uniques = inspector.get_unique_constraints("topics")
    name_only = [u for u in uniques if u["column_names"] == ["name"]]
    has_owner_unique = any(
        set(u["column_names"]) == {"name", "owner_user_id"} for u in uniques
    )
    if not name_only and has_owner_unique:
        return

    if bind.dialect.name == "sqlite":
        # SQLite needs a table rebuild; the naming convention gives the
        # unnamed UNIQUE(name) from 0007 a name we can drop.
        with op.batch_alter_table(
            "topics",
            recreate="always",
            table_kwargs={"sqlite_autoincrement": True},
            naming_convention={"uq": "uq_%(table_name)s_%(column_0_name)s"},
        ) as batch:
            if name_only:
                batch.drop_constraint("uq_topics_name", type_="unique")
            if not has_owner_unique:
                batch.create_unique_constraint(
                    "uq_topics_name_owner", ["name", "owner_user_id"]
                )
        return

    for constraint in name_only:
        op.drop_constraint(constraint["name"], "topics", type_="unique")
    if not has_owner_unique:
        op.create_unique_constraint(
            "uq_topics_name_owner", "topics", ["name", "owner_user_id"]
        )


def downgrade() -> None:
    raise RuntimeError(
        "Downgrade is disabled: it would destroy password hashes and "
        "sessions. Restore from backup instead."
    )
