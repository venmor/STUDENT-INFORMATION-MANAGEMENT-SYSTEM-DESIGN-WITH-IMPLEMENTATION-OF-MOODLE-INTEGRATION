# Phase 3.5D Academic Calendar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a central, role-aware Academic Calendar and Deadline Rules module for Step 3.5D without implementing Step 3.5E-3.5G.

**Architecture:** Create a focused `apps.calendar` backend app with one canonical event model, service helpers for visibility/sync/audit/optional notifications, DRF APIs under `/api/v1/calendar/`, and a shared React `/calendar` page backed by TanStack Query hooks. Keep generated course-section events separate via `source=COURSE_SECTION` and no hard delete path.

**Tech Stack:** Django 5, Django REST Framework, MySQL, pytest, React 18, TypeScript, Vite, TanStack Query, Tailwind CSS, Heroicons.

---

## File Map

- Create `backend/apps/calendar/`: model, serializers, views, services, URLs, admin registration, tests, migrations, and two management commands.
- Modify `backend/sis_backend/settings.py`, `backend/sis_backend/urls.py`, and `backend/apps/accounts/access.py` to register the app and route policies.
- Modify `backend/apps/audit/models.py` with an `ACADEMIC_CALENDAR` category.
- Create frontend `src/types/calendar.ts`, `src/api/calendar.ts`, `src/hooks/useAcademicCalendar.ts`, and `src/pages/AcademicCalendar.tsx`.
- Modify `frontend/src/router.tsx`, `frontend/src/components/layout/Sidebar.tsx`, and `frontend/src/components/layout/AppShell.tsx`.
- Add frontend unit tests for the calendar page and route/sidebar behavior.
- Update Phase 3.5 docs, project docs, backend/frontend READMEs, root README, and changelogs.

## Task 1: Backend Tests First

- [x] Create `backend/apps/calendar/tests/test_calendar_api.py`.
- [x] Add tests for admin list-all, student/faculty/advisor visibility, admin create/update/cancel, non-admin create rejection, invalid end date rejection, filters, summary counts, audit hooks, and metadata secret safety.
- [ ] Run `pytest -q apps/calendar/tests/test_calendar_api.py` and confirm it fails because `apps.calendar` is not installed and routes do not exist.

## Task 2: Calendar Model And Services

- [ ] Create `backend/apps/calendar/models.py` with `AcademicCalendarEvent` and choice classes.
- [ ] Create `backend/apps/calendar/services.py` for role visibility, urgency calculation, metadata sanitization, audit recording, optional high/critical notification targeting, course-section sync, and demo seed creation.
- [ ] Add migration `0001_initial.py`.
- [ ] Run the calendar tests and confirm model/service-level failures move toward API-specific failures.

## Task 3: Calendar APIs

- [ ] Create serializers in `backend/apps/calendar/api/serializers.py` using camelCase response fields.
- [ ] Create views in `backend/apps/calendar/api/views.py` for list/create, detail/update, cancel, and summary.
- [ ] Create `backend/apps/calendar/api/urls.py` and include it from `backend/sis_backend/urls.py`.
- [ ] Register route policies in `backend/apps/accounts/access.py`.
- [ ] Run `pytest -q apps/calendar/tests/test_calendar_api.py` and fix failures.

## Task 4: Management Commands

- [ ] Add `seed_academic_calendar_demo` using stable metadata and idempotent creation.
- [ ] Add `sync_academic_calendar_from_sections` using `source + related_section + event_type` idempotency.
- [ ] Add tests in `backend/apps/calendar/tests/test_calendar_commands.py`.
- [ ] Run `pytest -q apps/calendar/tests/` and fix failures.

## Task 5: Frontend Tests First

- [ ] Create `frontend/tests/unit/academic-calendar-page.test.tsx` with mocked hooks covering summary cards, month/list views, filters, details, admin controls, create/cancel mutations, empty/error states, and no emoji page text.
- [ ] Create `frontend/tests/unit/academic-calendar-route.test.tsx` covering `/calendar` route access and sidebar links for student, advisor, faculty, and admin.
- [ ] Run targeted Vitest tests and confirm failures because the page, hooks, and route do not exist.

## Task 6: Frontend Calendar Implementation

- [ ] Add calendar types, API functions, and TanStack Query hooks.
- [ ] Implement `AcademicCalendarPage` with summary cards, My Deadlines, month/list views, filters, event details, Current Scope, and admin modal.
- [ ] Add route `/calendar`, AppShell heading, and Sidebar links.
- [ ] Run targeted frontend tests and fix failures.

## Task 7: Documentation

- [ ] Update Phase 3 README/changelog with Step 3.5D complete and Step 3.5E next.
- [ ] Update setup guide and SRS requirement status.
- [ ] Update backend/frontend/root README and root CHANGELOG with concise Step 3.5D notes.
- [ ] Do not add a long UI/database run command section to docs.

## Task 8: Verification And Release

- [ ] Run backend verification: `python manage.py check`, migration check, calendar/audit/notifications/integration pytest targets, and `ruff check .`.
- [ ] Run frontend verification: typecheck, lint, test, build.
- [ ] Run `git diff --check`.
- [ ] Commit as `feat: add phase 3.5D academic calendar`.
- [ ] Merge to `main`, push to GitHub, and update local main.

## Self-Review

- Scope excludes Step 3.5E reporting, Step 3.5F documents, Step 3.5G admissions, AI, at-risk scoring, wellbeing, recurring rules, personal calendar sync, reminders, and timetable conflict detection.
- Backend plan covers model/API/commands/audit/optional notifications.
- Frontend plan covers route/sidebar/page/accessibility/mobile/list fallback/admin-only actions.
- Verification commands match the requested final command set and are not added as a long docs section.
