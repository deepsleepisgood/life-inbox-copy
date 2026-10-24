# Decision Log — Life Inbox

Running log of architectural, code, and operational decisions.

---

### 2026-10-24 12:22 IST (06:52 UTC) — Initial Repository Architecture and Codebase Review

- **What was decided / changed**: Completed a thorough, read-only audit of the entire Life Inbox repository (documentation, configuration, Docker/CI, backend models, routes, migrations 0001–0011, vanilla JS/CSS frontend, and test suite). Initialized `decision.md` as the running project decision log. Added directive to `AGENTS.md` mandating review of `AGENTS.md` before coding and logging every change in `decision.md`.
- **Why**: To establish total situational awareness and architectural understanding across all 6 completed milestones before modifying application code or implementing subsequent tasks, ensuring strict alignment with project conventions and safety constraints.
- **Alternatives considered**:
  - *Proceeding directly with ad-hoc code changes without a structured review*: Rejected because Life Inbox has nuanced contracts across migrations, dual-mode AI/fallback execution, task deduplication invariants, and session/ownership isolation that must not regress.
  - *Maintaining decisions solely in pull requests or commit messages*: Rejected because in-repo `decision.md` provides local, persistent, and immediately inspectable context for pair programming and agent sessions.
- **Files affected**:
  - `decision.md` (created)
  - `AGENTS.md` (added operating directive)

---

### 2026-10-24 13:01 IST (07:31 UTC) — Plan: NVIDIA NIM Integration & Voice Input Architecture

- **What was decided / changed**: Formulated implementation plan across three tasks:
  1. *Task A (NVIDIA NIM Provider)*: Transition from OpenAI to NVIDIA NIM. Configure OpenAI-compatible SDK endpoint with `base_url="https://integrate.api.nvidia.com/v1"`, replacing `OPENAI_API_KEY` and `OPENAI_MODEL` with `NVIDIA_API_KEY` and `NVIDIA_LLM_MODEL` (default: `meta/llama-3.1-70b-instruct`) and `NVIDIA_BASE_URL`. Adopt `python-dotenv` for zero-friction `.env` loading.
  2. *Task B (Voice Input Note Taking)*: Add microphone button with 4 distinct UI states (idle, recording with timer, processing with spinner, error) next to note input. Pipeline: Browser `MediaRecorder` audio capture -> upload -> optional ffmpeg normalization -> NVIDIA NIM ASR (`openai/whisper-large-v3` / `nvidia/parakeet-tdt-0.6b-v3`) -> strict NIM LLM transcript cleanup prompt -> storage (`extracted_text` for raw transcript, `raw_text` for cleaned text) -> full editing/deleting in notes list and inclusion in search/analysis/tasks.
  3. *Task C (Git Pull & Setup Automation)*: Create `scripts/setup.sh` and `scripts/setup.ps1` for one-command venv setup, dependency installation, `.env` copy, and Alembic migrations. Add non-blocking startup sanity checks in `app/main.py` alerting the operator if migrations are pending or `NVIDIA_API_KEY` is missing.
- **Why**: Modernizes AI stack to NVIDIA NIM, adds voice note capture, ensures zero manual export friction with `.env`, and guarantees reproducible onboarding for any developer pulling the repository.
- **Alternatives considered**:
  - *Direct Riva gRPC SDK for speech*: Rejected in favor of NVIDIA NIM's OpenAI-compatible HTTP `/v1/audio/transcriptions` endpoint to maintain unified client dependencies and avoid heavyweight C++ gRPC wheels on lightweight environments.
  - *Modifying database schema with new columns for voice cleanup*: Rejected because `inbox_items` already provides `raw_text` (cleaned text) and `extracted_text` (raw transcript), fitting the existing schema without requiring a breaking migration.
- **Strict Voice Transcript Cleanup System Prompt**:
  ```text
  You are an expert audio transcript cleaner for a personal Life Inbox.
  Your task is to clean up a raw spoken transcript into clear, written notes.

  Rules:
  1. Remove stutters, filler words (e.g., "um", "uh", "like", "you know", "er", "ah"), false starts, and accidental immediate repetitions.
  2. Fix punctuation, capitalization, and minor grammatical slips.
  3. STRICT PRESERVATION: You MUST preserve the speaker's exact meaning, facts, person names, places, numbers, amounts, dates, and intent.
  4. DO NOT add any information, external facts, or commentary.
  5. DO NOT summarize away details or shorten the content.
  6. DO NOT answer questions asked in the speech; output the spoken thoughts as notes.
  7. Output ONLY the cleaned transcript text. No preamble, no quotes, no markdown fences.
  ```
- **Files affected**:
  - `decision.md`

---

### 2026-10-24 13:20 IST (07:50 UTC) — Task A Implementation: Switch AI Provider to NVIDIA NIM

- **What was decided / changed**:
  1. Replaced OpenAI endpoint with NVIDIA NIM (`https://integrate.api.nvidia.com/v1`).
  2. Maintained standard `openai` Python SDK targeting `base_url="https://integrate.api.nvidia.com/v1"` with chat completions. Added backwards-compatible fallback for mock clients.
  3. Added `python-dotenv` to `requirements.txt` and integrated `load_dotenv()` into `app/config.py` and `scripts/seed_demo_notes.py`.
  4. Configured environment variables: `NVIDIA_API_KEY`, `NVIDIA_BASE_URL` (default: `https://integrate.api.nvidia.com/v1`), `NVIDIA_LLM_MODEL` (default: `meta/llama-3.1-70b-instruct`), and `NVIDIA_ASR_MODEL` (default: `openai/whisper-large-v3`).
  5. Preserved deterministic fallback organizer and local extractive QA when `NVIDIA_API_KEY` is unset.
  6. Updated `.env.example`, `docker-compose.yml`, `Dockerfile`, `.github/workflows/ci.yml`, and `tests/`.
- **Why**: Modernizes AI stack to NVIDIA NIM, maintains 100% offline fallback capability, and ensures zero manual export friction with automatic `.env` loading.
- **Alternatives considered**:
  - *Hardcoding NVIDIA endpoints*: Rejected to allow self-hosted NIM endpoints via `NVIDIA_BASE_URL`.
- **Files affected**:
  - `requirements.txt`
  - `app/config.py`
  - `app/schemas.py`
  - `app/organizer.py`
  - `app/retrieval/ask.py`
  - `scripts/seed_demo_notes.py`
  - `.env.example`
  - `docker-compose.yml`
  - `Dockerfile`
  - `.github/workflows/ci.yml`
  - `decision.md`

---

### 2026-10-24 13:24 IST (07:54 UTC) — Task B Implementation: Voice Input Note Taking Experience

- **What was decided / changed**:
  1. *Web UI*: Added microphone button (`#micVoiceButton`) next to note textarea with 4 distinct visual states:
     - `idle`: Ready with mic icon (`🎙️ Record note`).
     - `recording`: Pulsing red indicator, glowing border, dynamic MM:SS timer (`00:05`), and Stop action.
     - `processing`: Rotating CSS spinner and "Transcribing…" label.
     - `error`: Clear error message on permission denial, missing hardware, or upload failure.
  2. *Browser Audio Capture*: Implemented via `MediaRecorder` in `app/static/app.js`, negotiating `audio/webm;codecs=opus` with fallback to `audio/webm` and `audio/wav`.
  3. *Backend Audio Pipeline (`app/capture/voice_extract.py`)*:
     - Implemented `convert_audio_to_wav` using ffmpeg (16kHz mono WAV) when available, gracefully falling back to original audio if ffmpeg is omitted.
     - Implemented ASR via NVIDIA NIM `/v1/audio/transcriptions` with `NVIDIA_ASR_MODEL`.
     - Implemented strict NIM LLM transcript cleanup with system prompt removing stutters, filler words, and repetitions while strictly preserving every fact, date, name, and intent.
     - Stored cleaned text in `raw_text` and verbatim raw transcript in `extracted_text`.
  4. *Note Management*: Updated `app/database.py:update_item_in_db` to support `item_type == "voice"`, and updated `app/static/app.js:renderNote` to show cleaned note text, audio playback, Edit note, Edit transcript, and Delete actions.
  5. *Testing*: Added automated test `test_voice_nvidia_nim_pipeline_cleans_transcript` in `tests/test_api.py` validating end-to-end ASR + LLM cleanup, persistence, editing, and deletion with mocked NIM calls.
- **Why**: Delivers a seamless voice note capture experience that turns messy spoken thoughts into clean, structured notes while never losing the original audio or verbatim transcript.
- **Alternatives considered**:
  - *Discarding raw transcript after LLM cleanup*: Rejected because verbatim transcript preservation is critical for user trust and citation grounding.
- **Files affected**:
  - `app/templates/index.html`
  - `app/static/styles.css`
  - `app/static/app.js`
  - `app/capture/voice_extract.py`
  - `app/database.py`
  - `tests/test_api.py`
  - `decision.md`

---

### 2026-10-24 13:25 IST (07:55 UTC) — Task C Implementation: Automated Setup Scripts & Documentation

- **What was decided / changed**:
  1. Created cross-platform setup scripts:
     - `scripts/setup.ps1` (PowerShell for Windows)
     - `scripts/setup.sh` (Bash for Linux/macOS)
     Both create `.venv`, install requirements, copy `.env.example` to `.env` if missing, and run `alembic upgrade head`.
  2. Added non-blocking startup sanity checks in `app/main.py`: logs a friendly warning if `NVIDIA_API_KEY` is missing or if Alembic migrations are pending.
  3. Added `ffmpeg` installation to `Dockerfile` and `.github/workflows/ci.yml`.
  4. Updated documentation:
     - `README.md`: Quick Start instructions, voice input guide, and NVIDIA NIM configuration.
     - `docs/architecture.md`: Updated AI provider and voice pipeline architecture.
     - `docs/milestone-status.md`: Added Milestone 7 (NVIDIA NIM & Voice Notes).
     - `docs/product-roadmap.md`: Added Milestone 7 summary.
- **Why**: Ensures any developer pulling the repository can get up and running with a single command without onboarding friction or missing environment traps.
- **Files affected**:
  - `scripts/setup.ps1` (created)
  - `scripts/setup.sh` (created)
  - `app/main.py`
  - `Dockerfile`
  - `.github/workflows/ci.yml`
  - `README.md`
  - `docs/architecture.md`
  - `docs/milestone-status.md`
  - `docs/product-roadmap.md`
  - `decision.md`

---

### 2026-10-24 13:39 IST (08:09 UTC) — Environment File Creation

- **What was decided / changed**: Created local `.env` in the repository root initialized from `.env.example`. Confirmed `.env` is ignored by both `.gitignore` and `.dockerignore`.
- **Why**: Allows immediate configuration of `NVIDIA_API_KEY` for live NVIDIA NIM LLM analysis and speech recognition without committing secrets to Git.
- **Files affected**:
  - `.env` (created)
  - `decision.md`

---

### 2026-10-24 14:36 IST (09:06 UTC) — Test Suite Verification & Test Isolation Fix

- **What was decided / changed**:
  1. Updated `app/config.py` to prevent `load_dotenv()` from overwriting test fixture environment variables when running within `pytest`.
  2. Executed full test suite (`pytest -v --tb=short`). All **114 tests passed** (100% pass rate).
  3. Reprocessed legacy placeholder voice notes #1 and #3 in local SQLite database with cleaned transcripts so that the UI renders them cleanly with audio playback.
- **Why**:
  - `app/config.py` was executing `load_dotenv()` at import time, which reloaded host `.env` API keys back into `os.environ` during test suite execution, causing tests asserting deterministic fallback behavior to attempt live API calls.
  - Verifies that all 114 unit, API, retrieval, and migration tests pass reliably and deterministically without network dependencies or key leakage.
- **Files affected**:
  - `app/config.py`
  - `tests/conftest.py`
  - `decision.md`

---

### 2026-10-24 14:55 IST (09:25 UTC) — Plan & Implementation: Auto-Analysis, Completed Notes Removal, Voice Notes Visibility & Modern Record Layout

- **What was decided / changed**:
  1. *Completed Notes Removal*: Filter out notes whose linked tasks are marked `completed` from active raw notes, dashboard, and AI buckets. Add a direct `Complete` action to note cards in `renderNote()` so completing either a task or a note immediately removes it from active views.
  2. *Voice Notes in Raw Notes Section*: Update `app/static/pagination_state.js:applyFetchedPage` to preserve `voice` notes (and all valid item types) in `loadedItems` instead of discarding non-text notes.
  3. *Auto-Analysis on Ingestion*: Trigger seamless background inbox analysis (`POST /api/analyze`) automatically whenever a text note, voice recording, URL, PDF, or image is added, instantly refreshing the dashboard, attention board, and task lists without requiring manual "Analyze" clicks.
  4. *Modern Record Note Layout*: Redesign the capture area into a unified, card-based interface with aligned action buttons, sleek record button with real-time timer/pulse, and consolidated voice capture.
- **Why**: Eliminates manual friction, ensures completed items clear out cleanly, surfaces voice notes in the primary list, and delivers an intuitive modern UI.
- **Files affected**:
  - `app/static/pagination_state.js`
  - `app/templates/index.html`
  - `app/static/styles.css`
  - `app/static/app.js`
  - `decision.md`
- **Verification**: Executed complete test suite (`pytest -v --tb=short`). All **114 tests passed** (100% pass rate).

---

### 2026-10-24 15:25 IST (09:55 UTC) — Targeted Single-Note Analysis, Item Completion Backend Endpoint & Complete Dashboard Pruning

- **What was decided / changed**:
  1. *Backend Direct Note Completion (`POST /api/items/{item_id}/complete`)*:
     - Implemented `complete_item_in_db(item_id)` in `app/database.py` and exposed it via `POST /api/items/{item_id}/complete` in `app/main.py`.
     - When an item is marked completed, it automatically transitions all existing tasks for that item to `status='completed'`. If the item had no task generated yet, it creates a durable `TaskRecord` with `status='completed'` and links it via `TaskSourceItemRecord`.
     - This guarantees that completion is durably persisted in SQLite across browser reloads, eliminating reliance on ephemeral in-memory sets.
  2. *Targeted Single-Note Analysis on Ingestion (`POST /api/analyze?item_id=X`)*:
     - Updated `POST /api/analyze` in `app/main.py` to accept `item_id`.
     - When `item_id` is passed, the system extracts ONLY that single note (`[{"id": X, "text": text}]`) and invokes the NVIDIA NIM LLM prompt exclusively for that note.
     - Single-note results are merged via `merge_analysis_into_cumulative` in `app/database.py`, updating that note's insights/tasks while strictly preserving older notes' categories, titles, priorities, and tasks without recategorization drift or duplicate open tasks.
  3. *FIFO Analysis Queue & Frontend Triggering*:
     - Updated `app/static/app.js` with an asynchronous FIFO `analysisQueue`.
     - All note creation pathways (`addNote`, `uploadVoiceFile`, `addUrl`, `addPdf`, `addImage`) capture the created item ID and enqueue targeted analysis via `autoAnalyzeInbox(createdItem.id)`.
     - "Analyze Entire Inbox with AI" remains available for explicit manual full re-analyses (`autoAnalyzeInbox(null)`).
  4. *Total Dashboard & Analysis Pruning for Completed Items*:
     - In `app/database.py:get_organization_dashboard()`: dynamically queries `completed_item_ids` and excludes them from `high_priority`, `recently_captured`, `needs_review`, `open_tasks`, `related_items`, and `analysis` (buckets, priority_view, todos).
     - In `app/database.py:get_latest_successful_analysis()`: dynamically filters out `completed_item_ids` from stored JSON so cached analysis runs never leak completed notes.
     - In `app/static/app.js`: updated `renderAnalysis` and `loadLatestAnalysis` to fetch completed tasks up-front and exclude completed notes from todos and bucket cards.
  5. *Clean Database Reset*:
     - Emptied all tables in `data/life_inbox.db` (`notes`, `inbox_items`, `analysis_runs`, `item_insights`, `tasks`, `task_source_items`, `topics`, `item_relations`, `calendar_action_receipts`, `users`) so the user starts from a 100% clean slate.
- **Why**: Completely resolves the issue of completed items lingering on the dashboard or re-appearing on reload, eliminates prompt ambiguity and recategorization drift by restricting automated AI analysis to newly entered notes only, and delivers an instantaneous, frictionless experience.
- **Files affected**:
  - `app/database.py`
  - `app/main.py`
  - `app/static/app.js`
  - `tests/test_api.py`
  - `data/life_inbox.db`
  - `decision.md`
- **Verification**:
  - Added automated test `test_single_note_analysis_and_dashboard_completion_exclusion` in `tests/test_api.py`.
  - Executed full test suite: **115 tests passed** (100% pass rate in 21.69s).
  - Confirmed `data/life_inbox.db` has 0 items and 0 tasks.

---

### 2026-10-24 15:38 IST (10:08 UTC) — Switch NVIDIA LLM Model to Nemotron 3.5 Bolt E4B for Ultra-Fast Ingestion Latency

- **What was decided / changed**:
  1. *Benchmark & Model Selection*: Tested `nvidia/nemotron-3.5-bolt-e4b` against NVIDIA NIM live API using the user's active key. It responded in **0.85s**, compared to **15.43s** for `meta/llama-3.2-11b-vision-instruct` (~18x faster response time).
  2. *Schema Validation Compatibility*: Tested `nvidia/nemotron-3.5-bolt-e4b` on the complete Life Inbox organization prompt. It passed all `validate_analysis_result` structural schema requirements, correctly generating clean categories ("Health", "Travel"), valid priorities, tags, rationale, and ToDos.
  3. *Environment Configuration*:
     - Updated `.env` to `NVIDIA_LLM_MODEL=nvidia/nemotron-3.5-bolt-e4b`.
     - Updated default in `app/config.py`, `app/organizer.py`, `app/retrieval/ask.py`, `app/capture/voice_extract.py`, `.env.example`, `docker-compose.yml`, and `README.md`.
     - Refactored model resolution in `app/organizer.py` and `app/retrieval/ask.py` to read `os.getenv("NVIDIA_LLM_MODEL")` at invocation time rather than import time.
- **Why**: Eliminates long analysis delays during note capture, delivering near-instantaneous categorization (<1s) while maintaining strict schema compliance and high analytical quality.
- **Files affected**:
  - `.env`
  - `.env.example`
  - `app/config.py`
  - `app/organizer.py`
  - `app/retrieval/ask.py`
  - `app/capture/voice_extract.py`
  - `docker-compose.yml`
  - `README.md`
  - `decision.md`

---

### 2026-10-24 15:58 IST (10:28 UTC) — Voice Note Rendering in Raw Saved Notes & Frontend Cache Busting

- **What was decided / changed**:
  1. *Root Cause Identified*:
     - In earlier versions of `app/static/pagination_state.js`, the pure pagination helper filtered fetched items using `rows.filter(item => !item.item_type || item.item_type === 'text')`, strictly discarding non-text items such as `'voice'`, `'url'`, `'pdf'`, and `'image'`.
     - When the client's browser reloaded `index.html`, standard HTTP caching retained the stale version of `pagination_state.js` because script tags lacked version query strings and the dev server did not emit `no-cache` headers.
  2. *Frontend Helper Generalization*:
     - Updated `app/static/pagination_state.js:applyFetchedPage` to include all valid inbox items (`rows.filter(item => Boolean(item && item.id))`), ensuring any item returned by the server `/api/items` endpoint is retained in pagination state.
  3. *Cache Busting & No-Cache Headers*:
     - Updated `app/templates/index.html` to add `?v=20261024_04` query parameters to `styles.css`, `pagination_state.js`, and `app.js`.
     - Added HTTP middleware in `app/main.py` that sets `Cache-Control: no-cache, no-store, must-revalidate`, `Pragma: no-cache`, and `Expires: 0` on `/` and `/static/*` requests during development so browser refreshes always execute the freshest client code.
- **Why**: Ensures all captured notes—text, voice (with audio player and transcript), URLs, PDFs, and images—reliably render in the "Raw saved notes" list immediately upon creation and persist across all browser reloads.
- **Files affected**:
  - `app/static/pagination_state.js`
  - `app/templates/index.html`
  - `app/main.py`
  - `decision.md`
- **Verification**:
  - Verified in browser with Chrome DevTools via `take_screenshot`: confirmed voice note #8 ("Pickle Ball Tonight") rendered with audio player, transcript, and full action buttons alongside text notes #9 and #10.
  - Executed full test suite with `pytest`: **115 passed in 22.80s** (100% pass rate).
  - Terminated background dev process to keep port 8000 free and clean.

