"""Startup configuration validation for local and deployable beta modes."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


class ConfigError(RuntimeError):
    pass


EMAIL_PROVIDERS = frozenset({"console", "fake"})
DEV_ONLY_EMAIL_PROVIDERS = frozenset({"console", "fake"})
LOCAL_OTP_PEPPER = "local-only-otp-pepper-do-not-use-in-beta"


@dataclass(frozen=True)
class AppConfig:
    database_url: str
    upload_dir: str
    auth_mode: str  # password
    environment: str  # local | beta | production
    max_upload_mb: int
    timezone: str
    email_provider: str  # console | fake (smtp/resend later)
    otp_pepper: str

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")


def load_config(*, strict: Optional[bool] = None) -> AppConfig:
    environment = os.getenv("LIFE_INBOX_ENV", "local").strip() or "local"
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/life_inbox.db",
    ).strip()
    upload_dir = os.getenv("LIFE_INBOX_UPLOAD_DIR", "./data/uploads").strip()
    auth_mode = os.getenv("LIFE_INBOX_AUTH_MODE", "password").strip() or "password"
    timezone = os.getenv("LIFE_INBOX_TIMEZONE", "UTC").strip() or "UTC"
    max_upload_mb = int(os.getenv("LIFE_INBOX_MAX_UPLOAD_MB", "5") or "5")
    email_provider = (
        os.getenv("LIFE_INBOX_EMAIL_PROVIDER", "console").strip().lower()
        or "console"
    )
    otp_pepper = os.getenv("LIFE_INBOX_OTP_PEPPER", "").strip()

    if strict is None:
        strict = environment in {"beta", "production"}

    errors: list[str] = []
    if not database_url:
        errors.append("DATABASE_URL is required.")
    if environment in {"beta", "production"} and database_url.startswith("sqlite"):
        errors.append(
            "PostgreSQL DATABASE_URL is required for beta/production "
            "(SQLite is local/dev only)."
        )
    if not upload_dir:
        errors.append("LIFE_INBOX_UPLOAD_DIR is required.")
    if auth_mode != "password":
        errors.append("LIFE_INBOX_AUTH_MODE must be 'password'.")
    if max_upload_mb < 1 or max_upload_mb > 50:
        errors.append("LIFE_INBOX_MAX_UPLOAD_MB must be between 1 and 50.")
    if email_provider not in EMAIL_PROVIDERS:
        errors.append(
            "LIFE_INBOX_EMAIL_PROVIDER must be one of: "
            + ", ".join(sorted(EMAIL_PROVIDERS))
        )
    if environment in {"beta", "production"}:
        if email_provider in DEV_ONLY_EMAIL_PROVIDERS:
            errors.append(
                "LIFE_INBOX_EMAIL_PROVIDER must send real email in "
                "beta/production (console/fake are local only)."
            )
        if len(otp_pepper) < 32:
            errors.append(
                "LIFE_INBOX_OTP_PEPPER must be at least 32 random characters "
                "in beta/production."
            )

    if errors and strict:
        raise ConfigError("; ".join(errors))

    if not otp_pepper:
        # Local-only fallback; strict environments must set a real secret.
        otp_pepper = LOCAL_OTP_PEPPER

    return AppConfig(
        database_url=database_url,
        upload_dir=upload_dir,
        auth_mode=auth_mode,
        environment=environment,
        max_upload_mb=max_upload_mb,
        timezone=timezone,
        email_provider=email_provider,
        otp_pepper=otp_pepper,
    )


def config_warnings(config: AppConfig) -> list[str]:
    warnings: list[str] = []
    if config.is_sqlite and config.environment != "local":
        warnings.append("SQLite in use outside local environment.")
    if config.email_provider == "console":
        warnings.append("Email is printed to the server terminal (console mode).")
    if config.otp_pepper == LOCAL_OTP_PEPPER:
        warnings.append("Using the local-only OTP pepper.")
    return warnings
