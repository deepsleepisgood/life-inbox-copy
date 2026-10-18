"""Move data owned by the legacy "Local Owner" into a registered account.

Before password login, anonymous local use stored everything under the
built-in user ``local@life-inbox.local``. That user has no password, so after
upgrading nobody can sign in to see that data. Register your real account in
the app first, then run:

    python -m scripts.claim_local_owner --to-email you@example.com --dry-run
    python -m scripts.claim_local_owner --to-email you@example.com

Uses DATABASE_URL like the app. Runs in one transaction; running it again
does nothing.
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import text

from app.database import DEFAULT_OWNER_EMAIL, engine


OWNED_TABLES = ("inbox_items", "tasks", "analysis_runs")


def claim(to_email: str, *, dry_run: bool) -> dict:
    target_email = to_email.strip().lower()
    summary: dict = {"topics_merged": 0, "topics_moved": 0}
    with engine.connect() as connection, connection.begin() as transaction:
        source_id = connection.scalar(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": DEFAULT_OWNER_EMAIL},
        )
        if source_id is None:
            summary["status"] = "nothing_to_claim"
            return summary
        target = connection.execute(
            text("SELECT id, password_hash FROM users WHERE email = :email"),
            {"email": target_email},
        ).one_or_none()
        if target is None or not target.password_hash:
            raise SystemExit(
                f"No registered account for {target_email}. "
                "Create it on the sign-in page first."
            )
        target_id = target.id

        for table in OWNED_TABLES:
            summary[table] = connection.execute(
                text(
                    f"UPDATE {table} SET owner_user_id = :target "
                    "WHERE owner_user_id = :source"
                ),
                {"target": target_id, "source": source_id},
            ).rowcount

        target_topics = {
            row.name: row.id
            for row in connection.execute(
                text("SELECT id, name FROM topics WHERE owner_user_id = :o"),
                {"o": target_id},
            )
        }
        for row in connection.execute(
            text("SELECT id, name FROM topics WHERE owner_user_id = :o"),
            {"o": source_id},
        ).all():
            existing = target_topics.get(row.name)
            if existing is None:
                connection.execute(
                    text("UPDATE topics SET owner_user_id = :t WHERE id = :id"),
                    {"t": target_id, "id": row.id},
                )
                summary["topics_moved"] += 1
                continue
            for column in ("topic_id", "user_topic_id"):
                connection.execute(
                    text(
                        f"UPDATE item_insights SET {column} = :new "
                        f"WHERE {column} = :old"
                    ),
                    {"new": existing, "old": row.id},
                )
            connection.execute(
                text("DELETE FROM topics WHERE id = :id"), {"id": row.id}
            )
            summary["topics_merged"] += 1

        connection.execute(
            text("DELETE FROM users WHERE id = :id"), {"id": source_id}
        )
        summary["status"] = "dry_run" if dry_run else "claimed"
        if dry_run:
            transaction.rollback()
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--to-email", required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would move without changing anything.",
    )
    args = parser.parse_args(argv)
    summary = claim(args.to_email, dry_run=args.dry_run)
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
