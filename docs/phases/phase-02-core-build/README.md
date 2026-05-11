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

- Status: Complete
- Source guide: `docs/project/modern-sis-setup-guide.md` Phase 2
- Historical Step 2.3 implementation slice: `feat/phase-02-step-2-3-core-modules`
- Execution plan: `docs/superpowers/plans/2026-04-12-phase-02-core-build-implementation.md`

## Current Step

- Step 2.4 is complete on this implementation slice: the React 18 + TypeScript + Vite frontend now exists and is wired to the verified Step 2.3 backend surface.
- Step 2.4 has also been rebuilt to replace the earlier placeholder UI with a role-specific, institution-neutral SIS frontend, a documented design system, and browser-tested role flows.
- Step 2.4 also introduced narrow backend support additions required by the frontend: login student-profile metadata, student registration-target section reads, and enrollment list reads.
- Step 2.5 is complete on this implementation slice: the required CI workflow, separate Playwright workflow, Docker image builds, and distinct staging Compose baseline are now in place and verified.
- The next implementation step in the setup guide is Phase 3 Step 3.1: stand up a Moodle instance for integration work.

## Implementation Progress

- Step 2.1 complete: Django backend scaffold, environment-driven settings, initial MySQL migration baseline, and reserved `frontend/` plus `infra/` directories
- Step 2.2 complete: custom user model, seeded role catalog, `wellbeing_coordinator` capability flags, JWT login/refresh endpoints, bcrypt-backed password storage, central API route-policy enforcement, and verified role/capability probe endpoints
- Step 2.3 close-out complete: enrollment validation now blocks grade create, update, and officialisation without an active enrollment; section list plus roster reads exist for faculty and admin flows; and grade list reads now respect student, advisor, faculty, and admin visibility rules.
- Step 2.3 student workflow completion: financial flags can be updated and cleared, draft advising notes can be updated with field-level audit logging, manual academic-standing overrides require a reason, attendance percentages are exposed on student detail, and students can submit correction requests for admin review.
- Step 2.3 documentation alignment complete: the OpenAPI contract, backend notes, and ERD now reflect the implemented route surface including correction requests and the additional Step 2.3 read endpoints.
- Step 2.4 is unblocked from the backend side: the student, advisor, faculty, and admin dashboard data dependencies called out in the setup guide now have matching REST endpoints.
- Step 2.4 frontend scaffold complete: Vite, React 18, TypeScript, Tailwind CSS, TanStack Query, React Router, Axios, and Vitest are configured under `frontend/`.
- Step 2.4 design-system rebuild complete: the frontend now uses a documented DM Sans/Sora/JetBrains Mono token system, neutral SIS branding, a custom logo asset, and component-first primitives under `frontend/docs/frontend-design-system.md`.
- Step 2.4 role-aware navigation complete: unauthenticated users are redirected to login, authenticated users land on role-specific homes, password-reset users are redirected to account password management, and wrong-role UI routes render a proper access-denied state.
- Step 2.4 student workflows complete: profile overview, official grades, transcript download, section registration, section drops, and correction-request submission are wired to live APIs.
- Step 2.4 advisor workflows complete: assigned-student search, unified student profile, financial-flag visibility, official grade history, and advising note create/update are wired to live APIs.
- Step 2.4 faculty workflows complete: assigned section list, roster reads, and draft grade entry are wired to live APIs.
- Step 2.4 admin workflows complete: operational overview, user management, standing overrides, financial-flag management, advising-note approval, correction-request review, and grade officialisation are wired to live APIs.
- Step 2.4 roadmap signalling complete: AI co-pilot, at-risk alerts, Moodle engagement, wellbeing, and AI audit-log surfaces are shown as explicit later-phase placeholders instead of fabricated integrations.
- Step 2.4 frontend verification coverage complete: unit tests cover primitives and route/auth behaviour, and Playwright covers role login, student registration, advisor profile navigation, faculty grade entry, admin user creation, and wellbeing shell visibility.
- Step 2.4 local-demo support complete: `python manage.py seed_demo_sis` now creates repeatable multi-role demo accounts and academic records for manual testing.
- Step 2.5 CI refresh complete: the stale GitHub Actions workflow has been replaced by a repo-accurate required pipeline for backend quality, frontend quality, and container validation, plus a separate Playwright workflow for browser verification.
- Step 2.5 staging baseline complete: backend and frontend Dockerfiles now exist, the `infra/` directory now contains shared Compose definitions plus dev and staging overlays, and later-phase services are modelled as profile-gated placeholders instead of undocumented gaps.
- Step 2.5 runtime verification complete: the staging-oriented core stack boots through the reverse proxy, serves the frontend on `127.0.0.1:8088`, and forwards API traffic to Django as expected.

## Verification Snapshot

- verified against a temporary `mysql:8` container on `127.0.0.1:3313`
- `python manage.py check` passed with the application database user
- `python manage.py makemigrations --check --dry-run` reported no model drift
- `python manage.py migrate` applied the Step 2.3 accounts, students, academics, and integration migrations successfully, including `students.0002_studentcorrectionrequest`
- `python -m compileall apps sis_backend` passed
- `pytest -q --cov=apps --cov-report=term-missing` passed with 43 tests and 93% total coverage
- targeted Step 2.3 close-out verification passed for section reads, roster reads, grade visibility, enrollment-aware grade validation, financial-flag updates, advising-note updates, attendance percentages, standing-override validation, and correction-request review flow
- frontend verification passed with `npm test`, `npm run lint`, and `npm run build`
- frontend rebuild verification passed with `npm run typecheck`, `npm test -- --reporter=dot`, `npm run lint`, `npm run build`, and `npm run test:e2e`
- Step 2.4 backend-support verification passed with `manage.py check`, `manage.py makemigrations --check --dry-run`, `manage.py migrate --noinput`, and `pytest -q --cov=apps --cov-report=term-missing`
- latest full backend verification reached 46 passing tests and 93.58% total backend coverage on a disposable `mysql:8` instance
- latest frontend verification reached 14 passing unit/component tests and 9 passing Playwright browser tests
- demo-data verification passed through the new idempotent command test for `seed_demo_sis`
- Step 2.5 workflow parsing verification passed with `workflow-yaml-ok`
- Step 2.5 image verification passed with `docker build -f frontend/Dockerfile -t modern-sis-frontend:step-2-5 ./frontend` and `docker build --network host -f backend/Dockerfile -t modern-sis-backend:step-2-5 ./backend`
- Step 2.5 Compose verification passed with `docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config`, `docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml config`, `docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml up -d db backend frontend proxy`, `docker compose ... ps`, and `docker compose ... down`
- Step 2.5 proxy verification passed with `curl -I http://127.0.0.1:8088` returning `200` and `curl http://127.0.0.1:8088/api/v1/auth/login` returning `405` through the reverse proxy

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
- documented design system and frontend rebuild runbook
- local Docker Compose stack and CI workflow baseline
- Step 2.4 frontend implementation records and verification notes
- Step 2.5 required CI workflow, Docker image build path, and staging-stack runbook
- distinct dev and staging Compose overlays with later-phase placeholder services

## Exit Criteria

- core SIS works without any Moodle dependency
- backend tests cover auth, RBAC, and core module behavior
- Step 2.4 frontend build passes and protected navigation is wired
- documented local stack can start consistently
- Step 2.5 CI runs lint, test, and build checks on the Phase 2 codebase
- Step 2.5 staging stack exists separately from the manual local-development runbook

## Tracking

- [Phase 2 Changelog](CHANGELOG.md)
- [Phase 2 Implementation Plan](../../superpowers/plans/2026-04-12-phase-02-core-build-implementation.md)
- [Setup Guide](../../project/modern-sis-setup-guide.md)
