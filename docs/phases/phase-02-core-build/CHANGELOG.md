# Phase 2 Changelog

## [Unreleased]

### Added
- Phase 2 README to track the core build separately from the Phase 1 documentation baseline.
- Django backend scaffold for Phase 2 Step 2.1.
- Backend dependency files and environment example for the Django/MySQL baseline.
- Reserved `frontend/` and `infra/` directories for later Phase 2 steps.
- Accounts app with a custom user model, primary-role catalog, capability flags, JWT auth endpoints, and probe endpoints for RBAC verification.
- Tracked `infra/.env.example` so the Step 2 environment template is version-controlled instead of being hidden by `.gitignore`.

### Changed
- Reclassified the core implementation plan from Phase 1 to Phase 2 to match the setup guide.
- Reserved the `feat/phase-02-core-build` branch and `.worktrees/phase-02-core-build/` worktree as the execution path for core implementation.
- Shifted active execution for this slice to `feat/phase-02-step-2-1-bootstrap` so Step 2.1 can be delivered independently.
- Shifted the active execution slice to `feat/phase-02-step-2-2-auth-rbac` for the authentication and RBAC delivery step.
- Expanded the backend README with Step 2.2 auth/RBAC notes and the local test-database caveat for Django on MySQL.

### Notes
- Step 2.1 was re-verified against a temporary `mysql:8` container, not a local MariaDB workaround.
- Step 2.2 verification uses the application database user for `manage.py` commands and a database user with test-schema creation rights for `pytest`.
