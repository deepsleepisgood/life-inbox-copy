# Production Auth Plan — Life Inbox Milestone 7

Status: **Partly implemented** (see "Implementation status" below)
Branch (planned): `milestone/7-production-auth`
Tag (planned): `milestone-7`
Last updated: 2026-10-15

This document says exactly what will change in Life Inbox to replace the current
dev login with production-ready login: email OTP, phone OTP, password, forgot
password and account recovery. It also covers strict per-user data isolation and
GDPR / India DPDP Act 2023 compliance, so the app can later ship on the Apple App
Store and Google Play.

> Legal note: this document defines the technical controls. The privacy policy,
> terms, and any Data Protection Impact Assessment (DPIA) must be reviewed by a
> qualified lawyer before public launch.

## Implementation status (2026-10-16)

**Done: password sign-up, password login, logout, change password.**

- Migration `0012_password_auth`: password and account-lifecycle columns on
  `users`, the `auth_sessions` table, and topic names made unique per owner
  instead of across all users. The old app-wide constraint made a second
  user's registration fail on Alembic-built databases.
- `app/auth.py`: argon2id hashing, password policy, 5-failure / 15-minute
  lockout, and server-side sessions (30-day idle, 90-day absolute,
  rotated on every sign-in).
- `app/main.py`: an auth gate in front of every route except `PUBLIC_PATHS`.
  It also blocks cross-site writes and sets security headers. Dev login and
  the Google stub are removed.
- `/login` page (create account / sign in), draft `/privacy` and `/terms`,
  and an app header with Sign out, Sign out everywhere and Change password.
- `scripts/claim_local_owner.py` moves pre-M7 "Local Owner" data into a
  registered account.

**Done (2026-10-18): forgot password with email codes.** Migration
`0013_otp_challenges`; `request_password_reset` / `reset_password_with_code`
in `app/auth.py`; `app/email_sender.py` with `console` (prints to the server
terminal) and `fake` (tests) providers; `POST /api/auth/password/forgot` and
`/api/auth/password/reset`; two-step form on `/login`. Rate limits come from
counting `otp_challenges` rows, so no separate `rate_limits` table.
`scripts/reset_password.py` is the operator fallback.

**Migration numbering changed** from §3: the remaining work becomes
`0014_production_auth` (SMS, recovery codes, consent, audit) and
`0015_owner_required`.

**Not done yet:** real email delivery (SMTP/Resend), SMS codes, email
verification at sign-up, sign-in with a code, recovery codes, consent
records table, account export and deletion, AI-processing toggle,
per-user upload folders, and `owner_user_id NOT NULL`.

---

## 0. Decisions

| # | Topic | Decision |
|---|---|---|
| D1 | Email login | One-time code sent to the user's email address (Gmail or any other provider). No "Sign in with Google" button, so the Sign in with Apple requirement (App Store guideline 4.8) does not apply. |
| D2 | Email provider | **Resend**. No account exists yet; see §11.1. |
| D3 | SMS provider | **Twilio Verify**. See §11.2. |
| D4 | Privacy regimes | **GDPR** (EU/EEA/UK) and **DPDP Act 2023** (India). |
| D5 | Minimum age | **18+**. This avoids the DPDP Act's verifiable-parental-consent rules for minors. |
| D6 | Password | **Required at registration**. Users can log in with password **or** OTP. Forgot password works through OTP to any verified channel. |
| D7 | Account recovery | Any verified channel (email or phone) can recover the account. Users can also generate one-time **recovery codes** as a backup. |
| D8 | Sessions | Server-side and stored in the database (opaque token), so logout revokes them immediately. |
| D9 | Stack | Same stack as today: FastAPI + SQLAlchemy + Alembic + vanilla JS. No React, no Redis. |

---

## 1. Today vs. target

| Area | Today (Milestone 6) | Target (Milestone 7) |
|---|---|---|
| Identity proof | None. Typing an email logs you in. | OTP to email or phone, plus password |
| Session | HMAC-signed JSON cookie with no server record | Random token; its hash is stored in `auth_sessions` and can be revoked |
| Logout | Deletes the cookie only. A copied token stays valid for 14 days. | Revokes the session row; the token becomes invalid immediately |
| Logged-out access | `require_owner_id()` falls back to "Local Owner" in every environment | 401 on every `/api/*` route; `/` redirects to `/login` |
| UI before login | Full app is visible | Only the login/register page is visible |
| Data isolation | `owner_user_id` is nullable; uploads share one folder | `owner_user_id NOT NULL` with indexes; uploads stored as `uploads/<user_id>/…` |
| Privacy rights | None | Export my data, delete my account, consent records, AI-processing toggle |

---

## 2. User flows

### 2.1 Register (new user)

```
/login
  └─ "Create account"
      1. Enter email OR phone (+country code)
      2. POST /api/auth/otp/request  {identifier, purpose:"register"}
      3. Enter the 6-digit code
      4. Enter: display name, password (+confirm),
         [ ] I am 18 or older                  (required)
         [ ] I agree to the Terms              (required, links /terms)
         [ ] I have read the Privacy Policy    (required, links /privacy)
         [ ] Allow AI processing of my content (optional, default OFF)
      5. POST /api/auth/register  → session cookie set → redirect to /
      6. (Optional prompt) Add your other contact (phone or email) for recovery
      7. (Optional prompt) Generate recovery codes
```

### 2.2 Login

```
/login
  ├─ Tab "Password":  identifier + password → POST /api/auth/login/password
  │                   [Forgot password?] → flow 2.3
  └─ Tab "One-time code": identifier → POST /api/auth/otp/request {purpose:"login"}
                          code → POST /api/auth/login/otp
```

On success the server sets the session cookie and the browser goes to `/`.

### 2.3 Forgot password

```
/login → "Forgot password?"
  1. Enter email or phone
  2. POST /api/auth/otp/request {purpose:"reset_password"}
  3. Enter code + new password (+confirm)
  4. POST /api/auth/password/reset
     → password updated, ALL existing sessions revoked,
       security notice sent to every verified channel,
       new session created → redirect to /
```

### 2.4 Account recovery (lost access to one channel)

| Situation | Recovery path |
|---|---|
| Lost the phone, still has email | Log in with email OTP or password, then replace the phone number in Settings (needs a new OTP on the new number) |
| Lost the email, still has phone | Same as above, using phone OTP |
| Lost both channels, but has the password | Log in with the password, then add new channels in Settings. Each new channel must be verified with OTP. |
| Lost both channels **and** the password | Use a recovery code at `/login → "Use a recovery code"`. This forces a password reset and the user must add a new channel. |
| Lost everything | Manual support process: the account can't be recovered automatically. The documented support policy is to verify through an old-channel notice and a 7-day waiting period, or else create a new account. |

### 2.5 Logout

The **Sign out** button calls `POST /api/auth/logout`. The session row is marked
revoked, the cookie is cleared, all app data is wiped from the screen, and the
browser goes to `/login`. **Sign out of all devices** revokes every session
belonging to the user.

### 2.6 Delete account

Settings → Delete account → enter an OTP or the password → `DELETE /api/account`.
The account is deactivated immediately and all sessions are revoked. Data is
permanently erased within 30 days (§8.3).

---

## 3. Database changes (Alembic)

There are two new migrations. As AGENTS.md requires, Alembic is the only way the
schema changes. Both migrations work on SQLite (local and tests) and PostgreSQL
(beta and production) by using `batch_alter_table`.

### 3.1 Migration `0012_production_auth`

File: `migrations/versions/0012_production_auth.py`

```python
"""Production auth: verified contacts, passwords, sessions, OTP, audit, consent.

Revision ID: 0012_production_auth
Revises: 0011_multi_user_ownership
"""

from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0012_production_auth"
down_revision: Optional[str] = "0011_multi_user_ownership"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    # --- users: new identity + lifecycle columns -------------------------
    with op.batch_alter_table("users") as batch:
        batch.alter_column("email", existing_type=sa.Text(), nullable=True)
        batch.add_column(sa.Column("phone_e164", sa.Text(), nullable=True))
        batch.add_column(sa.Column("email_verified_at", sa.Text(), nullable=True))
        batch.add_column(sa.Column("phone_verified_at", sa.Text(), nullable=True))
        batch.add_column(sa.Column("password_hash", sa.Text(), nullable=True))
        batch.add_column(sa.Column("password_changed_at", sa.Text(), nullable=True))
        batch.add_column(
            sa.Column("status", sa.Text(), nullable=False, server_default="active")
        )
        batch.add_column(sa.Column("failed_password_attempts", sa.Integer(),
                                   nullable=False, server_default="0"))
        batch.add_column(sa.Column("locked_until", sa.Text(), nullable=True))
        batch.add_column(sa.Column("last_login_at", sa.Text(), nullable=True))
        batch.add_column(sa.Column("deletion_requested_at", sa.Text(), nullable=True))
        batch.add_column(sa.Column("ai_processing_enabled", sa.Boolean(),
                                   nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("adult_confirmed_at", sa.Text(), nullable=True))
        batch.create_unique_constraint("uq_users_phone_e164", ["phone_e164"])
        batch.create_check_constraint(
            "ck_users_status", "status IN ('active','locked','pending_deletion')"
        )
        batch.create_check_constraint(
            "ck_users_has_contact",
            "email IS NOT NULL OR phone_e164 IS NOT NULL "
            "OR status = 'pending_deletion'",
        )

    # --- server-side sessions -------------------------------------------
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),      # sha256(token)
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("last_seen_at", sa.Text(), nullable=False),
        sa.Column("idle_expires_at", sa.Text(), nullable=False),
        sa.Column("absolute_expires_at", sa.Text(), nullable=False),
        sa.Column("revoked_at", sa.Text(), nullable=True),
        sa.Column("revoked_reason", sa.Text(), nullable=True),
        sa.Column("auth_method", sa.Text(), nullable=False),     # otp_email|otp_sms|password|recovery_code
        sa.Column("device_label", sa.Text(), nullable=True),     # parsed UA, e.g. "Chrome on Windows"
        sa.Column("ip_hash", sa.Text(), nullable=True),
        sa.UniqueConstraint("token_hash", name="uq_auth_sessions_token_hash"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])

    # --- OTP challenges --------------------------------------------------
    op.create_table(
        "otp_challenges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("channel", sa.Text(), nullable=False),          # email|sms
        sa.Column("purpose", sa.Text(), nullable=False),          # register|login|reset_password|verify_contact|reauth
        sa.Column("identifier_hash", sa.Text(), nullable=False),  # HMAC(pepper, normalized identifier)
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("code_hash", sa.Text(), nullable=True),         # NULL when Twilio Verify owns the code
        sa.Column("provider_ref", sa.Text(), nullable=True),      # Resend email id / Twilio Verify SID
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.Text(), nullable=False),
        sa.Column("consumed_at", sa.Text(), nullable=True),
        sa.Column("verified_token_hash", sa.Text(), nullable=True),  # short-lived proof used by /register & /password/reset
        sa.CheckConstraint("channel IN ('email','sms')", name="ck_otp_channel"),
    )
    op.create_index("ix_otp_identifier_purpose", "otp_challenges",
                    ["identifier_hash", "purpose", "created_at"])

    # --- recovery codes --------------------------------------------------
    op.create_table(
        "recovery_codes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code_hash", sa.Text(), nullable=False),        # argon2id
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("used_at", sa.Text(), nullable=True),
    )
    op.create_index("ix_recovery_codes_user_id", "recovery_codes", ["user_id"])

    # --- rate limiting (DB-backed, fixed window) ------------------------
    op.create_table(
        "rate_limits",
        sa.Column("bucket_key", sa.Text(), primary_key=True),     # e.g. "otp:dest:<hash>:1h"
        sa.Column("window_start", sa.Text(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
    )

    # --- consent records (proof of consent, GDPR Art.7 / DPDP s.6) -------
    op.create_table(
        "consent_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subject_ref", sa.Text(), nullable=False),      # HMAC of user id; survives erasure
        sa.Column("consent_type", sa.Text(), nullable=False),     # terms|privacy|ai_processing|adult_confirmation
        sa.Column("document_version", sa.Text(), nullable=True),  # e.g. "privacy-2026-10-15"
        sa.Column("granted", sa.Boolean(), nullable=False),
        sa.Column("recorded_at", sa.Text(), nullable=False),
        sa.Column("ip_hash", sa.Text(), nullable=True),
    )
    op.create_index("ix_consent_subject", "consent_records", ["subject_ref"])

    # --- security audit log ---------------------------------------------
    op.create_table(
        "auth_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),            # never raw codes/passwords/PII
        sa.Column("ip_hash", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Text(), nullable=False),
    )
    op.create_index("ix_auth_events_user_created", "auth_events",
                    ["user_id", "created_at"])

    # Existing users: emails were never verified; mark dev users clearly.
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")


def downgrade() -> None:
    raise RuntimeError(
        "Downgrade is disabled: it would destroy sessions, consent records "
        "and audit history. Restore from backup instead."
    )
```

### 3.2 Migration `0013_owner_required`

File: `migrations/versions/0013_owner_required.py`

This migration makes data ownership mandatory and indexes it. It **refuses to
run** if any row still has no owner, so data is never silently given to the
wrong user.

```python
"""Make owner_user_id mandatory and indexed on all owned tables.

Revision ID: 0013_owner_required
Revises: 0012_production_auth
"""

from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0013_owner_required"
down_revision: Optional[str] = "0012_production_auth"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None

OWNED_TABLES = ("inbox_items", "topics", "tasks", "analysis_runs")


def upgrade() -> None:
    conn = op.get_bind()
    for table in OWNED_TABLES:
        orphans = conn.execute(
            sa.text(f"SELECT COUNT(*) FROM {table} WHERE owner_user_id IS NULL")
        ).scalar()
        if orphans:
            raise RuntimeError(
                f"{orphans} rows in {table} have no owner. "
                "Run scripts/claim_local_owner.py first."
            )
    for table in OWNED_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.alter_column("owner_user_id", existing_type=sa.Integer(),
                               nullable=False)
        op.create_index(f"ix_{table}_owner_user_id", table, ["owner_user_id"])


def downgrade() -> None:
    raise RuntimeError("Downgrade disabled to protect ownership integrity.")
```

### 3.3 Foreign keys and deletion cascade

Today, `inbox_items.owner_user_id` and the other owner columns use plain
`ForeignKey("users.id")` with no cascade. The account purge job (§8.3) therefore
deletes child rows **explicitly in code**, in this order:

```
item_relations → item_insights → calendar_action_receipts → tasks
  → analysis_runs → inbox_items (and stored files) → topics
  → recovery_codes → otp_challenges → auth_sessions → users
```

Doing this in code avoids a risky cascade-rewrite migration on tables that
already hold data. It is also easier to test and log.

### 3.4 Moving existing data to a real account

Existing data belongs to the user `local@life-inbox.local`. The new script
`scripts/claim_local_owner.py --email you@example.com` handles the handover:

1. Requires the target user to have registered already (email verified).
2. Inside one transaction, reassigns every row in `OWNED_TABLES` from the local
   owner to the target user.
3. Moves uploaded files from `uploads/<file>` to `uploads/<user_id>/<file>` and
   updates `inbox_items.storage_path`.
4. Deletes the `local@life-inbox.local` user.
5. Prints a summary. Running it twice is safe and does nothing the second time.

### 3.5 SQLAlchemy model changes (`app/database.py`)

- `UserRecord`: add the columns from §3.1.
- New models: `AuthSessionRecord`, `OtpChallengeRecord`, `RecoveryCodeRecord`,
  `RateLimitRecord`, `ConsentRecord`, `AuthEventRecord`.
- `owner_user_id` on `InboxItemRecord`, `TopicRecord`, `TaskRecord` and
  `AnalysisRunRecord` changes to `nullable=False, index=True`.
- `require_owner_id()` **raises `NotAuthenticated`** when no owner is set. The
  fallback to the default owner is removed. The only exception is when
  `LIFE_INBOX_ALLOW_ANONYMOUS_LOCAL=1` **and** `LIFE_INBOX_ENV=local`; config
  validation rejects that combination in any other environment.
- `init_db()`: the test-only auto-create path still seeds a local owner, but
  only when `LIFE_INBOX_ALLOW_ANONYMOUS_LOCAL=1`.

---

## 4. Backend modules

`app/auth.py` is replaced by a package. Existing imports
(`from app.auth import SESSION_COOKIE, …`) are re-exported from `__init__.py`
during the transition.

```
app/auth/
  __init__.py          # re-exports: require_user, get_current_user, SESSION_COOKIE
  identifiers.py       # normalize email (lowercase, strip) / phone (phonenumbers → E.164)
  passwords.py         # argon2id hash/verify, policy, breached-password check
  sessions.py          # create / validate / touch / revoke / revoke_all / rotate
  otp.py               # request + verify challenges, attempt counting
  recovery_codes.py    # generate 10 codes, hash, consume
  rate_limit.py        # hit(bucket_key, limit, window) → raises 429
  audit.py             # record_event(user_id, type, success, detail)
  consent.py           # record_consent(...), current document versions
  middleware.py        # AuthGateMiddleware, SecurityHeadersMiddleware, CsrfMiddleware
  routes.py            # APIRouter for /api/auth/* and /api/account/*
  providers/
    base.py            # class OtpSender(Protocol): send(dest, purpose) -> ref; check(dest, code, ref) -> bool
    resend_email.py    # Resend adapter (we generate the code, Resend delivers it)
    smtp_email.py      # SMTP adapter for private beta without a domain (e.g. Gmail App Password)
    twilio_verify.py   # Twilio Verify adapter (Twilio generates + checks the code)
    console.py         # local dev only: logs code to stdout; forbidden outside local
    fake.py            # tests: captures codes in memory
```

New pages in `app/main.py`: `GET /login`, `GET /privacy`, `GET /terms` and
`GET /delete-account`. The auth routes are mounted with
`app.include_router(auth_router)`.

### 4.1 Requirements additions (`requirements.txt`)

```
argon2-cffi      # password + recovery-code hashing (argon2id)
phonenumbers     # phone validation / E.164 normalization
resend           # Resend email SDK
twilio           # Twilio Verify SDK
```

### 4.2 Password rules (`passwords.py`)

- Hashing: **argon2id** via `argon2-cffi`, with the library's default
  parameters, which follow RFC 9106. Hashes are upgraded automatically on login
  if the parameters change later (`check_needs_rehash`).
- Policy, following NIST SP 800-63B: **at least 10 characters**, at most 128.
  No rules forcing particular character types. Rejected if it matches the
  email or phone, or appears in a bundled list of the top 10,000 breached
  passwords (`app/auth/data/common_passwords.txt`). The rules are checked on
  the server; the browser only shows a strength hint.
- Lockout: after **5 failed password attempts**, `locked_until` is set to
  now + 15 minutes, and each further lock doubles the time, up to 24 hours.
  OTP login still works during a password lockout, so a lockout can't be used
  to keep the real owner out.
- Every password change or reset **revokes all other sessions** and sends a
  "Your password was changed" notice to every verified channel.

### 4.3 OTP rules (`otp.py`)

| Rule | Value |
|---|---|
| Code | 6 digits from `secrets.randbelow` (email). Twilio generates SMS codes. |
| Storage | `code_hash = HMAC-SHA256(LIFE_INBOX_OTP_PEPPER, challenge_id + code)` |
| Lifetime | 10 minutes |
| Attempts | 5 per challenge, then the challenge is dead |
| Single use | `consumed_at` is set on success |
| Resend cooldown | 60 s per identifier |
| Per identifier | at most 5 codes per hour and 10 per day |
| Per IP | at most 20 OTP requests per hour |
| SMS countries | Allow-list set in `LIFE_INBOX_SMS_ALLOWED_COUNTRIES` (default `IN`, plus EU countries you choose). This blocks SMS-pumping fraud. |
| No enumeration | `/otp/request` always returns `202 {"status":"sent_if_eligible"}`. For `login` or `reset_password` on an unknown identifier, nothing is sent. For `register` on an identifier that's already registered, a "someone tried to register with your email" notice is sent instead of a code. |

After a correct code, the server returns a **verification token**: 32 random
bytes, single use, valid for 10 minutes, stored as `verified_token_hash`.
`/register` and `/password/reset` require this token, so they never accept the
raw code a second time.

### 4.4 Sessions (`sessions.py`)

| Property | Value |
|---|---|
| Token | `secrets.token_urlsafe(32)`, sent only in the cookie |
| Stored as | `sha256(token)` in `auth_sessions.token_hash` |
| Cookie | `__Host-life_inbox_session`; `HttpOnly; Secure; SameSite=Lax; Path=/`. Locally over plain http, it falls back to `life_inbox_session` without `Secure`. |
| Idle timeout | 30 days, extended at most once per hour so every request doesn't write to the database |
| Absolute timeout | 90 days |
| On login | A new token is always issued (prevents session fixation) |
| Revoked by | Logout, logout-all, password change or reset, account deletion, admin lock |

The current `create_session_token` / `parse_session_token` HMAC-cookie code is
**deleted**. Any old cookies become invalid, so every user signs in once more.

### 4.5 Middleware (`middleware.py`)

These are added in `app/main.py` and replace `bind_owner_from_session` at
`app/main.py:113`.

1. **`AuthGateMiddleware`**
   - Public routes: `/login`, `/privacy`, `/terms`, `/delete-account`,
     `/static/*`, `/api/health`, `/api/auth/otp/*`, `/api/auth/register`,
     `/api/auth/login/*`, `/api/auth/password/reset`,
     `/api/auth/recovery/login`.
   - Every other route needs a valid session. Without one, `/api/*` returns
     `401 {"detail":"Authentication required."}` and HTML routes redirect
     (`302`) to `/login`.
   - When the session is valid, it calls `set_current_owner_id(user.id)` and
     clears it in `finally`, as today.
   - Because this is one gate in front of all routes, any new route is
     protected automatically. A test checks this (§9).
2. **`CsrfMiddleware`**: for `POST`/`PUT`/`PATCH`/`DELETE` to `/api/*`, the
   `Origin` (or `Referer`) header must match `LIFE_INBOX_PUBLIC_ORIGIN` and the
   request must carry the header `X-Requested-With: life-inbox`. This works
   together with `SameSite=Lax` cookies.
3. **`SecurityHeadersMiddleware`**:
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (beta and production)
   - `Content-Security-Policy: default-src 'self'; img-src 'self' data: blob:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'`
   - `X-Content-Type-Options: nosniff`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Permissions-Policy: camera=(), geolocation=()`. The microphone stays
     allowed for `self` because voice capture needs it.
   - `Cache-Control: no-store` on `/api/*`

### 4.6 Uploaded files

- `app/storage_backend.py`: every path is built as `"<owner_id>/<uuid>.<ext>"`.
  `resolve_path` rejects anything that escapes the user's own folder.
- The file download route at `app/main.py:580` loads the item **filtered by
  owner** before reading the file, and returns 404 rather than 403 so it
  doesn't reveal that another user's item exists.

### 4.7 Config (`app/config.py`) — new variables

| Variable | Required in | Purpose |
|---|---|---|
| `LIFE_INBOX_PUBLIC_ORIGIN` | beta/prod | e.g. `https://app.lifeinbox.example`. Used for the CSRF check and email links. |
| `LIFE_INBOX_OTP_PEPPER` | beta/prod | 32+ random characters; secret key for OTP and identifier hashes |
| `LIFE_INBOX_EMAIL_PROVIDER` | all | `resend` \| `smtp` (private beta, e.g. Gmail App Password) \| `console` (local only) \| `fake` (tests) |
| `RESEND_API_KEY` | when `resend` | Resend API key |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` | when `smtp` | e.g. `smtp.gmail.com` / `587` / a dedicated Gmail address / its App Password. Uses the standard library's `smtplib` with STARTTLS. |
| `LIFE_INBOX_EMAIL_FROM` | when `resend` | e.g. `Life Inbox <no-reply@auth.lifeinbox.example>` |
| `LIFE_INBOX_SMS_PROVIDER` | all | `twilio_verify` \| `console` \| `fake` \| `disabled` |
| `TWILIO_ACCOUNT_SID` | when `twilio_verify` | |
| `TWILIO_AUTH_TOKEN` | when `twilio_verify` | |
| `TWILIO_VERIFY_SERVICE_SID` | when `twilio_verify` | `VA…` service id |
| `LIFE_INBOX_SMS_ALLOWED_COUNTRIES` | optional | e.g. `IN,DE,FR,IE,NL` |
| `LIFE_INBOX_ALLOW_ANONYMOUS_LOCAL` | local only | `1` keeps the old "Local Owner" demo mode. **Rejected** outside `local`. |
| `LIFE_INBOX_PRIVACY_VERSION` / `LIFE_INBOX_TERMS_VERSION` | all | e.g. `2026-10-15`. If a user has accepted an older version, they are asked to accept again at their next login. |

Removed: `LIFE_INBOX_SESSION_SECRET` (no longer used to sign cookies),
`LIFE_INBOX_AUTH_MODE` and `LIFE_INBOX_ALLOW_DEV_LOGIN`.

Strict validation in beta/production refuses to start if: the email provider is
`console` or `fake`, the pepper is shorter than 32 characters, the public origin
isn't `https://`, or anonymous-local mode is on.

---

## 5. API contract

All bodies are JSON. All state-changing calls need the CSRF headers (§4.5).
Errors use the form `{"detail": "..."}`.

### 5.1 Public (no session)

| Method & path | Body | Success | Notes |
|---|---|---|---|
| `POST /api/auth/otp/request` | `{identifier, purpose}` where `purpose ∈ register\|login\|reset_password` | `202 {"status":"sent_if_eligible","challenge_id","resend_after_s":60}` | Same response whether or not the account exists |
| `POST /api/auth/otp/verify` | `{challenge_id, identifier, code}` | `200 {"verification_token"}` | 400 on a wrong code with `attempts_left`; 410 once expired or used up |
| `POST /api/auth/register` | `{verification_token, display_name, password, accept_terms:true, accept_privacy:true, confirm_adult:true, ai_processing:false}` | `201 user` + cookie | Writes 3–4 `consent_records` |
| `POST /api/auth/login/otp` | `{verification_token}` | `200 user` + cookie | Token must have purpose `login` |
| `POST /api/auth/login/password` | `{identifier, password}` | `200 user` + cookie | Always runs an argon2 check, even for unknown users, so timing reveals nothing. 423 when locked. |
| `POST /api/auth/password/reset` | `{verification_token, new_password}` | `200 user` + cookie | Revokes all other sessions and sends a notice |
| `POST /api/auth/recovery/login` | `{identifier, recovery_code, new_password}` | `200 user` + cookie | Uses up the code, forces a new password and revokes other sessions |

### 5.2 Authenticated

| Method & path | Purpose |
|---|---|
| `GET /api/auth/me` | Current user (no "Local Owner" fallback) |
| `POST /api/auth/logout` | Revoke the current session and clear the cookie |
| `POST /api/auth/logout-all` | Revoke all of the user's sessions |
| `GET /api/auth/sessions` | List active sessions (device, created, last seen, current?) |
| `DELETE /api/auth/sessions/{id}` | Revoke one session |
| `POST /api/auth/reauth` | `{password}` or `{verification_token}` (purpose `reauth`), then `{reauth_token}` valid for 5 minutes. Required for the sensitive actions below. |
| `POST /api/auth/password/change` | `{reauth_token, new_password}` |
| `POST /api/auth/contact/start` | `{identifier}`: sends an OTP to a new email or phone (purpose `verify_contact`) |
| `POST /api/auth/contact/confirm` | `{reauth_token, verification_token}`: links the contact, or replaces the existing one of the same type |
| `POST /api/auth/recovery-codes` | `{reauth_token}`: returns 10 new codes **once**; previous codes are invalidated |
| `GET /api/account/consents` | Current consent state |
| `PATCH /api/account/consents` | `{ai_processing: bool}`: withdrawing must be as easy as granting (GDPR Art. 7(3)) |
| `GET /api/account/export` | ZIP with `profile.json`, `items.json`, `tasks.json`, `topics.json`, `consents.json`, `sessions.json` and `/files/*` |
| `DELETE /api/account` | `{reauth_token, confirm:"DELETE"}` → `202`. Status becomes `pending_deletion`, all sessions are revoked, and confirmation is sent to every channel. |

### 5.3 Removed

- `POST /api/auth/dev-login`
- `GET /api/auth/google/start`

During local development, use `LIFE_INBOX_EMAIL_PROVIDER=console` instead: the
OTP code appears in the server log.

---

## 6. Frontend changes

### 6.1 New files

- `app/templates/login.html`: a standalone page that loads only `auth.js` and
  `styles.css`. **No app markup or app JS reaches the browser before login.**
- `app/static/auth.js` contains these views:
  - `identify`: email or phone field. The phone field has a country selector
    defaulting to +91.
  - `otp`: 6-box code input with paste support, resend countdown and "use
    password instead".
  - `register`: name, password + confirm with a strength meter, and the 3
    required checkboxes plus 1 optional one.
  - `password`: identifier + password, with "Forgot password?" and "Use a
    recovery code".
  - `reset`: OTP followed by a new password.
  - `recovery`: identifier + recovery code + new password.
- `app/templates/privacy.html`, `terms.html` and `delete-account.html`. The
  delete-account page is a public page explaining how to delete an account;
  Google Play requires it.

### 6.2 Changes to existing files

| File | Change |
|---|---|
| `app/templates/index.html:15-21` | Remove the dev-login form. Add a header menu: user name, **Settings**, **Sign out**. |
| `app/templates/index.html` | New Settings panel: profile, email/phone (verified badges), change password, recovery codes, active sessions, AI processing toggle, export data, delete account. |
| `app/static/app.js` | `fetchJson` always sends `X-Requested-With: life-inbox` and `credentials: 'same-origin'`. **Any 401 → `window.location.replace('/login')`.** |
| `app/static/app.js:1418` | Delete `devLogin()`. Rewrite `logoutSession()`: call the API, clear in-memory state, then `location.replace('/login')`. |
| `app/static/app.js:1408` | `loadAuthUser()` no longer shows "Not signed in"; a 401 already redirects to `/login`. |
| `app/main.py:1215` | `GET /` is behind the auth gate, so logged-out users never receive the HTML. |

### 6.3 Accessibility and app-store readiness

- Every input has a label; errors are announced with `aria-live`; the whole flow
  works with the keyboard alone.
- OTP input uses `autocomplete="one-time-code"` and `inputmode="numeric"`, which
  lets iOS and Android autofill codes from SMS.
- Password fields use `autocomplete="new-password"` or `"current-password"` so
  password managers work.

---

## 7. AI processing and consent

Today, item content is sent to OpenAI whenever `OPENAI_API_KEY` is set. Under
GDPR and the DPDP Act, that is a disclosure to a third-party processor and must
be lawful and transparent.

- New per-user flag: `users.ai_processing_enabled`. It is **off by default**
  and is the optional checkbox at registration.
- `app/organizer.py`: when the flag is off, use `fallback_analyze` (already
  exists at `organizer.py:130`) and never call OpenAI.
- `app/retrieval/` Ask: when the flag is off, use the extractive fallback that
  already exists.
- Voice transcription with OpenAI is disabled when the flag is off; the UI says
  "Enable AI processing in Settings to transcribe voice notes".
- The privacy policy names OpenAI as a processor and explains the data transfer
  to the US.

---

## 8. Privacy and compliance controls

### 8.1 Requirements mapped to code

| Requirement | Source | Where it is implemented |
|---|---|---|
| Lawful basis and notice before collecting data | GDPR Art. 6, 13; DPDP s.5 | Privacy notice linked on the register screen; `consent_records` |
| Consent can be proven, and withdrawn as easily as given | GDPR Art. 7; DPDP s.6(4) | `consent_records`; `PATCH /api/account/consents` |
| Collect only what's needed | GDPR Art. 5(1)(c); DPDP s.6(1) | Collected: email/phone, name, password hash. IPs are hashed. No date of birth, only an 18+ confirmation. |
| Right of access and portability | GDPR Art. 15, 20; DPDP s.11 | `GET /api/account/export` |
| Right to correct data | GDPR Art. 16; DPDP s.12 | Settings → edit name and contacts |
| Right to erasure | GDPR Art. 17; DPDP s.12 | `DELETE /api/account` plus the purge job |
| Account deletion inside the app | Apple guideline 5.1.1(v); Google Play account-deletion policy | Settings → Delete account; public `/delete-account` page |
| Security of processing | GDPR Art. 32; DPDP s.8(5) | argon2id, hashed tokens and codes, HTTPS/HSTS, rate limits, audit log, encrypted DB and backups at the host |
| Breach notification | GDPR Art. 33/34 (72 h); DPDP s.8(6) and Rules | `docs/incident-response.md` runbook |
| Children's data | DPDP s.9; GDPR Art. 8 | 18+ confirmation is required; the terms forbid under-18 use |
| Processors | GDPR Art. 28 | Sign the DPAs from Resend, Twilio, OpenAI and the hosting provider; list them in the privacy policy |
| International transfers | GDPR Ch. V | Use Standard Contractual Clauses (part of each processor's DPA) and disclose them in the privacy policy |
| Grievance contact | DPDP s.8(10) | Grievance officer email in the privacy policy and in Settings |
| App Store privacy label / Google Play Data safety form | Both stores | Filled in from `docs/privacy-data-inventory.md` |

### 8.2 Data inventory (summary)

The full table goes in a new `docs/privacy-data-inventory.md`.

| Data | Purpose | Stored where | Retention |
|---|---|---|---|
| Email, phone | Login, recovery, security notices | `users` | Until the account is deleted |
| Password hash | Login | `users` | Until the account is deleted |
| Inbox content, files, tasks | Core service | `inbox_items`, `tasks`, …; uploads folder | Until the user deletes them or the account |
| Session metadata | Security | `auth_sessions` | 90 days after expiry |
| OTP challenges | Login | `otp_challenges` | 24 hours, then purged |
| Auth events | Security, fraud prevention | `auth_events` | 12 months |
| Consent records | Proof of consent (legal obligation) | `consent_records` | 3 years after the account is deleted, keyed by `subject_ref` only |
| Email/SMS delivery logs | Delivery | Resend / Twilio | According to each provider's retention settings |

### 8.3 Account deletion pipeline

Script: `scripts/purge_accounts.py`. It runs daily (cron or a container
schedule).

1. `DELETE /api/account` → `status='pending_deletion'`,
   `deletion_requested_at=now`, all sessions revoked, email and phone kept only
   so the confirmation can be sent.
2. Within 7 days, the user can cancel by logging in. Login is allowed for
   `pending_deletion` users and shows a "Restore account" banner.
3. On day 7, the purge job deletes the child rows in the §3.3 order and the
   files under `uploads/<user_id>/`, sets `consent_records.user_id = NULL` and
   `auth_events.user_id = NULL`, then deletes the user row.
4. Backups age out within 30 days, which is the documented backup retention, so
   erasure is complete within 30 days.

### 8.4 Logging rules

- Never log: OTP codes (except the `console` provider in local mode), passwords,
  session tokens, recovery codes, or full email addresses and phone numbers.
- Use the helpers `mask_email("a***@gmail.com")` and `mask_phone("+91******3210")`.
- Exception messages from providers are cleaned of personal data before
  logging.

---

## 9. Tests

No real emails or SMS are sent in tests: `fake` providers capture codes in
memory, following the AGENTS.md rule against calling paid APIs.

New file `tests/test_auth.py`:

**Registration and OTP**
- Register by email: request code → verify → register → `/api/auth/me` returns the user
- Register by phone: the phone is normalized to E.164 (`98765 43210` with IN → `+919876543210`)
- Wrong code returns `attempts_left`; the 6th attempt returns 410; an expired code returns 410; a used code can't be reused
- Resend before the cooldown → 429; more than 5 per hour → 429
- Registering an existing email returns the same 202 and sends a notice email instead of a code
- Unknown identifier with purpose `login` → 202 and nothing sent
- An SMS to a country not on the allow-list is rejected
- Registration without `confirm_adult`, `accept_terms` or `accept_privacy` → 422
- Each consent decision creates its own consent row with the document version

**Password**
- Password login succeeds; a wrong password increments the counter; the 6th attempt → 423 locked
- OTP login still works while the password is locked
- A weak, common or too-short password → 422
- Stored hash starts with `$argon2id$`
- Forgot-password flow: OTP → new password → old password fails → other sessions revoked
- Recovery-code login works once; the same code fails the second time
- Generating recovery codes invalidates the previous set

**Sessions and logout**
- After logout, the old cookie gets a 401 on `/api/items`
- `logout-all` revokes sessions from two different clients
- Idle expiry and absolute expiry both return 401 (simulated with a frozen clock)
- Each login creates a new token (session fixation check)
- Changing the password revokes all other sessions

**Isolation and gate** (the most important tests)
- **Route sweep:** iterate over `app.routes`; every `/api/*` route not on the public allow-list returns 401 without a cookie. A new route without protection fails this test.
- Users A and B each create items, tasks, topics and files. For every list, get, update, delete and download route, A gets 404 or an empty result for B's data.
- `GET /` without a session → 302 to `/login`; the HTML contains no app markup.
- Path traversal on file download (`../`) → 404.

**Security**
- A POST without `X-Requested-With` or with a foreign `Origin` → 403
- Security headers are present on HTML and API responses
- Config: `LIFE_INBOX_ENV=production` with `console` email or a short pepper → `ConfigError`

**Privacy**
- The export ZIP contains only the requesting user's rows and files
- Delete → status `pending_deletion` → login can restore within 7 days → after the purge job runs, no rows remain for that user in any owned table and the upload folder is gone
- AI processing off → OpenAI client mock is **never** called during analysis, Ask or voice

`tests/test_migrations.py` additions:
- Upgrade an empty database to head
- Upgrade a database seeded at `0011` with data → `0012` → claim script → `0013`
- `0013` fails with a clear message if orphan rows exist

Existing tests: a new fixture `logged_in_client(email)` registers a user through
the fake provider and returns a client holding the cookie.
`tests/test_api.py` and `tests/test_retrieval.py` switch from `dev-login` to
this fixture.

---

## 10. Implementation order

Each step ends with a full green test run and its own commit on
`milestone/7-production-auth`.

| Step | Work | Mainly touches |
|---|---|---|
| 1 | Create the branch; add dependencies; config variables plus strict validation | `requirements.txt`, `app/config.py` |
| 2 | Migration `0012` + models | `migrations/`, `app/database.py` |
| 3 | `app/auth/` package: identifiers, passwords, sessions, rate limit, audit, consent | `app/auth/*` |
| 4 | OTP service with `fake`/`console` providers; auth routes | `app/auth/otp.py`, `routes.py` |
| 5 | Middleware (gate, CSRF, headers); remove the default-owner fallback; remove dev login | `app/main.py`, `app/database.py` |
| 6 | Owner-scoped file storage; secure download | `app/storage_backend.py`, `app/main.py` |
| 7 | Claim script + migration `0013` | `scripts/`, `migrations/` |
| 8 | Login page, Settings panel, 401 redirect | `app/templates/*`, `app/static/*` |
| 9 | Account export, deletion, purge job, AI-consent gating | `app/auth/routes.py`, `scripts/purge_accounts.py`, `app/organizer.py`, `app/retrieval/` |
| 10 | Resend + Twilio Verify adapters, tested against mocked HTTP | `app/auth/providers/*` |
| 11 | Docs: this file → implemented; `deployment.md`, `architecture.md`, `privacy-data-inventory.md`, `incident-response.md`, `AGENTS.md`; milestone report | `docs/*`, `AGENTS.md` |
| 12 | Manual end-to-end run on a temp database with real Resend and Twilio test credentials (owner-provided); tag `milestone-7` | — |

---

## 11. Provider setup (owner actions)

You do these yourself. Agents never create accounts or handle live keys.

### 11.1 Resend (email)

**If you don't own a domain yet**, use one of these stages:

| Stage | Email OTP | SMS OTP | App URL |
|---|---|---|---|
| Local dev (now) | `console` provider (code printed in the server log) | `console` provider | `http://127.0.0.1:8000` |
| Private beta, a few testers | `smtp` provider sending from a dedicated Gmail account with a Google App Password (needs 2-step verification on that account; Gmail daily send limits apply) | Twilio Verify (no domain needed) | Free hosting subdomain, e.g. `*.onrender.com` or `*.fly.dev` (HTTPS included) |
| Public launch / app stores | Resend with your own domain (steps below) | Twilio Verify | Your own domain |

Resend's built-in test sender (`onboarding@resend.dev`) can only email the
address that owns the Resend account, so it's useful for testing the
integration but not for real users. Sending "from" an `@gmail.com` address
through Resend or another service isn't allowed and would land in spam anyway.

A domain costs roughly $10–15 a year (e.g. Cloudflare Registrar, Namecheap,
Porkbun). Buy one before public launch: app stores also expect a privacy
policy URL, support URL and account-deletion URL on a site you control.

1. Create an account at resend.com.
2. **You need a domain you own** (e.g. `lifeinbox.app`). Resend can't send
   from `@gmail.com` addresses. Add a sending subdomain such as
   `auth.lifeinbox.app` and add the DNS records Resend shows (SPF, DKIM, and
   ideally DMARC).
3. Create an API key with **Sending access** only, restricted to that domain.
4. Put it in the deployment secret store as `RESEND_API_KEY`. **Never commit
   it**, never put it in `.env` files inside the repo, and never paste it in chat.
5. Sign Resend's DPA (in the dashboard / legal page).
6. Until steps 1–5 are done, local development uses
   `LIFE_INBOX_EMAIL_PROVIDER=console`, and the code is printed in the server log.

### 11.2 Twilio Verify (SMS)

1. Create a Twilio account and upgrade it from trial; a trial can only text
   verified numbers.
2. Console → Verify → create a **Verify Service** ("Life Inbox"); code length 6.
3. Turn on **Fraud Guard** and set **Geo Permissions** to only the countries
   you serve (same list as `LIFE_INBOX_SMS_ALLOWED_COUNTRIES`).
4. India: check in the Twilio console that Verify covers DLT compliance for
   your use case before launch. If it doesn't, register a DLT sender and
   template.
5. Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` and
   `TWILIO_VERIFY_SERVICE_SID` in the secret store.
6. Sign Twilio's DPA.

Twilio Verify generates, delivers and checks SMS codes itself. Our
`otp_challenges` row keeps the attempts, expiry, rate limits and
`provider_ref`, with `code_hash = NULL`.

### 11.3 Before public launch

- [ ] Domain and HTTPS for the app (`LIFE_INBOX_PUBLIC_ORIGIN`)
- [ ] Managed PostgreSQL with encryption at rest, plus daily backups kept 30 days
- [ ] Privacy policy and terms written and **reviewed by a lawyer**
- [ ] Grievance officer / contact email published (DPDP)
- [ ] DPAs signed: Resend, Twilio, OpenAI, hosting provider
- [ ] `docs/privacy-data-inventory.md` complete; App Store privacy label and Google Play Data safety form filled in from it
- [ ] Public `/delete-account` URL entered in the Google Play Console
- [ ] Incident-response runbook in place

---

## 12. Out of scope for Milestone 7

- Sign in with Google or Apple (social login). If Google is added later, Sign in with Apple becomes mandatory for the iOS app.
- Authenticator-app 2FA (TOTP) and passkeys (WebAuthn). These are the natural next steps after M7.
- Native iOS/Android apps. M7 makes the web backend ready for them; a native app would use the same API with a bearer-token variant of `auth_sessions`.
- Admin console for support staff.
