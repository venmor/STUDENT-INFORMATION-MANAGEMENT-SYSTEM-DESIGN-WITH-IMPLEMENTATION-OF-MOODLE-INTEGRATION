# Phase 3.5E Admin Reporting Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build an admin-only institutional reporting dashboard over existing SIS, Moodle, calendar, notification, and audit data.

**Architecture:** Add a new backend `apps.reporting` package with service-layer aggregations and thin API views. Add a React admin page using existing query hooks, shared UI primitives, Tailwind tokens, and Heroicons, with no heavy chart dependency.

**Tech Stack:** Django 5, Django REST Framework, MySQL-compatible ORM queries, React 18, TypeScript, TanStack Query, Vite, Tailwind CSS, Vitest.

---

## File Map

- Create `backend/apps/reporting/apps.py`: Django app config.
- Create `backend/apps/reporting/services.py`: report filters, aggregations, capacity status, safe report payload builders.
- Create `backend/apps/reporting/api/urls.py`: reporting route registration.
- Create `backend/apps/reporting/api/views.py`: admin report API views and capacity CSV response.
- Create `backend/apps/reporting/management/commands/seed_reporting_demo.py`: optional local/demo data command.
- Create `backend/apps/reporting/tests/test_admin_reporting_api.py`: backend endpoint, aggregation, permissions, CSV, and secret-safety tests.
- Modify `backend/sis_backend/settings.py`: install `apps.reporting`.
- Modify `backend/sis_backend/urls.py`: include reporting URLs.
- Modify `backend/apps/accounts/access.py`: register admin-only route policies for reporting endpoints.
- Create `frontend/src/types/reports.ts`: TypeScript report contracts.
- Create `frontend/src/api/reports.ts`: API client functions.
- Create `frontend/src/hooks/useAdminReports.ts`: TanStack Query hooks.
- Create `frontend/src/pages/admin/Reports.tsx`: reporting dashboard UI.
- Modify `frontend/src/router.tsx`: admin-only route.
- Modify `frontend/src/components/layout/Sidebar.tsx`: Reports navigation item.
- Modify `frontend/src/components/layout/AppShell.tsx`: reports page heading.
- Create `frontend/tests/unit/admin-reports-route.test.tsx`: route/sidebar/access tests.
- Create `frontend/tests/unit/admin-reports-page.test.tsx`: page rendering tests.
- Update the normal docs and changelogs listed in the spec.

## Tasks

### Task 1: Backend Tests First

- [x] Create `backend/apps/reporting/tests/test_admin_reporting_api.py`.
- [x] Seed real users, students, sections, enrollments, grades, Moodle outbox events, Moodle maps, engagement runs, calendar events, notifications, and audit events in tests.
- [x] Add tests for admin access and `401`/`403` denial across all report endpoints.
- [x] Add tests for summary counts, capacity calculations, grade state mapping, Moodle report safety, calendar deadlines, activity counts, and safe CSV export.
- [x] Run `pytest -q apps/reporting/tests/` and confirm it fails because `apps.reporting` does not exist yet.

### Task 2: Backend Reporting App

- [x] Create the `apps.reporting` package and service/API files.
- [x] Implement filter parsing for `academic_year`, `semester`, `programme`, `course`, and `status`.
- [x] Implement `get_admin_reporting_summary()`.
- [x] Implement `get_enrollment_report()`.
- [x] Implement `get_capacity_report()` and capacity status helpers.
- [x] Implement `get_grade_report()`.
- [x] Implement `get_moodle_sync_report()`.
- [x] Implement `get_calendar_deadline_report()`.
- [x] Implement `get_operational_activity_report()`.
- [x] Implement safe capacity CSV export and `ADMIN_REPORT_EXPORTED` audit event.
- [x] Register routes in `sis_backend.urls` and admin-only access policies in `apps.accounts.access`.
- [x] Run `pytest -q apps/reporting/tests/` until the reporting tests pass.

### Task 3: Frontend Tests First

- [x] Create `frontend/tests/unit/admin-reports-route.test.tsx`.
- [x] Create `frontend/tests/unit/admin-reports-page.test.tsx`.
- [x] Mock report hooks and verify route registration, sidebar visibility, non-admin denial, summary cards, health strip, filters, capacity table, grade table, Moodle/Calendar/Audit links, empty state, error state, and no emoji text.
- [x] Run `npm run test -- admin-reports` and confirm it fails because reports modules/page do not exist yet.

### Task 4: Frontend Reporting UI

- [x] Create report types in `frontend/src/types/reports.ts`.
- [x] Create API client functions in `frontend/src/api/reports.ts`.
- [x] Create query hooks in `frontend/src/hooks/useAdminReports.ts`.
- [x] Create `frontend/src/pages/admin/Reports.tsx` using existing `Card`, `Badge`, `Button`, `Input`, `Select`, `Table`, `EmptyState`, and `Alert`.
- [x] Add `/admin/reports` to `frontend/src/router.tsx`.
- [x] Add Reports with `ChartBarIcon` under an admin Insights sidebar group.
- [x] Add AppShell heading for `/admin/reports`.
- [x] Run targeted frontend tests until they pass.

### Task 5: Demo Data Command

- [x] Implement `python manage.py seed_reporting_demo`.
- [x] Reuse `seed_demo_sis`, `seed_academic_calendar_demo`, and `seed_audit_activity_demo` where safe.
- [x] Add safe Moodle outbox, mappings, engagement run/snapshot, and admin notification records if related core records exist.
- [x] Do not create or print secrets.
- [x] Keep the command idempotent enough for repeated local demo runs.

### Task 6: Documentation

- [x] Update Phase 3 README and changelog to mark Step 3.5E implemented.
- [x] Update setup guide Step 3.5E from expected to implemented.
- [x] Update SRS revision/status for Step 3.5E.
- [x] Update root README and CHANGELOG.
- [x] Update backend and frontend READMEs with API/UI/test notes.
- [x] Keep long run-and-test command details out of docs except where existing repo convention already has them; final chat response will include exact commands.

### Task 7: Verification and Git

- [x] Run backend checks:
  - `cd backend`
  - `python manage.py check`
  - `python manage.py makemigrations --check --dry-run`
  - `pytest -q apps/reporting/tests/`
  - `pytest -q apps/calendar/tests/`
  - `pytest -q apps/audit/tests/`
  - `pytest -q apps/notifications/tests/`
  - `pytest -q apps/integration/tests/`
  - `ruff check .`
- [x] Run frontend checks:
  - `cd frontend`
  - `npm run typecheck`
  - `npm run lint`
  - `npm run test`
  - `npm run build`
- [x] Run `git diff --check`.
- [x] Commit with `feat: add phase 3.5E admin reporting dashboard`.
- [x] Merge to local `main`, push to GitHub, and update local `main`.
