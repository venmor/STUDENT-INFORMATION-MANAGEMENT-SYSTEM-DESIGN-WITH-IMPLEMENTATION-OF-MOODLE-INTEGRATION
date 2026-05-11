# Phase 3 Step 3.4 Integration Verification And Analytics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Step 3.4 Moodle integration-verification gate with a formal test matrix, mocked verification coverage, and a Moodle engagement analytics ingestion foundation.

**Architecture:** Keep Moodle integration in `apps.integration`. Add engagement run/snapshot models, a Moodle engagement service using `core_enrol_get_enrolled_users`, management commands for ingestion and readiness reporting, and small LTI advising context/frontend enhancements. Live Moodle remains optional; automated tests mock Moodle REST.

**Tech Stack:** Django 5, Django management commands, MySQL migrations, pytest, React 18, TypeScript, Vitest, Markdown runbooks.

**Execution status:** Implemented in the Phase 3 Step 3.4 slice. The checklist below records the original execution plan used for the work.

---

## File Map

- Modify: `backend/apps/integration/models.py`
- Modify: `backend/apps/integration/services.py`
- Create: `backend/apps/integration/management/commands/ingest_moodle_engagement.py`
- Create: `backend/apps/integration/management/commands/verify_phase_3_integrations.py`
- Create: `backend/apps/integration/tests/test_moodle_engagement_service.py`
- Create: `backend/apps/integration/tests/test_ingest_moodle_engagement_command.py`
- Create: `backend/apps/integration/tests/test_verify_phase_3_integrations_command.py`
- Modify: `backend/apps/integration/tests/test_lti_tool_provider.py`
- Create: `backend/apps/integration/migrations/0004_moodle_engagement.py`
- Modify: `frontend/src/types/lti.ts`
- Modify: `frontend/src/pages/lti/AdvisingTool.tsx`
- Create: `frontend/tests/unit/lti-advising-tool.test.tsx`
- Create: `docs/phases/phase-03-moodle-integration/STEP_3_4_TEST_MATRIX.md`
- Create: `docs/superpowers/specs/2026-04-30-phase-03-step-3-4-integration-verification-analytics-design.md`
- Create: `docs/superpowers/plans/2026-04-30-phase-03-step-3-4-integration-verification-analytics.md`
- Modify: `docs/phases/phase-03-moodle-integration/README.md`
- Modify: `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- Modify: `docs/project/modern-sis-setup-guide.md`
- Modify: `docs/project/SRS_Modern_SIS.md`
- Modify: `backend/README.md`
- Modify: `frontend/README.md`
- Modify: `infra/README.md`
- Modify: `infra/moodle.env.example`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/README.md`
- Modify: `docs/phases/README.md`

## Task 1: Add Failing Analytics Service Tests

- [ ] Create `backend/apps/integration/tests/test_moodle_engagement_service.py`.
- [ ] Add helper functions for Moodle settings, response mocks, mapped SIS user/student, and mapped course section.
- [ ] Add tests for successful engagement ingestion, missing config, HTTP failure, Moodle exception payload, invalid JSON, unmapped Moodle user skipping, and token-safe errors.
- [ ] Run:

```bash
cd backend
pytest -q apps/integration/tests/test_moodle_engagement_service.py
```

- [ ] Expected before implementation: tests fail because engagement models and service do not exist.

## Task 2: Add Failing Management Command Tests

- [ ] Create `backend/apps/integration/tests/test_ingest_moodle_engagement_command.py`.
- [ ] Test `--dry-run` creates an ingestion run but no snapshots.
- [ ] Test normal command creates snapshots and prints courses/users/snapshots/failures.
- [ ] Test command errors do not leak `MOODLE_WS_TOKEN`.
- [ ] Create `backend/apps/integration/tests/test_verify_phase_3_integrations_command.py`.
- [ ] Test readiness output reports Moodle config, LTI config, mapping counts, outbox counts, and latest ingestion run.
- [ ] Run:

```bash
cd backend
pytest -q apps/integration/tests/test_ingest_moodle_engagement_command.py apps/integration/tests/test_verify_phase_3_integrations_command.py
```

- [ ] Expected before implementation: tests fail because commands and models do not exist.

## Task 3: Add Failing LTI Engagement Context Test

- [ ] Modify `backend/apps/integration/tests/test_lti_tool_provider.py`.
- [ ] Extend the mapped advising-context test to create a latest `MoodleEngagementSnapshot`.
- [ ] Assert the roster entry includes engagement fields from that snapshot.
- [ ] Run:

```bash
cd backend
pytest -q apps/integration/tests/test_lti_tool_provider.py::test_context_api_returns_mapped_advising_context_with_roster
```

- [ ] Expected before implementation: test fails because the roster payload has no engagement object.

## Task 4: Implement Backend Models And Migration

- [ ] Add `MoodleEngagementIngestionStatus`, `MoodleEngagementIngestionRun`, and `MoodleEngagementSnapshot` to `backend/apps/integration/models.py`.
- [ ] Include minimal privacy-aware fields only: mappings, Moodle IDs, access timestamps, nullable assignment/quiz/forum metrics, minimal raw summary, timestamps, and run summary counters.
- [ ] Create `backend/apps/integration/migrations/0004_moodle_engagement.py`.
- [ ] Run targeted model-related tests again and keep failures focused on missing service behavior.

## Task 5: Implement Moodle Engagement Service

- [ ] Add `MoodleEngagementError`, result helpers, and `MoodleEngagementService` to `backend/apps/integration/services.py`.
- [ ] Implement safe Moodle REST request handling for `core_enrol_get_enrolled_users`.
- [ ] Implement `section_id`, `user_id`, `limit`, `since`, and `dry_run` handling.
- [ ] Count courses inspected, users inspected, snapshots created/updated, skipped unmapped users, and failures.
- [ ] Ensure all errors are safe and do not contain the Moodle token.
- [ ] Re-run `test_moodle_engagement_service.py` until green.

## Task 6: Implement Management Commands

- [ ] Add `ingest_moodle_engagement`.
- [ ] Validate config, parse `--since`, call the service, and print a clear summary.
- [ ] Add `verify_phase_3_integrations`.
- [ ] Keep readiness verification non-live by default.
- [ ] Re-run command tests until green.

## Task 7: Add Engagement To LTI Context

- [ ] Update `backend/apps/integration/lti.py` so advising roster entries include latest engagement snapshot for the mapped section/user.
- [ ] Keep registration tool payload unchanged.
- [ ] Re-run the targeted LTI test until green.

## Task 8: Add Small Frontend Advising Selection Flow

- [ ] Update `frontend/src/types/lti.ts` with optional roster engagement fields.
- [ ] Update `frontend/src/pages/lti/AdvisingTool.tsx` to support selecting a roster student and showing a read-only student/engagement panel.
- [ ] Create `frontend/tests/unit/lti-advising-tool.test.tsx` with mocked fetch data.
- [ ] Run:

```bash
cd frontend
npm run typecheck
npm run lint
npm test -- lti-advising-tool
```

## Task 9: Add Step 3.4 Test Matrix And Docs

- [ ] Create `docs/phases/phase-03-moodle-integration/STEP_3_4_TEST_MATRIX.md`.
- [ ] Cover Lane A, Lane B, ETL, failure/retry, invalid LTI, unmapped contexts, secret-safety, no-live-Moodle automation, and optional live Moodle verification.
- [ ] Update Phase 3 README and changelog.
- [ ] Update backend, frontend, infra, root README, root changelog, docs indexes, setup guide, and SRS.
- [ ] Update `infra/moodle.env.example` comments and `infra/README.md` with `core_enrol_get_enrolled_users` guidance.

## Task 10: Full Verification

- [ ] Run backend checks:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/integration/tests/test_verify_moodle_rest_command.py
pytest -q apps/integration/tests/test_moodle_sync_service.py
pytest -q apps/integration/tests/test_process_moodle_sync_command.py
pytest -q apps/integration/tests/test_lti_tool_provider.py
pytest -q apps/integration/tests/
ruff check .
```

- [ ] Run frontend checks because LTI frontend changed:

```bash
cd frontend
npm run typecheck
npm run lint
npm test
npm run build
```

- [ ] Run docs/git checks:

```bash
git diff --check
git status -sb
```

## Task 11: Finish And Publish

- [ ] Confirm no Phase 3.5 dashboards, AI, at-risk scoring, wellbeing support, secrets, private keys, or `.env.local` files are staged.
- [ ] Commit with:

```bash
git add backend frontend docs README.md CHANGELOG.md infra
git commit -m "feat: implement phase 3 step 3.4 analytics ingestion"
```

- [ ] Push feature branch.
- [ ] Merge into local `main`.
- [ ] Push `main` to GitHub.
- [ ] Verify local `main` and `origin/main` point at the same commit.
