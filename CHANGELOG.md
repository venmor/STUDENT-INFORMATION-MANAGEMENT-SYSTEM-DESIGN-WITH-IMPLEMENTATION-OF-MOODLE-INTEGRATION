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

### Notes
- Phase 2 Step 2.1 verification now includes a fresh `mysql:8` container-backed `manage.py check` and `manage.py migrate` run.
- Phase 2 Step 2.2 verification uses a temporary `mysql:8` container, the application database user for runtime checks, and a database user with test-schema creation rights for `pytest`.
- The Step 2.2 security hardening pass was re-verified with `manage.py check`, `manage.py migrate`, `pytest apps/accounts/tests -q`, and `ruff check backend`.
- Phase 2 Step 2.3 verification used temporary `mysql:8` on `127.0.0.1:3313`, `python -m compileall apps sis_backend`, `manage.py check`, `manage.py migrate`, `pytest -q --cov=apps --cov-report=term-missing`, and `ruff check backend`, yielding 33 passing tests and 90% total backend coverage.

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
