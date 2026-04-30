# Phase 3.5A Moodle Sync Monitoring Dashboard Implementation Plan

> **Execution note:** The user requested end-to-end execution without repeated approval checkpoints. This plan records the implementation checklist used for the slice.

**Goal:** Add an admin-only Moodle Sync Monitoring Dashboard over existing Step 3.2 outbox/mappings and Step 3.4 engagement ingestion state, with safe retry for failed/pending outbox events.

**Architecture:** Reuse `apps.integration` models and services. Add a small admin-only DRF API module, policy registrations, frontend API/hooks/types, and one admin page in the existing shell. Do not create new sync behavior except routing retry requests to `process_outbox_event`.

**Tech Stack:** Django 5, Django REST Framework, pytest, React 18, TypeScript, TanStack Query, Axios, Heroicons, Tailwind, Vitest.

---

## File Map

- Create: `backend/apps/integration/api/__init__.py`
- Create: `backend/apps/integration/api/serializers.py`
- Create: `backend/apps/integration/api/views.py`
- Create: `backend/apps/integration/api/urls.py`
- Modify: `backend/sis_backend/urls.py`
- Modify: `backend/apps/accounts/access.py`
- Create: `backend/apps/integration/tests/test_moodle_sync_monitoring_api.py`
- Create: `frontend/src/types/moodleSync.ts`
- Create: `frontend/src/api/moodleSync.ts`
- Create: `frontend/src/hooks/useMoodleSync.ts`
- Create: `frontend/src/pages/admin/MoodleSync.tsx`
- Modify: `frontend/src/router.tsx`
- Modify: `frontend/src/components/layout/Sidebar.tsx`
- Modify: `frontend/src/components/layout/AppShell.tsx`
- Modify: `frontend/src/pages/admin/Dashboard.tsx`
- Create: `frontend/tests/unit/moodle-sync-page.test.tsx`
- Create: `frontend/tests/unit/admin-moodle-sync-route.test.tsx`
- Create: `docs/superpowers/specs/2026-04-30-phase-03-5a-moodle-sync-monitoring-dashboard.md`
- Create: `docs/superpowers/plans/2026-04-30-phase-03-5a-moodle-sync-monitoring-dashboard.md`
- Modify: Phase, project, backend, frontend, root docs and changelogs

## Task 1: Add Failing Backend API Tests

- [ ] Create `test_moodle_sync_monitoring_api.py`.
- [ ] Test admin access and non-admin denial.
- [ ] Test summary counts and secret safety.
- [ ] Test outbox filters and safe payload summaries.
- [ ] Test retry success, processed rejection, and safe retry failure.
- [ ] Test user maps, course maps, engagement runs, and engagement snapshots.
- [ ] Run the new test file and confirm failures are due to missing routes/API.

## Task 2: Implement Backend API

- [ ] Add serializers with camelCase response fields matching the dashboard contract.
- [ ] Add views for summary, outbox list, retry, maps, runs, and snapshots.
- [ ] Add URL routes under `/api/v1/integration/moodle/...`.
- [ ] Register every route in the access-policy map as admin-only.
- [ ] Re-run backend API tests until green.

## Task 3: Add Failing Frontend Tests

- [ ] Add route/sidebar tests for `/admin/moodle-sync`.
- [ ] Add page rendering tests with mocked hooks.
- [ ] Cover summary cards, outbox table, retry action, mappings, engagement, empty/error states, and practical no-emoji labels.
- [ ] Run the new frontend tests and confirm failures are due to missing page/hooks/routes.

## Task 4: Implement Frontend API, Hooks, And Page

- [ ] Add Moodle sync TypeScript types.
- [ ] Add Axios API helpers.
- [ ] Add TanStack Query hooks and retry mutation.
- [ ] Add `AdminMoodleSyncPage`.
- [ ] Add route and admin sidebar item.
- [ ] Add AppShell title/subtitle.
- [ ] Update the admin dashboard text so Moodle sync monitoring is no longer described as deferred.
- [ ] Re-run frontend tests until green.

## Task 5: Documentation

- [ ] Update Phase 3 README and changelog.
- [ ] Update setup guide and SRS if status clarity is needed.
- [ ] Update backend and frontend READMEs.
- [ ] Update root README and changelog.
- [ ] Document admin-only scope, retry behavior, secret safety, no live Moodle requirement, and Step 3.5B as next.

## Task 6: Verification

- [ ] Run backend:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/integration/tests/
ruff check .
```

- [ ] Run frontend:

```bash
cd frontend
npm run typecheck
npm run lint
npm run test
npm run build
```

- [ ] Run docs/git:

```bash
git diff --check
git status -sb
```

## Task 7: Finish And Publish

- [ ] Confirm no `.env.local`, local secrets, Moodle tokens, LTI private keys, or generated runtime secrets are staged.
- [ ] Commit with `feat: add phase 3.5A Moodle sync monitoring dashboard`.
- [ ] Push `feature/phase-03-5a-moodle-sync-monitoring`.
- [ ] Fast-forward merge to local `main` if possible.
- [ ] Push `main`.
- [ ] Verify local `main` and `origin/main`.
