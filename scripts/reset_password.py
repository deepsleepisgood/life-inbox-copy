"""Set a new password for an account (operator tool, until email reset exists).

Use it when someone forgot their password, or for accounts created with the
old dev login, which never had one. You type the new password privately; it
is never printed or logged. All of the account's sessions are signed out.

    python -m scripts.reset_password --email you@example.com

Uses DATABASE_URL like the app. If typing seems frozen in Git Bash, run it
from PowerShell or Command Prompt instead.
"""

from __future__ import annotations

import argparse
import getpass
import sys
from datetime import datetime, timezone

from app.auth import end_all_sessions, hash_password, normalize_email, password_problem
from app.database import (
    DEFAULT_OWNER_EMAIL,
    get_user_credentials_by_email,
    set_user_password_hash,
)


class ResetError(Exception):
    pass


def reset_password(email: str, new_password: str) -> dict:
    cleaned = normalize_email(email)
    if cleaned == DEFAULT_OWNER_EMAIL:
        raise ResetError("The built-in Local Owner cannot sign in.")
    user = get_user_credentials_by_email(cleaned)
    if user is None:
        raise ResetError(f"No account for {cleaned}.")
    problem = password_problem(new_password, email=cleaned)
    if problem:
        raise ResetError(problem)
    set_user_password_hash(
        user["id"],
        hash_password(new_password),
        datetime.now(timezone.utc).isoformat(),
    )
    revoked = end_all_sessions(user["id"])
    return {"email": cleaned, "user_id": user["id"], "sessions_signed_out": revoked}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--email", required=True)
    args = parser.parse_args(argv)

    new_password = getpass.getpass("New password (10+ characters, hidden): ")
    confirm = getpass.getpass("Type it again: ")
    if new_password != confirm:
        print("Passwords do not match. Nothing changed.", file=sys.stderr)
        return 1
    try:
        result = reset_password(args.email, new_password)
    except ResetError as exc:
        print(f"{exc} Nothing changed.", file=sys.stderr)
        return 1
    except Exception as exc:  # e.g. invalid email from normalize_email
        print(f"{getattr(exc, 'detail', exc)} Nothing changed.", file=sys.stderr)
        return 1
    print(
        f"Password set for {result['email']}. "
        f"Signed out {result['sessions_signed_out']} session(s). "
        "You can sign in now."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
