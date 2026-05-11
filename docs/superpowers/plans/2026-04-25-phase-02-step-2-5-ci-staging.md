# Phase 2 Step 2.5 CI And Staging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the stale CI workflow, enforce the backend coverage gate, add Docker image validation, and commit a distinct staging stack with later-phase placeholder services.

**Architecture:** Keep the required CI gate deterministic and aligned to the existing repo commands. Build a base-plus-overlay Compose stack where the real Phase 2 services run now and the later-phase services are present as profile-gated placeholders for future phases.

**Tech Stack:** GitHub Actions, Python 3.11, Django 5, pytest, ruff, Node 20, Vite, Vitest, Docker, Docker Compose, Nginx, MySQL 8

---

## Status

Implemented and verified on 2026-04-25.

## File Map

- Modify: `.github/workflows/django.yml`
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/playwright.yml`
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Create: `frontend/Dockerfile`
- Create: `frontend/.dockerignore`
- Create: `infra/docker-compose.yml`
- Create: `infra/docker-compose.dev.yml`
- Create: `infra/docker-compose.staging.yml`
- Create: `infra/staging.env.example`
- Modify: `infra/README.md`
- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `frontend/README.md`
- Modify: `docs/phases/phase-02-core-build/README.md`
- Modify: `docs/phases/phase-02-core-build/CHANGELOG.md`
- Modify: `CHANGELOG.md`

### Task 1: Replace The Stale CI Baseline

**Files:**
- Delete or replace: `.github/workflows/django.yml`
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/playwright.yml`

- [x] **Step 1: Write the failing CI-shape check**

Inspect the current workflow and confirm it is stale:

```bash
sed -n '1,220p' .github/workflows/django.yml
```

Expected: it targets incorrect Python versions, wrong install paths, and does not exercise the frontend or coverage gate.

- [x] **Step 2: Remove the stale workflow**

The old workflow must not coexist with the new one:

```bash
git rm .github/workflows/django.yml
```

- [x] **Step 3: Add the required CI workflow**

Create `.github/workflows/ci.yml` with:

- backend quality job using MySQL 8 service
- frontend quality job using Node 20
- container validation job building backend and frontend images plus Compose config validation
- required triggers on `push` and `pull_request` for `main`

- [x] **Step 4: Add the non-blocking Playwright workflow**

Create `.github/workflows/playwright.yml` with:

- `workflow_dispatch`
- optional `pull_request` trigger
- frontend install
- Playwright browser install
- browser test execution

- [x] **Step 5: Verify workflow syntax**

Run:

```bash
python - <<'PY'
from pathlib import Path
import yaml
for path in [Path('.github/workflows/ci.yml'), Path('.github/workflows/playwright.yml')]:
    with path.open() as fh:
        yaml.safe_load(fh)
print('workflow-yaml-ok')
PY
```

Expected: `workflow-yaml-ok`

### Task 2: Add Backend And Frontend Image Builds

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Create: `frontend/Dockerfile`
- Create: `frontend/.dockerignore`

- [x] **Step 1: Add the backend Docker build path**

Backend image must:

- use Python 3.11 slim
- install `backend/requirements/base.txt`
- copy backend source
- run `gunicorn sis_backend.wsgi:application`

- [x] **Step 2: Add the frontend Docker build path**

Frontend image must:

- use a Node build stage
- produce the Vite static bundle
- serve the bundle from Nginx in the final image

- [x] **Step 3: Add `.dockerignore` files**

Ignore local artifacts:

- `.venv`
- `node_modules`
- `dist`
- `.pytest_cache`
- `__pycache__`
- Playwright outputs

- [x] **Step 4: Verify image builds**

Run:

```bash
docker build -f backend/Dockerfile -t modern-sis-backend:test .
docker build -f frontend/Dockerfile -t modern-sis-frontend:test ./frontend
```

Expected: both builds exit `0`

### Task 3: Add Compose Baseline, Dev Overlay, And Staging Overlay

**Files:**
- Create: `infra/docker-compose.yml`
- Create: `infra/docker-compose.dev.yml`
- Create: `infra/docker-compose.staging.yml`
- Create: `infra/staging.env.example`

- [x] **Step 1: Create shared Compose definitions**

The base file must define:

- `db`
- `backend`
- `frontend`
- `proxy`
- `redis`
- `celery_worker`
- `celery_beat`
- `qdrant`
- `moodle`
- `moodle_db`

Later-phase services must use profiles so they do not activate by default.

- [x] **Step 2: Add the dev overlay**

The delivered dev overlay favors image-level parity with explicit developer-friendly port exposure because manual source-mounted development is already covered by the non-Compose runbook.

- [x] **Step 3: Add the staging overlay**

The staging overlay must:

- be distinct from local development
- drive the stack through the reverse proxy
- reference a staging env template
- avoid bind-mounted source assumptions

- [x] **Step 4: Validate Compose resolution**

Run:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config > /tmp/modern-sis-dev-compose.yaml
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml config > /tmp/modern-sis-staging-compose.yaml
```

Expected: both commands exit `0`

- [x] **Step 5: Verify the staging core stack boots**

Run:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml up -d db backend frontend proxy
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml ps
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml down
```

Expected: the four core services reach running or healthy state and the stack tears down cleanly.

### Task 4: Update Documentation And Versioning

**Files:**
- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `frontend/README.md`
- Modify: `infra/README.md`
- Modify: `docs/phases/phase-02-core-build/README.md`
- Modify: `docs/phases/phase-02-core-build/CHANGELOG.md`
- Modify: `CHANGELOG.md`

- [x] **Step 1: Document the CI workflow**

Add:

- required CI jobs
- backend coverage gate
- non-blocking Playwright workflow
- Python lint choice (`ruff`)

- [x] **Step 2: Document the Compose stacks**

Add:

- dev stack commands
- staging stack commands
- explanation of placeholder later-phase services and profiles

- [x] **Step 3: Update phase tracking**

Record:

- Step 2.5 as complete when verified
- Phase 3 Step 3.1 as the next setup-guide item

- [x] **Step 4: Update repo and phase changelogs**

Record CI, Docker, and staging changes in:

- `CHANGELOG.md`
- `docs/phases/phase-02-core-build/CHANGELOG.md`

### Task 5: Run Final Verification

**Files:**
- Verify all files changed in Tasks 1-4

- [ ] **Step 1: Verify backend quality locally**

Run:

```bash
cd backend
. /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/.venv/bin/activate
export DJANGO_SECRET_KEY='test-secret-key-with-sufficient-length-1234567890'
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
export MYSQL_DATABASE=modern_sis
export MYSQL_USER=modern_sis
export MYSQL_PASSWORD=modern_sis
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3313
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
ruff check .
pytest -q --cov=apps --cov-report=term-missing --cov-fail-under=80
```

Expected: all commands exit `0`

- [ ] **Step 2: Verify frontend quality locally**

Run:

```bash
cd frontend
npm ci
npm run typecheck
npm test -- --reporter=dot
npm run lint
npm run build
```

Expected: all commands exit `0`

- [ ] **Step 3: Verify Docker and Compose locally**

Run:

```bash
docker build -f backend/Dockerfile -t modern-sis-backend:test .
docker build -f frontend/Dockerfile -t modern-sis-frontend:test ./frontend
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml config
```

Expected: all commands exit `0`

- [ ] **Step 4: Review git diff and prepare completion**

Run:

```bash
git status --short
git diff --stat
```

Expected: only the intended Step 2.5 CI and staging files plus documentation changes are present.

## Spec Coverage Check

- setup-guide Step 2.5 CI requirement is covered by Task 1
- backend coverage gate is covered by Tasks 1 and 5
- Docker image build verification is covered by Tasks 2 and 5
- staging environment requirement is covered by Task 3
- documentation and versioning requirements are covered by Task 4

## Placeholder Scan

- no TODO or TBD placeholders remain
- later-phase services are explicitly described as placeholders, not unfinished hidden work

## Type And Naming Consistency

- Compose file names use the same `infra/docker-compose*.yml` convention throughout
- workflow names map consistently to CI and Playwright verification responsibilities
