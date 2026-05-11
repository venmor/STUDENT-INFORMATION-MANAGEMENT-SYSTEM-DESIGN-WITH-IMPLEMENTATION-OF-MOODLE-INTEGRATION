# Phase 2 Changelog

## [Unreleased]

### Added
- Phase 2 README to track the core build separately from the Phase 1 documentation baseline.
- Django backend scaffold for Phase 2 Step 2.1.
- Backend dependency files and environment example for the Django/MySQL baseline.
- Reserved `frontend/` and `infra/` directories for later Phase 2 steps.
- Accounts app with a custom user model, primary-role catalog, capability flags, JWT auth endpoints, and probe endpoints for RBAC verification.
- Tracked `infra/.env.example` so the Step 2 environment template is version-controlled instead of being hidden by `.gitignore`.
- Central API access-policy registry, middleware, and Django system checks for Step 2.2 route enforcement.
- Bcrypt dependency and password-hash verification coverage for Step 2.2.
- Step 2.3 accounts hardening for full password complexity validation, access logging, password change/reset flows, and user administration APIs.
- Step 2.3 students app with student profiles, advisor assignments, financial flags, and approval-aware advising notes.
- Step 2.3 academics app with course catalog, sections, timetable records, enrollments, CSV bulk enrollment, attendance capture, grade workflows, transcript PDF export, GPA recalculation, and academic-standing rules.
- Step 2.3 integration outbox models for later Moodle provisioning and grade-passback work.
- Shared test utilities plus backend coverage tooling for the Phase 2 core-module slice.
- Step 2.3 student deactivation endpoint and field-level audit logging for student updates.
- Step 2.3 contract refresh so the OpenAPI document matches the implemented auth, user, student, and academics endpoints only.
- Step 2.3 ERD refresh to match integer user identifiers, normalized section timetables, and the implemented integration outbox model.
- Step 2.3 close-out endpoints for section list reads, section roster reads, role-scoped grade list reads, financial-flag updates, advising-note updates, and student correction-request submission plus admin review.
- Step 2.3 attendance-percentage exposure on student detail for frontend-ready student and advisor profile views.
- Step 2.4 React frontend scaffold with Vite, React 18, TypeScript, Tailwind CSS, TanStack Query, React Router, Axios, and Vitest.
- Step 2.4 protected routing and role-aware application shell for student, advisor, faculty, and admin flows.
- Step 2.4 student frontend workflows for profile overview, official grades, transcript download, section registration, section drops, and correction requests.
- Step 2.4 advisor frontend workflows for assigned-student search, unified profile view, financial-flag visibility, official grade history, and advising note draft management.
- Step 2.4 faculty frontend workflows for assigned section reads, roster reads, and draft grade entry.
- Step 2.4 admin frontend workflows for user management, student standing overrides, financial-flag management, advising-note approval, correction-request review, and grade officialisation.
- Step 2.4 supporting backend contract additions for login `student_profile_id`, student-visible registration sections, and `GET /enrollments`.
- Step 2.4 frontend rebuild design-system document at `frontend/docs/frontend-design-system.md`.
- Step 2.4 Playwright configuration and browser tests for role redirects, student registration, advisor profile navigation, faculty draft grade entry, admin user creation, and wellbeing shell visibility.
- Repeatable demo-data management command `python manage.py seed_demo_sis` plus regression coverage for the seeded multi-role dataset.
- Step 2.5 required CI workflow covering backend quality, frontend quality, and container validation on `main`.
- Step 2.5 separate Playwright workflow so browser verification remains available without becoming the blocking merge gate.
- Step 2.5 backend and frontend Dockerfiles plus reverse-proxy configuration for Compose-based runtime validation.
- Step 2.5 Compose base, dev overlay, and staging overlay with profile-gated placeholders for Redis, Celery, Qdrant, and Moodle services.

### Changed
- Reclassified the core implementation plan from Phase 1 to Phase 2 to match the setup guide.
- Reserved the `feat/phase-02-core-build` branch and `.worktrees/phase-02-core-build/` worktree as the execution path for core implementation.
- Shifted active execution for this slice to `feat/phase-02-step-2-1-bootstrap` so Step 2.1 can be delivered independently.
- Shifted the active execution slice to `feat/phase-02-step-2-2-auth-rbac` for the authentication and RBAC delivery step.
- Shifted the active execution slice to `feat/phase-02-step-2-2-security-hardening` for the Step 2.2 security and enforcement hardening pass.
- Shifted the active execution slice to `feat/phase-02-step-2-3-core-modules` for the Step 2.3 core SIS backend modules.
- Expanded the backend README with Step 2.2 auth/RBAC notes and the local test-database caveat for Django on MySQL.
- Reconciled the setup guide with the SRS by standardizing on Django's built-in bcrypt hasher and a central API RBAC middleware model.
- Carried the remaining `FR-USR-007` password complexity requirements into the implementation baseline before domain modules were added.
- Extended Step 2.3 audit coverage with explicit read-list events for students, financial flags, and advising notes.
- Tightened Step 2.3 grade workflows so create, update, and officialise operations require an active enrollment in the target section.
- Tightened Step 2.3 student update rules so manual academic-standing changes require an explicit override reason.
- Corrected the Phase 2 README so it no longer claims Step 2.3 was complete before the missing contract surface existed.
- Removed the stale pre-middleware `backend/apps/accounts/permissions.py` artifact so route-policy middleware remains the single RBAC source of truth.
- Updated the Phase 2 README so Step 2.4 is recorded as complete and Step 2.5 is recorded as the next implementation step.
- Replaced the placeholder `frontend/README.md` with frontend-specific setup, route, and auth notes for the real React application.
- Refreshed the OpenAPI contract to include the Step 2.4 frontend-support additions to auth and enrollment reads.
- Rebuilt the Step 2.4 frontend visual system to use neutral SIS branding, a component-first layout, richer loading and empty states, and a documented role-aware information hierarchy.
- Updated the frontend runbook to include browser-test setup and the `3306` / `3313` local database note for different developer machines.
- Tightened ESLint ignores so local Playwright output does not break lint on machines where browser tests have already been run.
- Expanded the `infra/` runbook and environment templates from placeholders into a documented Step 2.5 staging baseline.
- Updated the Phase 2 tracking README so Step 2.5 is recorded as complete and the next setup-guide item is Phase 3 Step 3.1.

### Notes
- Step 2.1 was re-verified against a temporary `mysql:8` container, not a local MariaDB workaround.
- Step 2.2 verification uses the application database user for `manage.py` commands and a database user with test-schema creation rights for `pytest`.
- The Step 2.2 hardening pass was re-verified on `mysql:8` with `manage.py check`, `manage.py migrate`, `pytest apps/accounts/tests -q`, and `ruff check backend`.
- Step 2.3 close-out verification used `mysql:8` on `127.0.0.1:3313` with `python -m compileall apps sis_backend`, `manage.py check`, `manage.py makemigrations --check --dry-run`, `manage.py migrate --noinput`, and `pytest -q --cov=apps --cov-report=term-missing`.
- The final Step 2.3 verification pass completed with 43 passing tests and 93% total backend coverage.
- Step 2.4 frontend verification used `npm test`, `npm run lint`, and `npm run build`.
- Step 2.4 backend-support verification used a disposable `mysql:8` database on `127.0.0.1:3313`, `manage.py check`, `manage.py makemigrations --check --dry-run`, `manage.py migrate --noinput`, and `pytest -q --cov=apps --cov-report=term-missing`.
- The Step 2.4 verification pass completed with 45 passing backend tests, 93% backend coverage, 3 passing frontend tests, and a clean frontend production build.
- The Step 2.4 frontend rebuild verification completed with `npm run typecheck`, `npm test -- --reporter=dot`, `npm run lint`, `npm run build`, and `npm run test:e2e`, resulting in 14 passing unit/component tests and 9 passing browser tests.
- Demo-data verification now includes `backend/apps/accounts/tests/test_seed_demo_sis_command.py`.
- Step 2.5 verification used `workflow-yaml-ok`, `docker build --network host -f backend/Dockerfile -t modern-sis-backend:step-2-5 ./backend`, `docker build -f frontend/Dockerfile -t modern-sis-frontend:step-2-5 ./frontend`, Compose config validation for dev and staging, and a staging-stack smoke check through `127.0.0.1:8088`.
