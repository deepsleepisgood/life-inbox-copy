# Architecture

## Stack

- **API:** FastAPI
- **ORM:** SQLAlchemy
- **Migrations:** Alembic (authoritative schema owner)
- **DB:** SQLite locally (temp/test DBs for development)
- **UI:** HTML + vanilla JS/CSS
- **AI:** NVIDIA NIM (`https://integrate.api.nvidia.com/v1`); deterministic fallback organizer always available
- **Voice / Speech:** Browser MediaRecorder + ffmpeg 16kHz WAV conversion + NVIDIA NIM ASR (`openai/whisper-large-v3`) + NVIDIA NIM LLM transcript cleanup (`meta/llama-3.1-70b-instruct`)

## Core modules

| Module | Responsibility |
| --- | --- |
| `app/main.py` | HTTP routes, error shaping, startup health checks |
| `app/database.py` | Models, persistence helpers, fingerprints, task upsert |
| `app/schemas.py` | Request/response and analysis contracts |
| `app/organizer.py` | NVIDIA NIM + fallback organization |
| `app/capture/` | Rich capture (URL, PDF, image, voice note pipeline) |
| `app/retrieval/` | Keyword + local TF-IDF search, grounded Ask My Inbox (NVIDIA NIM) |
| `app/attention/` | Timing parse, attention buckets, briefing helpers |
| `app/integrations/` | Replaceable Calendar adapter (mock / preview-only Google) |
| `app/auth.py` / `app/config.py` | Password login (argon2id), server-side sessions (`auth_sessions`), startup config validation |
| `app/storage_backend.py` | Upload storage abstraction (local FS default) |
| `app/templates` / `app/static` | Browser UI |

## Data model (current)

- `inbox_items` — canonical captures
- `notes` — legacy safety copy (not authoritative)
- `topics` — user-editable spaces/projects (seeded defaults)
- `analysis_runs` — analyze attempts + JSON result (includes inbox fingerprint)
- `item_insights` — AI category/title/priority/tags/rationale/topic plus user overrides
- `item_relations` — duplicate / near-duplicate / related pairs (dismissible)
- `tasks` / `task_source_items` — durable tasks; multiple tasks per source allowed;
  AI vs confirmed timing distinguished, with normalized optional local due time
- `notification_preferences`, `push_subscriptions`, and
  `notification_deliveries` — per-user Web Push opt-in, browser subscriptions,
  and idempotent delivery/retry history

## Analysis freshness

Successful analysis stores an `inbox_fingerprint` hash of inbox content.
`GET /api/analyze/latest` recomputes the hash and sets `is_stale` when the
inbox has changed since that run.

## Schema evolution

1. Change SQLAlchemy models
2. Add an Alembic revision under `migrations/versions/`
3. `alembic upgrade head` on empty and previous-milestone DBs in the quality gate

`LIFE_INBOX_AUTO_CREATE_TABLES=1` is allowed only for isolated automated tests.

## Rich capture lifecycle

URL, PDF, image, and voice captures follow: **capture → save original →
process → extract → organize → ready/failed**.

- Original sources are persisted before extraction (`source_url` or `storage_path`).
- `processing_status`: `captured`, `processing`, `ready`, `failed`.
- `POST /api/items/{id}/retry` re-runs processing for failed capture items.
- Images: OCR text in `extracted_text` (editable facts); AI copy in
  `ai_description` (inferred). Thumbnails via `?variant=thumb`.
- Voice: original audio retained; transcript in `extracted_text` (editable);
  browser MediaRecorder upload supported when the mic is available.
- Ready captures feed organization via `list_notes_from_db()` (uses `extracted_text`).

Uploads default to `data/uploads/` (override with `LIFE_INBOX_UPLOAD_DIR`).
OCR/vision/transcription adapters degrade gracefully when not configured
(`LIFE_INBOX_DISABLE_OCR=1`, `LIFE_INBOX_DISABLE_TRANSCRIPTION=1` for tests).

## Retrieval + Ask My Inbox

- `GET /api/search?q=` — ranked passages with keyword and semantic scores
- `POST /api/ask` — extractive grounded answers with per-item citations
- Insufficient evidence returns an explicit “not enough information” response (no fabrication)
- Semantic layer is local TF-IDF cosine similarity (no vector database, no paid API in tests)

## Attention & safe actions

- Timing phrases stay on tasks (`timing_text` / `ai_timing_text`); normalized
  `due_on` + `due_confidence` power Today/Upcoming/Overdue/Unscheduled views.
- Ambiguous timing sets `needs_confirmation` until the user confirms.
- Snooze / reminder fields are local only (`snoozed_until`, `reminder_at`).
- Opted-in browser push sends one daily digest for open tasks due on the user's
  local date. AI-linked High-priority tasks with an explicit, unambiguous time
  also receive a push one hour before. Date-only tasks are never assigned a
  guessed time. Undated tasks are not scheduled; users may opt into a simple
  count prompt in the digest.
- `python -m app.notifications.dispatcher` is the one-shot scheduler entry
  point and must run once per minute in deployments. The Compose
  `notifications` service provides a local minute-loop worker. Push requires
  HTTPS, browser permission, and VAPID keys.
- Calendar integrations: `GET /api/calendar/status`, `POST /api/calendar/preview`,
  `POST /api/calendar/confirm`. Mock confirm stores a local receipt.
  Google provider is preview-only; confirm is blocked (no OAuth / no writes).

## In-App Calendar

- **Single Source of Truth**: The existing `tasks` table (`TaskRecord`) stores canonical date metadata (`due_on`, `due_confidence`, `timing_text`, `timing_confirmed`). Joined with `task_source_items` and `inbox_items` to retrieve full provenance without a separate event table or migrations.
- **Endpoint**: `GET /api/calendar/events?start=YYYY-MM-DD&end=YYYY-MM-DD` provides read-only, performant queries filtered by date range and user isolation (`require_owner_id()`). Zero LLM / external API calls on page load.
- **Date Normalization**: `app/attention/dates.py:parse_timing_phrase` parses ISO dates, Month-Day ("Nov 3"), Day-Month ("3 Nov"), Month-only ("sometime in March"), relative expressions ("next Friday", "tomorrow"), and explicit time strings.
- **Lifecycle Rules**:
  - Notes without dates are completely excluded.
  - Completed tasks are displayed struck through with completion indicators.
  - Dismissed tasks are excluded from the calendar.
  - Deleting a source note cascades to orphan tasks and immediately removes calendar entries.
- **Frontend & Interactions**: Vanilla JS month grid with ARIA accessibility, keyboard navigation, event indicators, day inspector with source badges (`text`, `voice`, `url`, `pdf`, `image`), and smooth-scroll/pulse highlighting to source notes. Automatically refreshes on note creation, edit, deletion, or analysis.

## External services

Automated tests mock OpenAI and must not call paid APIs. Live calls are for
explicit manual smoke testing only. Never enable real Calendar OAuth/writes
without owner approval.
