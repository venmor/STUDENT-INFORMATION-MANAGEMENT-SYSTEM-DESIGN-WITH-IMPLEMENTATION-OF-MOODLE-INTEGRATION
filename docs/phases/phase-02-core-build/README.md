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
- Active implementation branch: `feat/phase-02-core-build`
- Active implementation worktree: `.worktrees/phase-02-core-build/`
- Execution plan: `docs/superpowers/plans/2026-04-12-phase-02-core-build-implementation.md`

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
- frontend build passes and protected navigation is wired
- documented local stack can start consistently
- CI runs lint, test, and build checks on the Phase 2 codebase

## Tracking

- [Phase 2 Changelog](CHANGELOG.md)
- [Phase 2 Implementation Plan](../../superpowers/plans/2026-04-12-phase-02-core-build-implementation.md)
- [Setup Guide](../../project/modern-sis-setup-guide.md)
