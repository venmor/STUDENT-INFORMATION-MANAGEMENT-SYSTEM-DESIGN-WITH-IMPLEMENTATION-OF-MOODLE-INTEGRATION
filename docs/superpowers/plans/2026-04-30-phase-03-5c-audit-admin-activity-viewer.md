# Phase 3.5C Audit/Admin Activity Viewer Implementation Plan

> **Execution note:** The user requested end-to-end execution without repeated approval checkpoints. This plan records the implementation checklist used for the slice.

**Goal:** Add a read-only admin activity viewer backed by real database audit records, wire clean audit hooks, and document exact commands for running/testing the UI with the backend database.

**Architecture:** Add a small `apps.audit` Django app with an append-only audit model, sanitizer, service helpers, admin-only read APIs, and optional local demo data command. Reuse the existing `/admin/audit-log` frontend route and existing design system. Wire only clean hooks in existing integration, notification, accounts, academics, and LTI code paths.

**Tech Stack:** Django 5, Django REST Framework, pytest, React 18, TypeScript, TanStack Query, Axios, Heroicons, Tailwind, Vitest.

---

## File Map

- Create: `backend/apps/audit/__init__.py`
- Create: `backend/apps/audit/apps.py`
- Create: `backend/apps/audit/models.py`
- Create: `backend/apps/audit/services.py`
- Create: `backend/apps/audit/api/__init__.py`
- Create: `backend/apps/audit/api/serializers.py`
- Create: `backend/apps/audit/api/views.py`
- Create: `backend/apps/audit/api/urls.py`
- Create: `backend/apps/audit/management/commands/seed_audit_activity_demo.py`
- Create: `backend/apps/audit/migrations/0001_initial.py`
- Create: `backend/apps/audit/tests/test_audit_activity_api.py`
- Modify: `backend/sis_backend/settings.py`
- Modify: `backend/sis_backend/urls.py`
- Modify: `backend/apps/accounts/access.py`
- Modify: `backend/apps/accounts/api/views.py`
- Modify: `backend/apps/academics/services.py`
- Modify: `backend/apps/integration/services.py`
- Modify: `backend/apps/integration/api/views.py`
- Modify: `backend/apps/integration/lti.py`
- Modify: `backend/apps/notifications/api/views.py`
- Create: `frontend/src/types/audit.ts`
- Create: `frontend/src/api/audit.ts`
- Create: `frontend/src/hooks/useAuditActivity.ts`
- Modify: `frontend/src/pages/admin/AuditLog.tsx`
- Modify: `frontend/src/components/layout/AppShell.tsx`
- Create/modify frontend unit tests for the audit page/route
- Create: `docs/superpowers/specs/2026-04-30-phase-03-5c-audit-admin-activity-viewer.md`
- Create: `docs/superpowers/plans/2026-04-30-phase-03-5c-audit-admin-activity-viewer.md`
- Modify: phase, project, backend, frontend, root docs and changelogs

## Task 1: Add Failing Backend Tests

- [ ] Add audit API tests for admin list, detail, summary, filters, date range, and search.
- [ ] Add authorization tests for non-admin and unauthenticated users.
- [ ] Add sanitizer tests for token/password/private key/JWT/wstoken/access/refresh redaction.
- [ ] Add hook tests for Moodle sync failure and notification read.
- [ ] Add API secret-safety assertions.
- [ ] Run the new backend tests and confirm failures are due to missing implementation.

## Task 2: Implement Backend Audit Foundation

- [ ] Add `apps.audit` to `INSTALLED_APPS`.
- [ ] Implement `AuditEvent`, `AuditCategory`, and `AuditSeverity`.
- [ ] Generate the initial migration.
- [ ] Implement sanitizer and `record_audit_event`.
- [ ] Implement serializers and admin-only API views.
- [ ] Include audit URLs under `/api/v1/`.
- [ ] Register audit route names in the access-policy map for admins.
- [ ] Add optional `seed_audit_activity_demo` command.
- [ ] Re-run backend audit tests until green.

## Task 3: Wire Clean Audit Hooks

- [ ] Moodle sync failure/processed events in `process_outbox_event`.
- [ ] Moodle sync retry event in the retry API view.
- [ ] Notification read and read-all events in notification API views.
- [ ] LTI launch-created event after safe session persistence.
- [ ] User create/update/deactivate/password-reset-required events in admin user views.
- [ ] Enrollment created/dropped events in academic services.
- [ ] Grade officialised event in academic services.
- [ ] Keep all audit hook calls non-blocking.
- [ ] Re-run integration and notification tests.

## Task 4: Add Failing Frontend Tests

- [ ] Add Audit Log page tests with mocked audit hooks.
- [ ] Assert summary cards, filters, event rows, details panel, empty state, error state, and no emoji text.
- [ ] Add/extend route/sidebar test to confirm `/admin/audit-log` remains the admin Audit Log route.
- [ ] Run relevant frontend tests and confirm failures are due to missing implementation.

## Task 5: Implement Frontend Audit Viewer

- [ ] Add audit TypeScript types.
- [ ] Add Axios API helpers.
- [ ] Add TanStack Query hooks.
- [ ] Update `/admin/audit-log` page to the real Step 3.5C viewer.
- [ ] Update AppShell title/subtitle for `/admin/audit-log`.
- [ ] Implement summary cards, filters, table, details panel, states, and scope note.
- [ ] Re-run frontend tests until green.

## Task 6: Documentation

- [ ] Update Phase 3 README and changelog.
- [ ] Update setup guide and SRS if status clarity is needed.
- [ ] Update backend and frontend READMEs.
- [ ] Update root README and changelog.
- [ ] Add `Run and Test Step 3.5C UI With Backend Database` sections with exact Docker, migration, demo seed, URL, local frontend, test, and teardown commands.
- [ ] Document:
  - Step 3.5C is implemented.
  - It is admin-only and read-only.
  - It uses real backend API/database data.
  - Optional demo data command exists.
  - Step 3.5D remains next.
  - Step 3.5D-3.5G remain future.
  - No AI audit review beyond placeholder category was implemented.

## Task 7: Verification

- [ ] Run backend:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/audit/tests/
pytest -q apps/integration/tests/
pytest -q apps/notifications/tests/
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

## Task 8: Finish And Publish

- [ ] Confirm no `.env.local`, `local-secrets/`, Moodle tokens, LTI private keys, or generated runtime secrets are staged.
- [ ] Commit with `feat: add phase 3.5C audit activity viewer`.
- [ ] Push `feature/phase-03-5c-audit-admin-activity-viewer`.
- [ ] Fast-forward merge to local `main` if possible.
- [ ] Push `main`.
- [ ] Verify local `main` and `origin/main`.
