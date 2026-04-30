# Changelog

All notable changes to this repository should be documented in this file.

The format follows a simple `Keep a Changelog` style adapted for a documentation-first project baseline.

## [Unreleased]

### Added
- VS Code Web and GitHub fork buttons in the repository README for collaborators.
- Phase 2 documentation path under `docs/phases/phase-02-core-build/`.
- Phase 2 Step 2.1 backend bootstrap under `backend/`.
- `frontend/` and `infra/` placeholder directories to preserve the agreed repo structure.
- Phase 2 Step 2.2 authentication baseline with a custom Django user model, seeded primary-role catalog, capability flags, and JWT auth endpoints.
- A tracked `infra/.env.example` file so the backend environment template is version-controlled.
- Central API access-policy enforcement for Step 2.2, backed by route policies and Django system checks.
- Explicit bcrypt dependency and password-hash verification coverage for Step 2.2.
- Phase 2 Step 2.3 password complexity enforcement, user administration APIs, and access logging in the Django backend.
- Phase 2 Step 2.3 student, academics, and integration apps covering profiles, advising, courses, sections, enrollments, attendance, grades, transcripts, and Moodle-facing outbox events.
- Shared backend test utilities and coverage tooling for the Step 2.3 core-module slice.
- Phase 2 Step 2.3 alignment pass covering student-record deactivation, field-level student audit logging, explicit read-list audit events, and removal of the stale pre-middleware RBAC helper.
- Step 2.3 contract refresh so `docs/api/openapi.yaml` and `docs/diagrams/modern-sis-erd.md` match the implemented backend rather than future planned phases.
- Phase 2 Step 2.4 React frontend implementation with role-aware dashboards, protected routes, API wiring, and frontend verification tooling.
- Step 2.4 frontend-support backend additions for login `student_profile_id`, student registration-target section reads, and enrollment list reads.
- Phase 2 Step 2.5 CI workflows for backend quality, frontend quality, container validation, and separate Playwright browser verification.
- Backend and frontend Dockerfiles plus Nginx configuration for the Step 2.5 containerized runtime baseline.
- `infra/docker-compose.yml`, `infra/docker-compose.dev.yml`, and `infra/docker-compose.staging.yml` with later-phase placeholder services modelled as profile-gated Compose services.
- `infra/docker-compose.moodle.yml` and `infra/moodle.env.example` for the isolated Phase 3 Step 3.1 Moodle slice.
- `python manage.py verify_moodle_rest` for narrow local Moodle REST verification against `core_user_get_users`.
- Phase 3 documentation path under `docs/phases/phase-03-moodle-integration/`.
- The Phase 3 Step 3.2 Moodle Lane A sync baseline: retryable integration outbox metadata, Moodle user/course mapping models, `MoodleSyncService`, and `process_moodle_sync`.
- Mocked backend test coverage for Moodle provisioning, enrollment sync, grade pass-back foundations, and command-driven retry processing.
- Phase 3 Step 3.3 Moodle Lane B LTI v1.3 tool-provider baseline with JWKS, OIDC login, launch validation, DB-backed nonce/state replay protection, hashed launch sessions, and protected LTI context API.
- Usable LTI frontend pages for `/lti/tools/advising-dashboard` and `/lti/tools/registration`.
- Mocked backend test coverage for LTI JWKS, OIDC login, launch JWT validation, replay rejection, mapping behavior, and protected embedded tool access.
- Dedicated Phase 3 Step 3.3 LTI testing guide for Linux, Arch Linux, Windows with WSL2 or PowerShell, local `.env.local` setup, RSA keys, MySQL startup, backend and frontend verification, optional JWKS probing, optional live Moodle launch testing, expected results, and common fixes.
- Phase 3 Step 3.4 integration-verification and Moodle engagement analytics-ingestion foundation with `MoodleEngagementIngestionRun`, `MoodleEngagementSnapshot`, `ingest_moodle_engagement`, and `verify_phase_3_integrations`.
- Step 3.4 LTI advising roster engagement context plus a read-only frontend student-selection panel.
- Dedicated Phase 3 Step 3.4 test matrix covering Lane A, Lane B, analytics ETL, failure/retry paths, unmapped contexts, secret safety, mocked automation, and optional live Moodle verification.
- Phase 3.5A Moodle sync monitoring dashboard with admin-only backend APIs, `/admin/moodle-sync`, summary cards, integration readiness, outbox operations, Moodle mappings, engagement ingestion state, safe current-scope guidance, and failed/pending outbox retry through the existing processor.
- Backend and frontend tests for the Phase 3.5A dashboard, including admin-only access, non-admin denial, secret-safety checks, outbox filters, retry behavior, route registration, sidebar navigation, empty/error states, and no-emoji UI label coverage.

### Changed
- Replaced the non-working README VS Code web link with the official `vscode.dev/github/<owner>/<repo>` format.
- Replaced the unreliable desktop `vscode://` badge with explicit desktop clone guidance.
- Corrected phase sequencing so Phase 1 remains documentation-only and implementation planning/work is classified under Phase 2.
- Reserved the active implementation slice for Step 2.1 only on `feat/phase-02-step-2-1-bootstrap`.
- Moved the active isolated implementation slice to `feat/phase-02-step-2-2-auth-rbac` for auth and RBAC delivery.
- Moved the active isolated implementation slice to `feat/phase-02-step-2-2-security-hardening` for the Step 2.2 security hardening pass.
- Moved the active isolated implementation slice to `feat/phase-02-step-2-3-core-modules` for the Step 2.3 core SIS backend modules.
- Reconciled the setup guide with the SRS by standardizing on Django's built-in bcrypt hasher and central API RBAC enforcement.
- Updated repository and phase documentation to reflect that `main` now carries the approved Step 2.2 baseline while Step 2.3 remains under isolated review.
- Narrowed the published API contract back to the real Step 2.3 backend surface by removing unimplemented AI and LTI endpoints from the OpenAPI document.
- Advanced the active implementation slice from Step 2.3 backend close-out to Step 2.4 frontend delivery.
- Updated phase and frontend documentation so Step 2.4 is recorded as complete and Step 2.5 is recorded as next.
- Expanded the tracked infra environment template and runbooks so the Step 2.5 CI and staging baseline is documented alongside the manual local runbook.
- Updated the repository and phase runbooks to record Step 2.5 as complete and Phase 3 Step 3.1 as the next implementation target.
- Updated the repository, backend, infra, and phase runbooks so Moodle can be started through a dedicated overlay without changing the default Phase 2 startup path.
- Tightened the shared Moodle placeholder services with bootstrap variables, a MariaDB health check, and persisted Moodle runtime storage.
- Corrected the Moodle overlay bootstrap guidance so local first-run `wwwroot` follows the incoming browser host and port instead of hardcoding an invalid local origin.
- Expanded the Moodle runbooks and backend env documentation for Step 3.2 with Lane A service functions, least-privilege capabilities, retry commands, role/category config, and grade pass-back limitations.
- Clarified the local testing credentials in the repository and Phase 3 runbooks so the seeded SIS demo accounts and the local Moodle bootstrap login are documented in one place.
- Documented a planned `Phase 3.5 — SIS Operational Visibility and Completion Layer` after Phase 3 Step 3.4 and before Phase 4.
- Updated Moodle registration runbooks with Step 3.3 LTI external-tool setup, key handling, and launch-test guidance. Step 3.4 has since been implemented, and Phase 3.5 remains future scope after Step 3.4.
- Linked the dedicated Step 3.3 testing guide from the repository, docs indexes, backend, frontend, infra, and Phase 3 documentation, and corrected the short root README external-tool target-link wording to point at `/lti/tools/*` instead of `/lti/launch`.
- Updated Moodle runbooks and docs indexes for Step 3.4 analytics ingestion, readiness verification, `core_enrol_get_enrolled_users`, and the new test matrix. Phase 3.5 remains future scope after Step 3.4.
- Updated Moodle integration documentation for Step 3.5A as implemented and Step 3.5B Notification Center as the next planned slice.

### Notes
- Phase 2 Step 2.1 verification now includes a fresh `mysql:8` container-backed `manage.py check` and `manage.py migrate` run.
- Phase 2 Step 2.2 verification uses a temporary `mysql:8` container, the application database user for runtime checks, and a database user with test-schema creation rights for `pytest`.
- The Step 2.2 security hardening pass was re-verified with `manage.py check`, `manage.py migrate`, `pytest apps/accounts/tests -q`, and `ruff check backend`.
- Phase 2 Step 2.3 verification used temporary `mysql:8` on `127.0.0.1:3313`, `python -m compileall apps sis_backend`, `manage.py check`, `manage.py migrate`, `pytest -q --cov=apps --cov-report=term-missing`, and `ruff check backend`, yielding 35 passing tests and 91% total backend coverage.
- The Step 2.3 alignment pass adds targeted backend verification for student deactivation, field-level audit diffs, and route-policy coverage before Step 2.4.
- Phase 2 Step 2.4 verification used a disposable `mysql:8` database for backend checks plus `npm test`, `npm run lint`, and `npm run build` for the frontend.
- Phase 2 Step 2.5 verification used `workflow-yaml-ok`, backend quality checks with 46 passing tests and 93.58% backend coverage, frontend quality checks with 14 unit/component tests and 9 Playwright tests, Docker image builds, Compose config validation, and a staging proxy smoke test on `127.0.0.1:8088`.
- Phase 3 Step 3.1 intentionally stops at manual Moodle admin setup and local REST connectivity proof. The final close-out was re-verified on the documented Compose overlay at `http://127.0.0.1:8090`, and provisioning sync, LTI, and retry orchestration remain later steps.
- Phase 3 Step 3.2 keeps automated verification independent from live Moodle. Grade pass-back is intentionally narrow and requires explicit Moodle grade-target metadata instead of guessed gradebook writes.
- Phase 3 Step 3.3 keeps automated verification independent from live Moodle by signing mocked LTI launch JWTs with generated test keys. Registration is read-oriented in this slice; mutating registration actions remain governed by the normal SIS enrollment engine and should be hardened in Step 3.4 before exposing iframe writes.
- Phase 3 Step 3.4 keeps automated verification independent from live Moodle. It ingests Moodle access snapshots only; assignment, quiz, and forum metrics remain nullable until a later analytics expansion, and no at-risk scoring or Phase 3.5 dashboard is implemented.
- Phase 3.5A keeps automated verification independent from live Moodle and does not implement notifications, academic calendar, admin reporting, document management, admissions, AI, at-risk scoring, or wellbeing.

## [0.1.0] - 2026-04-12

### Added
- Repository-level README with project purpose, baseline stack, and document index.
- Mermaid-based architecture diagram pack covering context, components, sequences, activities, states, and deployment.
- Phase documentation structure under `docs/phases/`.
- Version-control guidance under `docs/process/version-control.md`.
- Release checklist and frozen-deliverables tracking for Phase 1.

### Changed
- Reorganized documentation assets into a clearer structure under `docs/`.
- Consolidated rendered diagram outputs under `docs/diagrams/rendered/`.
- Moved source Word documents into `docs/archive/source-docx/`.

### Removed
- None.
