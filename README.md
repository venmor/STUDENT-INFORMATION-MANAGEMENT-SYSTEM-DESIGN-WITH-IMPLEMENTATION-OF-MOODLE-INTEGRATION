# Modern Student Information System

[![Open in VS Code Web](https://img.shields.io/badge/Open%20in-VS%20Code%20Web-0098FF?logo=visualstudiocode&logoColor=white)](https://vscode.dev/github/venmor/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION)
[![Fork on GitHub](https://img.shields.io/badge/Fork%20on-GitHub-181717?logo=github&logoColor=white)](https://github.com/venmor/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/fork)

Modern SIS is a proposed institutional platform that keeps the Student Information System as the authoritative academic and administrative record, integrates Moodle as the learning environment, and adds governed AI features for support and decision assistance.

## Open In VS Code

- `Open in VS Code Web` opens the canonical repository in `vscode.dev` in the browser using the official `vscode.dev/github/<owner>/<repo>` URL format.
- `Fork on GitHub` creates a collaborator-owned copy of the repository. After forking, they can open their fork in VS Code Web by changing the owner segment in the same `https://vscode.dev/github/<owner>/<repo>` pattern, or by opening the fork on GitHub and pressing `.`.
- For local desktop work, collaborators should use VS Code's `Git: Clone` command or `GitHub Repositories: Open Repository...` command. A direct `vscode://` badge link is not reliable in GitHub README rendering across browsers.

The purpose of the project is to reduce operational fragmentation across student records, course administration, Moodle activity, advising, and support workflows. The intended outcome is earlier intervention, less manual reconciliation, better student visibility, and stronger institutional auditability.

## Current Status

Phase 2 is now complete through Step 2.5: the backend core modules, rebuilt React frontend, CI baseline, and staging Compose stack are all in place on this delivery slice. The next setup-guide step is Phase 3 Step 3.1: stand up a Moodle instance.

## How To Test The System Currently

Use two terminals: one for Django and one for the Vite frontend. The Phase 2 system currently expects a local MySQL 8 instance. The documented container mapping uses `3313` so it does not collide with a workstation that already has MySQL or MariaDB on `3306`.

### 1. Prepare Python Dependencies

From the repository root:

```bash
uv venv .venv
. .venv/bin/activate
uv pip install -r backend/requirements/dev.txt
```

### 2. Start MySQL 8

```bash
docker run -d --name modern-sis-local-mysql \
  -e MYSQL_DATABASE=modern_sis \
  -e MYSQL_USER=modern_sis \
  -e MYSQL_PASSWORD=modern_sis \
  -e MYSQL_ROOT_PASSWORD=root \
  -p 127.0.0.1:3313:3306 mysql:8

docker exec modern-sis-local-mysql mysql -uroot -proot -e \
  "GRANT ALL PRIVILEGES ON *.* TO 'modern_sis'@'%'; FLUSH PRIVILEGES;"
```

### 3. Start The Backend

In the first terminal:

```bash
. .venv/bin/activate
cd backend
export DJANGO_SECRET_KEY='test-secret-key-with-sufficient-length-1234567890'
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
export MYSQL_DATABASE=modern_sis
export MYSQL_USER=modern_sis
export MYSQL_PASSWORD=modern_sis
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3313
python manage.py migrate --noinput
python manage.py runserver 127.0.0.1:8000
```

If your machine does not already use `3306`, you can map the container there instead and export `MYSQL_PORT=3306`.

### 4. Start The Frontend

In the second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The frontend proxies `/api` to the Django server on `127.0.0.1:8000`.

### 5. Run The Current Verification Commands

Backend:

```bash
. .venv/bin/activate
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q --cov=apps --cov-report=term-missing
```

Frontend:

```bash
cd frontend
npm test
npm run lint
npm run build
```

### 6. Validate The Step 2.5 Container Baseline

```bash
docker build -f backend/Dockerfile -t modern-sis-backend:test ./backend
docker build -f frontend/Dockerfile -t modern-sis-frontend:test ./frontend
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml config
```

Optional containerized local stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build -d db backend frontend proxy
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml down
```

Staging-oriented smoke path:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml up -d db backend frontend proxy
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml ps
curl -I http://127.0.0.1:8088
curl http://127.0.0.1:8088/api/v1/auth/login
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml down
```

If a Linux machine shows unusually slow dependency downloads during `docker build`, a local-only fallback is `docker build --network host ...`. The committed CI workflow and the portable default runbook both use standard `docker build`.

### 7. Clean Up Local Services

```bash
docker rm -f modern-sis-local-mysql
```

## What The System Is Intended To Do

- manage student records, courses, enrollments, grades, attendance, and advising context
- provision users, sections, enrollments, and official grades into Moodle
- embed selected SIS workflows inside Moodle using LTI v1.3
- provide AI-assisted co-pilot, summarisation, at-risk insights, and approval-gated wellbeing support
- enforce audit logging, role boundaries, and privacy controls throughout

## Approved Baseline

- Backend: `Python 3.11+`, `Django 5`, `Django REST Framework`
- Frontend: `React 18`, `TypeScript`, `Vite`
- Primary database: `MySQL 8.0`
- Background jobs: `Celery + Redis`
- Moodle integration: `Moodle REST API + PyLTI1p3`
- Vector store: `Qdrant`
- AI provider model: `OpenAI-compatible gateway`
- Deployment: `Docker Compose` on a Linux host for development, staging, and demonstration

## Recommended Reading Order

1. [Docs Index](docs/README.md)
2. [Problem Statement And Vision](docs/project/modern-sis-problem-statement-and-vision.md)
3. [Software Requirements Specification (SRS)](docs/project/SRS_Modern_SIS.md)
4. [Phase 1 Foundation](docs/phases/phase-01-foundation/README.md)
5. [Phase 2 Core Build](docs/phases/phase-02-core-build/README.md)
6. [ADR-001 Technology Baseline](docs/architecture/ADR-001-technology-baseline.md)
7. [Technology Stack](docs/architecture/technology-stack.md)
8. [Architecture Diagrams](docs/architecture/architecture-diagrams.md)
9. [ERD Draft](docs/diagrams/modern-sis-erd.md)
10. [OpenAPI Starter](docs/api/openapi.yaml)
11. [Setup Guide](docs/project/modern-sis-setup-guide.md)
12. [Version Control Guidance](docs/process/version-control.md)
13. [Pre-Implementation Design Summary](docs/superpowers/specs/2026-04-11-modern-sis-preimplementation-design.md)

## Repository Index

| Path | Role | Status |
|---|---|---|
| `docs/project/modern-sis-problem-statement-and-vision.md` | Strategic purpose, problem, and product vision | Authoritative |
| `docs/project/SRS_Modern_SIS.md` | Functional and non-functional requirements baseline | Authoritative |
| `docs/phases/phase-01-foundation/README.md` | Entry point for the frozen documentation baseline | Frozen |
| `docs/phases/phase-01-foundation/CHANGELOG.md` | Phase 1 scoped change history | Frozen |
| `docs/phases/phase-02-core-build/README.md` | Active entry point for the isolated core implementation work | Active |
| `docs/phases/phase-02-core-build/CHANGELOG.md` | Phase 2 scoped change history | Active |
| `docs/architecture/ADR-001-technology-baseline.md` | Locks the stack and phased delivery decisions | Authoritative |
| `docs/architecture/technology-stack.md` | Explains the selected stack, database split, and deployment rationale | Authoritative |
| `docs/architecture/architecture-diagrams.md` | Renderable Mermaid architecture and workflow diagrams | Authoritative |
| `docs/diagrams/README.md` | Diagram asset index and rendered-output layout | Maintained |
| `docs/diagrams/modern-sis-erd.md` | Domain model and ERD baseline | Authoritative |
| `docs/api/openapi.yaml` | Initial API contract surface | Authoritative draft |
| `docs/project/modern-sis-setup-guide.md` | Implementation order and build sequence guidance | Maintained |
| `docs/process/version-control.md` | Branching, commit, tagging, and changelog guidance | Maintained |
| `CHANGELOG.md` | Repository-wide change log | Maintained |
| `frontend/README.md` | Frontend setup, route, and auth notes for the Step 2.4 React app | Maintained |
| `docs/superpowers/specs/2026-04-11-modern-sis-preimplementation-design.md` | Summary of the approved baseline decisions | Maintained |
| `docs/diagrams/legacy/modern-sis-system-architecture.svg` | Static architecture illustration created before the Mermaid pack | Reference |
| `docs/archive/source-docx/Modern_SIS_Purpose_and_Problems.docx` | Original source Word document for early vision work | Historical source |
| `docs/archive/source-docx/Modern_SIS_Setup_Guide.docx` | Original source Word document for setup guidance | Historical source |

## Delivery Phases

- Phase 1: Documentation baseline, requirements, architecture, ERD, OpenAPI, and release/process setup
- Phase 2: Core SIS implementation, authentication, RBAC, audit logging, and local infrastructure
- Phase 3: Moodle Lane A provisioning plus Lane B embedded tools
- Phase 4: AI features in sequence: co-pilot and summarisation first, then at-risk, then wellbeing after policy approval

## Architecture Notes

- The SIS is the administrative source of truth.
- Moodle remains the learning platform, not the administrative system.
- Lane A is event-driven SIS to Moodle provisioning and grade pass-back.
- Lane B is Moodle-to-SIS launch via LTI v1.3 for embedded tools.
- Moodle engagement data is ingested on a schedule for analytics and at-risk processing.
- Wellbeing data is isolated from general AI audit logs and requires stricter access controls.

## Historical Source Material

The archived Word documents under [docs/archive/source-docx](docs/archive/source-docx) are kept as historical source material. The maintained Markdown files in `docs/` are the versions that should be reviewed and evolved going forward.
