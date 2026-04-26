# Phase 2 Step 2.5 CI And Staging Design

## Status

Implemented and verified on 2026-04-25 after design review in the active Codex session.

## Outcome

The approved design was delivered as:

- a required `ci.yml` workflow for backend quality, frontend quality, and container validation
- a separate `playwright.yml` workflow for browser verification
- backend and frontend Dockerfiles for the Phase 2 runtime baseline
- shared Compose definitions plus dev and staging overlays
- profile-gated placeholders for Redis, Celery, Qdrant, and Moodle services
- updated repo, phase, backend, frontend, and infra runbooks

Verification closed with:

- `workflow-yaml-ok`
- backend quality gate passing with 46 tests and 93.58% coverage
- frontend quality gate passing with 14 unit/component tests and 9 browser tests
- successful backend and frontend image builds
- successful Compose config validation for dev and staging
- successful staging proxy smoke verification on `127.0.0.1:8088`

## Context

Phase 2 Step 2.4 is complete and merged to `main`. The repository now has a working Django backend, a rebuilt React frontend, demo-data seeding, and repeatable local verification commands. Step 2.5 is the next setup-guide item:

1. create continuous integration on pushes to `main`
2. enforce backend test coverage at or above 80%
3. add linting and image-build verification
4. introduce a staging environment distinct from local development

The repository already contains a stale `.github/workflows/django.yml` that targets the wrong paths and Python versions. The `infra/` directory is still only a placeholder. Step 2.5 therefore needs targeted implementation, not greenfield scaffolding.

## Scope

### In Scope

- replace the stale GitHub Actions workflow with a repo-accurate CI workflow
- enforce backend coverage in CI using the existing pytest coverage tooling
- run Python lint, frontend lint, frontend unit tests, frontend build, and Docker validation in CI
- add backend and frontend Dockerfiles suitable for CI image builds and Compose-based staging
- add a Docker Compose baseline plus distinct local-development and staging overlays
- include later-phase infrastructure placeholders in Compose so the platform shape matches the SRS and setup guide
- document all changes in the established phase, repo, and superpowers documentation structure

### Out Of Scope

- implementing Moodle REST sync logic
- implementing Celery tasks, Redis-backed queues, or Qdrant-backed retrieval logic
- implementing LTI launch security
- implementing AI services, at-risk processing, or wellbeing restricted storage
- making Playwright browser tests a required CI gate

Those later-phase capabilities may appear as profile-gated or disabled services in Compose, but Step 2.5 does not activate them as required runtime dependencies.

## Requirements Mapping

### Setup Guide Alignment

Step 2.5 in `docs/project/modern-sis-setup-guide.md` requires:

1. GitHub Actions on `main`
2. backend unit tests with an 80% coverage gate
3. linting for Python and TypeScript
4. Docker image build verification
5. a staging environment separate from local development

### SRS Alignment

This step directly supports:

- `NFR-MNT-004`: maintain at least 80% backend coverage measured on CI
- `NFR-SEC-009`: environment-driven secrets handling
- `NFR-MNT-007`: document significant infrastructure decisions
- the Phase 2 capability rollout baseline in Section 2.5 by preparing the delivery and verification pipeline for later Moodle and AI phases

## Design Decisions

### 1. CI Structure

The repository will use two workflows:

- `ci.yml`: required workflow for `push` and `pull_request` targeting `main`
- `playwright.yml`: separate browser workflow for deeper UI verification without making `main` protection depend on browser stability

The required CI workflow will contain these jobs:

- `backend-quality`
  - Python 3.11
  - MySQL 8 service container
  - install backend dev dependencies
  - `python manage.py check`
  - `python manage.py makemigrations --check --dry-run`
  - `python manage.py migrate --noinput`
  - Python lint
  - `pytest -q --cov=apps --cov-report=term-missing --cov-fail-under=80`

- `frontend-quality`
  - Node 20
  - `npm ci`
  - `npm run typecheck`
  - `npm run lint`
  - `npm test -- --reporter=dot`
  - `npm run build`

- `container-validation`
  - backend Docker image build
  - frontend Docker image build
  - Compose configuration validation for the shared base plus the dev and staging overlays

### 2. Python Lint Choice

The setup guide mentions `flake8`, but the implementation baseline already standardizes on `ruff` in `backend/requirements/dev.txt`. Step 2.5 will treat `ruff` as the Python lint gate instead of adding a second overlapping linter. This keeps the repo consistent with the existing toolchain and avoids redundant maintenance.

This is a controlled implementation-level adjustment, not a change in the intent of the guide. The guide requires a Python lint gate; `ruff check` will satisfy that gate.

### 3. Docker And Compose Structure

The Compose design uses one shared base file plus environment-specific overlays:

- `infra/docker-compose.yml`
  - shared service definitions and networks
- `infra/docker-compose.dev.yml`
  - local developer defaults
- `infra/docker-compose.staging.yml`
  - staging-oriented settings and reverse-proxy entrypoint

Real Phase 2 services:

- `db`
- `backend`
- `frontend`
- `proxy`

Later-phase placeholders included now:

- `redis`
- `celery_worker`
- `celery_beat`
- `qdrant`
- `moodle`
- `moodle_db`

Placeholder services will be profile-gated and clearly documented as inactive until later phases. This keeps the staging topology aligned with the SRS and setup guide without fabricating unfinished application behavior.

### 4. Image Design

Backend image:

- Python 3.11 slim base
- installs backend dependencies from `backend/requirements/`
- runs Django via `gunicorn`

Frontend image:

- multi-stage build
- Node build stage for Vite output
- Nginx runtime stage serving the static frontend build

The reverse proxy service will front the staging stack and route requests to frontend and backend containers.

### 5. Staging Environment Boundary

Staging must be distinct from local development, not just a renamed local stack. The distinction will be implemented through:

- separate Compose overlay file
- separate env file template for staging
- distinct hostnames / service wiring expectations in docs
- proxy-based entrypoint rather than relying on raw dev servers

## Files To Add Or Update

### CI

- replace `.github/workflows/django.yml`
- add `.github/workflows/ci.yml`
- add `.github/workflows/playwright.yml`

### Container And Infra

- add `backend/Dockerfile`
- add `backend/.dockerignore`
- add `frontend/Dockerfile`
- add `frontend/.dockerignore`
- add `infra/docker-compose.yml`
- add `infra/docker-compose.dev.yml`
- add `infra/docker-compose.staging.yml`
- add `infra/staging.env.example`
- update `infra/README.md`

### Documentation

- update `README.md`
- update `backend/README.md`
- update `frontend/README.md`
- update `docs/phases/phase-02-core-build/README.md`
- update `docs/phases/phase-02-core-build/CHANGELOG.md`
- update `CHANGELOG.md`

## Verification Strategy

Step 2.5 completion requires fresh verification evidence for:

- backend quality commands
- frontend quality commands
- backend image build
- frontend image build
- Compose config validation for dev and staging
- staging core stack boot validation

The separate Playwright workflow must also run successfully, but it is not the required branch-protection gate for `main`.

## Risks And Mitigations

### Risk: CI drifts from real local commands

Mitigation:

- use the same commands already documented and manually verified in Step 2.4
- keep docs and workflows updated together in the same change set

### Risk: placeholder services imply capabilities that do not exist yet

Mitigation:

- keep later-phase services profile-gated
- document them as inactive placeholders in `infra/README.md` and the phase README

### Risk: frontend browser tests slow or destabilize required CI

Mitigation:

- keep Playwright in a separate workflow
- preserve a deterministic required gate for merge protection

## Exit Criteria

Step 2.5 is complete when:

- required CI workflow is repo-accurate and green
- backend coverage is enforced at `>= 80%`
- Docker image builds succeed in CI and locally
- Compose validation succeeds for dev and staging overlays
- a staging stack exists separately from local development
- phase and repo documentation reflect the new CI and staging baseline
