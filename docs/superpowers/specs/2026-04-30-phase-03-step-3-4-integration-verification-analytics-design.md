# Phase 3 Step 3.4 Integration Verification And Analytics Design

## Status

Approved for implementation by the 2026-04-30 Codex request. The user explicitly requested an end-to-end implementation without repeated approval checkpoints, so this spec records the design used for the implementation slice.

## Context

Phase 3 Step 3.1 established the local Moodle development instance and REST connectivity proof. Step 3.2 added Moodle Lane A provisioning through `MoodleSyncService`, retryable outbox records, and Moodle user/course mapping tables. Step 3.3 added Moodle Lane B LTI v1.3 launch support with JWKS, OIDC login, launch validation, launch sessions, and embedded advising/registration pages.

Step 3.4 is the integration-verification and analytics-ingestion gate. It must prove the full Moodle integration surface is testable and add the first Moodle engagement ingestion foundation needed before any later at-risk or AI work.

Phase 3.5 remains future scope only. This design does not implement dashboards, notifications, reporting, audit viewers, document management, admissions intake, AI co-pilot, at-risk scoring, or wellbeing support.

## Goal

Implement a controlled Moodle engagement ingestion foundation and formal integration verification artifacts so Step 3.4 can validate the end-to-end Moodle integration path without making a live Moodle instance mandatory for normal automated tests.

## Scope

### In Scope

- Add a Step 3.4 Markdown test matrix covering Lane A, Lane B, analytics ingestion, failures, security, and optional live Moodle checks.
- Add `MoodleEngagementIngestionRun` to record each manual/scheduled ETL run.
- Add `MoodleEngagementSnapshot` to store Moodle engagement-like data linked to SIS user/student/section mappings where available.
- Add a `MoodleEngagementService` that uses `MOODLE_BASE_URL` and `MOODLE_WS_TOKEN`.
- Use Moodle REST function `core_enrol_get_enrolled_users` as the first stable engagement source.
- Store course/user access timestamps from Moodle where available.
- Keep assignment, quiz, and forum metrics nullable in this slice.
- Add `python manage.py ingest_moodle_engagement` with `--section-id`, `--user-id`, `--dry-run`, `--limit`, and `--since`.
- Add a lightweight non-live readiness command, `python manage.py verify_phase_3_integrations`, to report config presence, mapping counts, outbox state, and latest ingestion run.
- Add mocked backend tests for success, missing config, HTTP failure, Moodle exception payloads, invalid JSON, unmapped users, dry run, command summaries, and token safety.
- Surface the latest stored engagement snapshot in the advising LTI roster payload.
- Add a small advising LTI frontend student-selection view using the roster data already returned by the protected LTI context API.
- Update docs, runbooks, and changelogs.

### Out Of Scope

- Live Moodle as a mandatory automated test dependency.
- Assignment/quiz/forum deep extraction beyond nullable schema fields and documented future expansion.
- At-risk scoring or at-risk alert generation.
- AI co-pilot, RAG, AI audit logging, or wellbeing support.
- Phase 3.5 dashboards or operational UI.
- New secrets, committed tokens, committed private keys, or copied launch JWTs.

## Architecture

### 1. Data Model

Add two integration-app models:

- `MoodleEngagementIngestionRun`
  - records run status, dry-run flag, start/completion timestamps, inspected course/user counts, snapshot create/update counts, skipped unmapped user count, failure count, last safe error, and a small summary payload.
- `MoodleEngagementSnapshot`
  - records a per-run Moodle user/course snapshot with optional links to SIS `User`, `StudentProfile`, and `CourseSection`.
  - stores Moodle user/course IDs, Moodle last access timestamp, Moodle course last access timestamp, nullable assignment/quiz/forum metrics, a minimal raw summary payload, and collection timestamps.

The raw summary payload is intentionally small and does not store tokens, private keys, or copied personal profile data already available through SIS mappings.

### 2. Moodle Engagement Service

`MoodleEngagementService` lives in `backend/apps/integration/services.py` with the existing Moodle integration service. It follows the existing safe-request pattern:

- require `MOODLE_BASE_URL` and `MOODLE_WS_TOKEN`
- call `POST {MOODLE_BASE_URL}/webservice/rest/server.php`
- include `wstoken`, `wsfunction`, and `moodlewsrestformat=json`
- handle HTTP errors, invalid JSON, and Moodle exception payloads
- return safe errors that never include the token

The first source function is `core_enrol_get_enrolled_users` per course map. Moodle commonly returns user-level access fields such as `lastaccess` and `lastcourseaccess` in this response. If a Moodle instance omits either field, the snapshot stores `null`.

### 3. Filtering And Dry Run

The service supports:

- `section_id`: inspect one mapped section only
- `user_id`: keep snapshots for one mapped SIS user only
- `limit`: cap the number of mapped courses inspected
- `since`: skip snapshots whose available access timestamps are older than the parsed date/datetime
- `dry_run`: call Moodle and compute summary counts without writing snapshots

Dry runs still create an ingestion run record, but create no snapshots.

### 4. LTI Advising Context

The protected LTI context API remains the authority for embedded tool data. Step 3.4 extends the advising roster payload with an optional `engagement` object based on the latest stored snapshot for that mapped student and section.

The frontend advising page keeps the existing read-only design and adds a compact student-selection panel over the roster. This supports the Step 3.4 verification requirement without adding mutation paths or Phase 3.5 dashboards.

### 5. Verification Helper

`verify_phase_3_integrations` is intentionally non-live by default. It reports:

- Moodle REST config present or missing
- LTI config present or missing
- Moodle user/course mapping counts
- pending/failed integration outbox counts
- latest Moodle engagement ingestion run status

It does not call Moodle unless a later slice explicitly adds a live option.

## Moodle Web Service Functions

Step 3.4 requires this additional function for engagement ingestion:

- `core_enrol_get_enrolled_users`

The SRS also lists assignment, quiz, and forum functions for richer future analytics:

- `mod_assign_get_submissions`
- `mod_quiz_get_user_attempts`
- `mod_forum_get_forum_discussions_paginated`

Those richer functions are not implemented in this slice because they require broader Moodle activity discovery and per-module handling. The schema leaves nullable fields for those metrics and the docs call out the limitation.

## Security And Privacy

- Moodle tokens are read from environment variables only.
- No tokens, private keys, ID tokens, or copied LTI JWTs are stored in snapshots or run summaries.
- Error messages include the Moodle function name but not request payload secrets.
- Snapshots link to existing SIS records instead of duplicating names, emails, or other unnecessary personal data.
- Raw summary data is limited to operational Moodle IDs, access timestamps, roles, and source metadata.
- Unmapped Moodle users are counted and skipped rather than creating orphaned personal records.

## Testing Strategy

Automated tests use mocked Moodle HTTP responses and do not require live Moodle.

Tests cover:

- successful engagement ingestion for a mapped Moodle user/course
- missing Moodle config
- Moodle HTTP failure
- Moodle exception payload
- invalid JSON
- unmapped Moodle user skipped safely
- dry-run command creates a run but no snapshots
- normal command creates snapshots and prints summary counts
- command/service errors do not leak Moodle tokens
- LTI advising context includes latest engagement summary when a snapshot exists

Regression verification includes existing Step 3.1, Step 3.2, and Step 3.3 tests.

## Documentation

Docs must record:

- Step 3.4 verifies the full Moodle integration flow.
- Step 3.4 introduces Moodle engagement analytics ingestion foundation.
- Step 3.4 does not implement at-risk scoring.
- Step 3.4 does not implement Phase 3.5 dashboards.
- Live Moodle verification remains optional for automated testing.
- Phase 3.5 remains future scope after Step 3.4.

## Rollback

This slice is additive. Rollback is a normal code/database rollback:

- remove the Step 3.4 management commands
- roll back the migration adding engagement run/snapshot tables
- remove the LTI roster engagement fields
- remove the Step 3.4 documentation and test matrix

No Moodle core changes are required.
