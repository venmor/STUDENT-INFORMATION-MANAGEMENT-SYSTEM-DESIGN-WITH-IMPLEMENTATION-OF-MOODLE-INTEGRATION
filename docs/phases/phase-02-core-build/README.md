# Phase 2 Core Build

## Objective

Phase 2 builds the first working application baseline for Modern SIS in isolation from Moodle so core data, auth, RBAC, and UI flows are stable before external integration begins.

## Scope

- bootstrap the backend, frontend, and infra directories
- implement JWT authentication, RBAC, and capability-aware access control
- build the core SIS data model and representative API surface
- scaffold the role-aware frontend and protected routing baseline
- add local Docker-based infrastructure and CI foundations

## Status

- Status: In progress
- Source guide: `docs/project/modern-sis-setup-guide.md` Phase 2
- Active implementation branch: `feat/phase-02-step-2-3-core-modules`
- Active implementation worktree: `.worktrees/phase-02-step-2-3-core-modules/`
- Execution plan: `docs/superpowers/plans/2026-04-12-phase-02-core-build-implementation.md`

## Current Step

- In scope: Step 2.3, password-policy carry-forward, user administration, student records, course catalog, enrollment, and grade management
- Out of scope: Step 2.4 frontend app scaffold and Step 2.5 CI plus staging stack

## Implementation Progress

- Step 2.1 complete: Django backend scaffold, environment-driven settings, initial MySQL migration baseline, and reserved `frontend/` plus `infra/` directories
- Step 2.2 complete: custom user model, seeded role catalog, `wellbeing_coordinator` capability flags, JWT login/refresh endpoints, bcrypt-backed password storage, central API route-policy enforcement, and verified role/capability probe endpoints
- Step 2.3 complete on the active branch: full password complexity enforcement per `FR-USR-007`, user administration and access logging, student profiles and advising records, dedicated student-record deactivation, field-level student audit logging, financial flags, course and section management, CSV bulk enrollment, grade workflows, GPA and academic standing recalculation, transcript PDF generation, and Moodle-facing outbox events for later integration work
- Step 2.3 alignment pass complete: the OpenAPI contract now reflects only the implemented backend surface, the ERD now matches the live schema types and timetable normalization, and the stale pre-middleware RBAC helper was removed

## Verification Snapshot

- verified against a temporary `mysql:8` container on `127.0.0.1:3313`
- `python manage.py check` passed with the application database user
- `python manage.py migrate` applied the Step 2.3 accounts, students, academics, and integration migrations successfully
- `python -m compileall apps sis_backend` passed
- `pytest -q --cov=apps --cov-report=term-missing` passed with 35 tests and 91% total coverage
- `ruff check backend` passed
- targeted alignment verification passed for `apps/students/tests/test_students_api.py` and `apps/accounts/tests/test_access_control.py`, including the new student deactivation and field-level audit assertions

## Entry Criteria

- Phase 1 documentation baseline is frozen
- stack, architecture, ERD, and OpenAPI starter are approved
- version-control and change-log discipline are in place

## Expected Deliverables

- Django backend scaffold with environment-driven settings
- MySQL-backed core schema and migrations
- JWT login and refresh flow with enforced role/capability checks
- student, course, enrollment, grade, and user-admin core modules
- React frontend baseline with protected routes and API wiring
- local Docker Compose stack and CI workflow baseline

## Exit Criteria

- core SIS works without any Moodle dependency
- backend tests cover auth, RBAC, and core module behavior
- Step 2.4 frontend build passes and protected navigation is wired
- documented local stack can start consistently
- Step 2.5 CI runs lint, test, and build checks on the Phase 2 codebase

## Tracking

- [Phase 2 Changelog](CHANGELOG.md)
- [Phase 2 Implementation Plan](../../superpowers/plans/2026-04-12-phase-02-core-build-implementation.md)
- [Setup Guide](../../project/modern-sis-setup-guide.md)
