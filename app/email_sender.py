"""Outgoing email, behind one function so the delivery method is swappable.

Providers (``LIFE_INBOX_EMAIL_PROVIDER``):
- ``console``: prints the email in the server terminal. Local development only.
- ``fake``: keeps emails in ``FAKE_OUTBOX`` for automated tests.

Real delivery (Gmail SMTP, then Resend once there's a domain) plugs in here
without changing callers.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import load_config


@dataclass(frozen=True)
class OutgoingEmail:
    to: str
    subject: str
    body: str


FAKE_OUTBOX: list[OutgoingEmail] = []


def _send_console(message: OutgoingEmail) -> None:
    border = "=" * 64
    print(
        f"\n{border}\n"
        "[Life Inbox email, console mode: not actually sent]\n"
        f"To:      {message.to}\n"
        f"Subject: {message.subject}\n\n"
        f"{message.body}\n"
        f"{border}\n",
        flush=True,
    )


def _send_fake(message: OutgoingEmail) -> None:
    FAKE_OUTBOX.append(message)


_PROVIDERS = {
    "console": _send_console,
    "fake": _send_fake,
}


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email; returns the provider name used."""
    provider = load_config(strict=False).email_provider
    sender = _PROVIDERS.get(provider)
    if sender is None:
        raise RuntimeError(f"Email provider {provider!r} is not available.")
    sender(OutgoingEmail(to=to, subject=subject, body=body))
    return provider


def current_provider() -> str:
    return load_config(strict=False).email_provider
