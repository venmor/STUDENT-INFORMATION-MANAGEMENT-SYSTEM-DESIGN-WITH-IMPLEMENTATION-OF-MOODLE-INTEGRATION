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
- Historical Step 2.3 implementation slice: `feat/phase-02-step-2-3-core-modules`
- Execution plan: `docs/superpowers/plans/2026-04-12-phase-02-core-build-implementation.md`

## Current Step

- Step 2.3 close-out is complete: the backend contract now matches the Step 2.3 scope in the setup guide and supports the missing read and update workflows needed by the frontend.
- Step 2.4 is now the next implementation step: scaffold the React 18 + TypeScript + Vite frontend and wire protected role-specific screens to the verified backend surface.
- Step 2.5 CI plus staging stack remains out of scope for the current slice.

## Implementation Progress

- Step 2.1 complete: Django backend scaffold, environment-driven settings, initial MySQL migration baseline, and reserved `frontend/` plus `infra/` directories
- Step 2.2 complete: custom user model, seeded role catalog, `wellbeing_coordinator` capability flags, JWT login/refresh endpoints, bcrypt-backed password storage, central API route-policy enforcement, and verified role/capability probe endpoints
- Step 2.3 close-out complete: enrollment validation now blocks grade create, update, and officialisation without an active enrollment; section list plus roster reads exist for faculty and admin flows; and grade list reads now respect student, advisor, faculty, and admin visibility rules.
- Step 2.3 student workflow completion: financial flags can be updated and cleared, draft advising notes can be updated with field-level audit logging, manual academic-standing overrides require a reason, attendance percentages are exposed on student detail, and students can submit correction requests for admin review.
- Step 2.3 documentation alignment complete: the OpenAPI contract, backend notes, and ERD now reflect the implemented route surface including correction requests and the additional Step 2.3 read endpoints.
- Step 2.4 is unblocked from the backend side: the student, advisor, faculty, and admin dashboard data dependencies called out in the setup guide now have matching REST endpoints.

## Verification Snapshot

- verified against a temporary `mysql:8` container on `127.0.0.1:3313`
- `python manage.py check` passed with the application database user
- `python manage.py makemigrations --check --dry-run` reported no model drift
- `python manage.py migrate` applied the Step 2.3 accounts, students, academics, and integration migrations successfully, including `students.0002_studentcorrectionrequest`
- `python -m compileall apps sis_backend` passed
- `pytest -q --cov=apps --cov-report=term-missing` passed with 43 tests and 93% total coverage
- targeted Step 2.3 close-out verification passed for section reads, roster reads, grade visibility, enrollment-aware grade validation, financial-flag updates, advising-note updates, attendance percentages, standing-override validation, and correction-request review flow

## Entry Criteria

- Phase 1 documentation baseline is frozen
- stack, architecture, ERD, and OpenAPI starter are approved
- version-control and change-log discipline are in place

## Expected Deliverables

- Django backend scaffold with environment-driven settings
- MySQL-backed core schema and migrations
- JWT login and refresh flow with enforced role/capability checks
- student, course, enrollment, grade, and user-admin core modules with the full Step 2.3 read/update workflow surface
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
