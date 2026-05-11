# Phase 3 Step 3.2 Moodle Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans when implementing this plan task-by-task. Steps use checkbox syntax for progress tracking.

**Goal:** Deliver a tested Moodle Lane A provisioning baseline for SIS users, sections, enrollments, and official-grade pass-back foundations using the existing integration app and a retryable outbox.

**Architecture:** Extend the existing `IntegrationOutboxEvent` into a retryable sync record, add minimal Moodle user/course maps, process events through a `MoodleSyncService`, and keep normal test runs independent from a live Moodle instance.

**Tech Stack:** Django 5, requests, pytest, existing integration app, MySQL migrations, repository runbooks and changelogs

---

## Status

Plan written on 2026-04-26 from the approved Step 3.2 design in `docs/superpowers/specs/2026-04-26-phase-03-step-3-2-moodle-sync-design.md`.

## File Map

- Create: `backend/apps/integration/services.py`
- Create: `backend/apps/integration/tests/test_moodle_sync_service.py`
- Create: `backend/apps/integration/tests/test_process_moodle_sync_command.py`
- Create: `backend/apps/integration/management/commands/process_moodle_sync.py`
- Create: new integration migration(s)
- Create: `docs/superpowers/specs/2026-04-26-phase-03-step-3-2-moodle-sync-design.md`
- Create: `docs/superpowers/plans/2026-04-26-phase-03-step-3-2-moodle-sync.md`
- Modify: `backend/apps/integration/models.py`
- Modify: `backend/apps/academics/services.py`
- Modify: `backend/apps/academics/api/serializers.py`
- Modify: `backend/apps/accounts/api/serializers.py`
- Modify: `backend/apps/accounts/api/views.py`
- Modify: `backend/sis_backend/settings.py`
- Modify: `docs/phases/phase-03-moodle-integration/README.md`
- Modify: `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- Modify: `backend/README.md`
- Modify: `infra/README.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/README.md`
- Modify: `docs/phases/README.md`

## Task 1: Add The Retryable Integration Models

**Files:**
- Modify: `backend/apps/integration/models.py`
- Create: integration migration

- [ ] Extend `IntegrationOutboxEvent` with retry metadata:
  - `attempts`
  - `last_error`
  - `last_attempt_at`
  - `processed_at`

- [ ] Add `MoodleUserMap` with:
  - `user`
  - `moodle_user_id`
  - `moodle_username`
  - `last_synced_at`

- [ ] Add `MoodleCourseMap` with:
  - `section`
  - `moodle_course_id`
  - `moodle_shortname`
  - `moodle_category_id`
  - `last_synced_at`
  - nullable grade-target fields:
    - `grade_component`
    - `grade_activity_id`
    - `grade_item_number`
    - `grade_item_label`

- [ ] Run:

```bash
cd backend
python manage.py makemigrations integration
python manage.py makemigrations --check --dry-run
```

Expected:

- a new integration migration is created
- the follow-up drift check passes cleanly

## Task 2: Write The Moodle Sync Service And Processor

**Files:**
- Create: `backend/apps/integration/services.py`
- Modify: `backend/sis_backend/settings.py`

- [ ] Add settings/env support for:
  - `MOODLE_DEFAULT_CATEGORY_ID`
  - `MOODLE_STUDENT_ROLE_ID`
  - `MOODLE_EDITING_TEACHER_ROLE_ID`
  - `MOODLE_INSTITUTION`
  - optional `MOODLE_GRADE_SOURCE`

- [ ] Implement safe service primitives:
  - endpoint construction
  - standard REST payload wrapper
  - HTTP/JSON/Moodle-exception handling
  - no token leakage in errors or logs

- [ ] Implement service methods for:
  - `sync_user(user, action="UPSERT" | "SUSPEND")`
  - `sync_section(section)`
  - `sync_enrollment(enrollment, action="ENROLL" | "DROP")`
  - `sync_grade_record(grade_record)`

- [ ] Implement mapping helpers:
  - `ensure_user_mapping`
  - duplicate/existing-user fallback through `core_user_get_users`
  - `ensure_course_mapping`

- [ ] Implement grade sync behavior:
  - call `gradereport_user_get_grade_items`
  - require explicit grade-target metadata before `core_grades_update_grades`
  - fail clearly when the target is not configured

- [ ] Implement outbox processor behavior:
  - increment attempts
  - set `last_attempt_at`
  - mark `PROCESSED` and `processed_at` on success
  - mark `FAILED` and store a safe `last_error` on failure

## Task 3: Wire SIS Mutations Into The Outbox

**Files:**
- Modify: `backend/apps/academics/services.py`
- Modify: `backend/apps/academics/api/serializers.py`
- Modify: `backend/apps/accounts/api/serializers.py`
- Modify: `backend/apps/accounts/api/views.py`

- [ ] Refactor outbox creation into a reusable helper that can optionally schedule best-effort post-commit processing when Moodle config is present

- [ ] Extend user flows:
  - user create → queue user upsert sync
  - relevant user update → queue user upsert or suspend sync
  - user deactivate → queue user suspend sync

- [ ] Extend section flows:
  - section create → queue course sync
  - section update → queue course sync

- [ ] Keep and upgrade existing event flows:
  - enrollment create/drop keep emitting `ENROLLMENT_SYNC_REQUESTED`
  - official grade keep emitting `GRADE_SYNC_REQUESTED`
  - add enough payload identifiers for reliable processing

- [ ] Ensure SIS mutations do not fail if the Moodle sync attempt fails

## Task 4: Add Demonstration And Retry Commands

**Files:**
- Create: `backend/apps/integration/management/commands/process_moodle_sync.py`

- [ ] Implement command options:
  - default pending-only processing
  - include failed events for retry
  - optional `--event-id`
  - optional `--limit`

- [ ] Print a concise operator summary:
  - processed count
  - failed count
  - skipped count if any

- [ ] Keep command behavior safe when config is missing:
  - fail clearly
  - never print the token

## Task 5: Add Mocked Service And Command Tests

**Files:**
- Create: `backend/apps/integration/tests/test_moodle_sync_service.py`
- Create: `backend/apps/integration/tests/test_process_moodle_sync_command.py`
- Possibly modify: existing tests if helper coverage is needed

- [ ] Cover successful user provisioning
- [ ] Cover already-mapped user behavior
- [ ] Cover duplicate/existing Moodle user fallback via `core_user_get_users`
- [ ] Cover Moodle exception handling
- [ ] Cover course shell provisioning
- [ ] Cover enrollment sync
- [ ] Cover grade pass-back baseline
- [ ] Cover missing grade-target configuration failure
- [ ] Cover retry metadata updates in the outbox
- [ ] Cover command-driven retry processing
- [ ] Cover token-safe errors and log output

## Task 6: Update The Phase 3 Runbook And Repo Docs

**Files:**
- Modify: `docs/phases/phase-03-moodle-integration/README.md`
- Modify: `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- Modify: `backend/README.md`
- Modify: `infra/README.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/README.md`
- Modify: `docs/phases/README.md`

- [ ] Update Phase 3 README with:
  - Step 3.2 status
  - new service/command overview
  - least-privilege Moodle function list
  - added required capabilities for Step 3.2
  - role/category/course configuration notes
  - grade pass-back limitation notes

- [ ] Update backend README with:
  - new env variables
  - `process_moodle_sync`
  - mocked test entry points

- [ ] Update infra README only where Step 3.2 changes the Moodle setup/runbook

- [ ] Update root README and changelog to move the active next step forward and record Step 3.2 verification

## Task 7: Verify End To End

- [ ] Run backend system checks:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
```

- [ ] Run targeted sync tests:

```bash
cd backend
pytest -q apps/integration/tests/test_moodle_sync_service.py apps/integration/tests/test_process_moodle_sync_command.py apps/integration/tests/test_verify_moodle_rest_command.py
```

- [ ] Run broader backend verification if practical:

```bash
cd backend
pytest -q --cov=apps --cov-report=term-missing
ruff check .
```

- [ ] Run command smoke tests that do not require live Moodle, for example:

```bash
cd backend
python manage.py process_moodle_sync --help
```

- [ ] Optional live verification only if local token/config is available:
  - Step 3.1 Moodle overlay
  - create or update a SIS user/section/enrollment/official grade
  - run `python manage.py process_moodle_sync`

## Task 8: Finish The Branch Cleanly

- [ ] Review `git diff --check`
- [ ] Review `git status --short`
- [ ] Commit with a Phase 3 Step 3.2 message
- [ ] Merge into `main`
- [ ] Push `main` and the completed history
- [ ] Remove the Step 3.2 worktree and feature branch after merge
