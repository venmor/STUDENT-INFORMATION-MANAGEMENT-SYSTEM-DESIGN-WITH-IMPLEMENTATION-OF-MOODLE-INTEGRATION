# Phase 3.5B Notification Center Implementation Plan

> **Execution note:** The user requested end-to-end execution without repeated approval checkpoints. This plan records the implementation checklist used for the slice.

**Goal:** Add an authenticated in-app Notification Center for all primary roles, wire clean notification events, and apply the controlled AppShell/sidebar/topbar polish needed for discoverability.

**Architecture:** Add a small `apps.notifications` Django app with model, service helpers, and user-scoped DRF APIs. Wire only existing clean event points in integration, academics, and students. Add frontend API/hooks/types, a `/notifications` page, a topbar bell, and constrained shell polish using the existing design system.

**Tech Stack:** Django 5, Django REST Framework, pytest, React 18, TypeScript, TanStack Query, Axios, Heroicons, Tailwind, Vitest.

---

## File Map

- Create: `backend/apps/notifications/__init__.py`
- Create: `backend/apps/notifications/apps.py`
- Create: `backend/apps/notifications/models.py`
- Create: `backend/apps/notifications/services.py`
- Create: `backend/apps/notifications/api/__init__.py`
- Create: `backend/apps/notifications/api/serializers.py`
- Create: `backend/apps/notifications/api/views.py`
- Create: `backend/apps/notifications/api/urls.py`
- Create: `backend/apps/notifications/migrations/0001_initial.py`
- Create: `backend/apps/notifications/tests/test_notifications_api.py`
- Modify: `backend/sis_backend/settings.py`
- Modify: `backend/sis_backend/urls.py`
- Modify: `backend/apps/accounts/access.py`
- Modify: `backend/apps/integration/services.py`
- Modify: `backend/apps/academics/services.py`
- Modify: `backend/apps/students/api/views.py`
- Create: `frontend/src/types/notifications.ts`
- Create: `frontend/src/api/notifications.ts`
- Create: `frontend/src/hooks/useNotifications.ts`
- Create: `frontend/src/pages/Notifications.tsx`
- Modify: `frontend/src/router.tsx`
- Modify: `frontend/src/components/layout/AppShell.tsx`
- Modify: `frontend/src/components/layout/Sidebar.tsx`
- Modify: `frontend/src/components/layout/Topbar.tsx`
- Modify: `frontend/src/components/layout/MobileNav.tsx` if required by sidebar changes
- Create/modify frontend unit tests for notifications and layout polish
- Create: `docs/superpowers/specs/2026-04-30-phase-03-5b-notification-center.md`
- Create: `docs/superpowers/plans/2026-04-30-phase-03-5b-notification-center.md`
- Modify: phase, project, backend, frontend, root docs and changelogs

## Task 1: Add Failing Backend Tests

- [ ] Add tests for notification service creation and dedupe behavior.
- [ ] Add API tests for list, summary, filters, mark-one-read, and mark-all-read.
- [ ] Add authorization tests for unauthenticated users and cross-user access.
- [ ] Add event-hook tests for Moodle sync failure, enrollment confirmed, grade released, and approved advising note.
- [ ] Add secret-safety assertions for tokens, private keys, and raw JWT-like metadata.
- [ ] Run the new backend tests and confirm failures are due to missing implementation.

## Task 2: Implement Backend Notification Foundation

- [ ] Add `apps.notifications` to `INSTALLED_APPS`.
- [ ] Implement `Notification`, category choices, and severity choices.
- [ ] Generate the initial migration.
- [ ] Implement service helpers:
  - `create_notification`
  - `notify_admins`
  - `notify_moodle_sync_failure`
  - safe metadata/message sanitization
- [ ] Implement serializers and API views.
- [ ] Include notification URLs under `/api/v1/`.
- [ ] Register notification routes in the access-policy map for all primary roles.
- [ ] Wire existing clean hooks:
  - `process_outbox_event` failure
  - `create_enrollment` enrolled branch
  - `officialise_grade`
  - `AdvisingNoteApproveView`
- [ ] Re-run backend notification tests until green.

## Task 3: Add Failing Frontend Tests

- [ ] Add Notification Center page tests with mocked notification hooks.
- [ ] Add route test for `/notifications`.
- [ ] Add topbar bell unread count test.
- [ ] Add sidebar grouping, route order, active marker, and sign-out placement tests.
- [ ] Add practical no-emoji assertions for notification/layout text.
- [ ] Run the relevant frontend tests and confirm failures are due to missing implementation.

## Task 4: Implement Frontend Notification Center

- [ ] Add notification TypeScript types.
- [ ] Add Axios API helpers.
- [ ] Add TanStack Query hooks and read mutations.
- [ ] Add `/notifications` route for all authenticated roles.
- [ ] Add AppShell title and subtitle.
- [ ] Implement the Notification Center page:
  - summary cards
  - status/category/severity filters
  - mark-all-read
  - list items with action links and mark-read
  - loading, error, and empty states
- [ ] Re-run frontend notification tests until green.

## Task 5: Apply Controlled Layout Polish

- [ ] Refactor sidebar nav into role-specific groups.
- [ ] Preserve admin order: Courses, Moodle Sync, Audit Log.
- [ ] Improve active, hover, and focus-visible states.
- [ ] Move sign out into the sidebar bottom.
- [ ] Add compact sidebar account card with password link.
- [ ] Add topbar notification bell and unread badge.
- [ ] Keep account summary chip in the topbar.
- [ ] Remove sign out from topbar.
- [ ] Keep mobile nav functional with grouped sidebar and sign out.
- [ ] Re-run layout tests until green.

## Task 6: Documentation

- [ ] Update Phase 3 README and changelog.
- [ ] Update setup guide and SRS if status clarity is needed.
- [ ] Update backend and frontend READMEs.
- [ ] Update root README and changelog.
- [ ] Document:
  - Step 3.5B is implemented.
  - Notifications are in-app only.
  - No email/SMS/push delivery yet.
  - Moodle sync failure notifications are wired.
  - Grade, enrollment, and advising-note notifications are wired through clean existing hooks.
  - AppShell/sidebar/topbar received controlled UX polish.
  - Step 3.5C remains next.
  - Step 3.5D-3.5G remain future.
  - No AI, at-risk, or wellbeing was implemented.

## Task 7: Verification

- [ ] Run backend:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/notifications/tests/
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

## Task 8: Finish And Publish

- [ ] Confirm no `.env.local`, `local-secrets/`, Moodle tokens, LTI private keys, or generated runtime secrets are staged.
- [ ] Commit with `feat: add phase 3.5B notification center`.
- [ ] Push `feature/phase-03-5b-notification-center`.
- [ ] Fast-forward merge to local `main` if possible.
- [ ] Push `main`.
- [ ] Verify local `main` and `origin/main`.
