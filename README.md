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

Phase 2 is complete through Step 2.5. Phase 3 Step 3.1 established the local Moodle development instance and REST connectivity proof. Step 3.2 added Moodle Lane A provisioning and sync. Step 3.3 now adds Moodle Lane B LTI v1.3 tool-provider support with secure Moodle-to-SIS launches for advising and registration tools. The next implementation step is Step 3.4 integration verification and analytics ingestion. Phase 3.5 remains documented future scope only after Step 3.4.

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

## How To Test Phase 3 Moodle Integration

Step 3.1 is intentionally isolated from the normal Phase 2 workflow. Start Moodle only when you are doing Phase 3 integration work.

## Demo Accounts For Local Testing

### SIS Frontend Demo Accounts

Run `python manage.py seed_demo_sis` first, then sign in to the frontend at `http://127.0.0.1:5173` with:

- `admin.demo / DemoPass123!`
- `advisor.demo / DemoPass123!`
- `faculty.demo / DemoPass123!`
- `student.demo1 / DemoPass123!`
- `student.demo2 / DemoPass123!`

### Moodle Local Bootstrap Account

After starting the local Moodle overlay, sign in at `http://127.0.0.1:8090` with:

- `admin / ChangeMe123!`

This bootstrap account comes from `infra/moodle.env.example`.

### Moodle Service User Note

The `sis.service` account used for REST verification is created manually during the Phase 3 runbook. It is not seeded by the repo and does not have a fixed committed password. Choose a local password when you create it and keep it out of source control.

### 1. Start Moodle

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

Wait for the first-run Bitnami bootstrap to finish, then open `http://127.0.0.1:8090` and sign in with `admin / ChangeMe123!`.

Keep `MOODLE_HOST` empty for the local overlay so Moodle follows the incoming browser host and port. If Moodle renders as raw HTML or loads assets from `http://127.0.0.1/` without `:8090`, recreate the Moodle volumes, keep `MOODLE_HOST` empty, and start the overlay again:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down

docker volume rm \
  modern-sis_moodle_data \
  modern-sis_moodle_runtime_data \
  modern-sis_moodle_db_data

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

### 2. Complete The Moodle Admin Setup

In Moodle admin:

1. Enable web services at `Site administration > Advanced features`
2. Enable `REST` at `Site administration > Server > Web services > Manage protocols`
3. Create a dedicated service user such as `sis.service`
4. Create a least-privilege integration role for the service account with:
   `webservice/rest:use`, `moodle/user:viewdetails`, `moodle/user:viewhiddendetails`, `moodle/course:useremail`, `moodle/user:create`, `moodle/user:update`, `moodle/course:create`, `moodle/course:changefullname`, `moodle/course:changeshortname`, `moodle/grade:viewall`, and `moodle/grade:edit`
5. Assign that role to the dedicated service user at system context
6. Create a custom external service such as `Modern SIS REST`
7. Add the functions:
   `core_user_create_users`, `core_user_get_users`, `core_user_update_users`, `core_course_create_courses`, `core_course_update_courses`, `enrol_manual_enrol_users`, `enrol_manual_unenrol_users`, `gradereport_user_get_grade_items`, and `core_grades_update_grades`
8. Add the dedicated service user to the service's authorised users
9. Generate a token in `Manage tokens`

### 3. Export The Token, Lane A Settings, And Verify

```bash
. .venv/bin/activate
cd backend
export MOODLE_BASE_URL='http://127.0.0.1:8090'
export MOODLE_WS_TOKEN='paste-the-generated-token-here'
export MOODLE_DEFAULT_CATEGORY_ID=1
export MOODLE_STUDENT_ROLE_ID=5
export MOODLE_EDITING_TEACHER_ROLE_ID=3
export MOODLE_INSTITUTION='Student Information System'
export MOODLE_GRADE_SOURCE='modern_sis'
python manage.py verify_moodle_rest
```

Use `python manage.py verify_moodle_rest --username sis.service` if you want to force a specific lookup against the dedicated service account created for Step 3.1.

### 4. Process Moodle Sync Work

Once the token and Step 3.2 env values are exported:

```bash
python manage.py process_moodle_sync
```

Retry failed events:

```bash
python manage.py process_moodle_sync --failed
```

Retry one specific event:

```bash
python manage.py process_moodle_sync --event-id <outbox-event-uuid>
```

Important Step 3.2 limitation:

- official numeric grades can be pushed only when the SIS-side Moodle course map has an explicit grade target
- the service reads `gradereport_user_get_grade_items`, but it will not guess a write target if the gradebook structure is ambiguous

If you debug Moodle from inside the container, use `docker exec -u daemon ...` for PHP CLI commands so Moodle cache directories do not become root-owned.

### 5. Configure The Step 3.3 LTI Tool Provider

Generate local RSA keys in an untracked directory:

```bash
mkdir -p local-secrets
openssl genrsa -out local-secrets/lti_private.pem 2048
openssl rsa -in local-secrets/lti_private.pem -pubout -out local-secrets/lti_public.pem
```

Export SIS LTI settings:

```bash
export LTI_PLATFORM_ISSUER_ALLOWLIST='http://127.0.0.1:8090'
export LTI_CLIENT_ID='paste-moodle-client-id-here'
export LTI_DEPLOYMENT_ID='paste-moodle-deployment-id-here'
export LTI_PRIVATE_KEY_FILE='../local-secrets/lti_private.pem'
export LTI_PUBLIC_KEY_FILE='../local-secrets/lti_public.pem'
export LTI_KEY_ID='modern-sis-lti-local'
export LTI_PLATFORM_AUTH_LOGIN_URL='http://127.0.0.1:8090/mod/lti/auth.php'
export LTI_PLATFORM_JWKS_URL='http://127.0.0.1:8090/mod/lti/certs.php'
```

Register the SIS as a Moodle external tool with:

- Tool URL / launch URL: `http://127.0.0.1:8080/lti/launch`
- OIDC login URL: `http://127.0.0.1:8080/lti/login`
- JWKS URL: `http://127.0.0.1:8080/lti/jwks`
- Redirect URI: `http://127.0.0.1:8080/lti/launch`
- Target links:
  - `http://127.0.0.1:8080/lti/tools/advising-dashboard`
  - `http://127.0.0.1:8080/lti/tools/registration`

Store the Moodle-issued client ID and deployment ID in the SIS environment. Do not commit private keys, tokens, or copied launch JWTs.

### 6. Validate The Step 3 Backend Coverage

```bash
. .venv/bin/activate
export DJANGO_SECRET_KEY='test-secret-key-with-sufficient-length-1234567890'
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
export MYSQL_DATABASE=modern_sis
export MYSQL_USER=modern_sis
export MYSQL_PASSWORD=modern_sis
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3313
cd backend
pytest -q apps/integration/tests/test_verify_moodle_rest_command.py
pytest -q apps/integration/tests/test_moodle_sync_service.py apps/integration/tests/test_process_moodle_sync_command.py
pytest -q apps/integration/tests/test_lti_tool_provider.py
```

### 7. Stop Moodle

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down
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
6. [Phase 3 Moodle Integration](docs/phases/phase-03-moodle-integration/README.md)
7. [ADR-001 Technology Baseline](docs/architecture/ADR-001-technology-baseline.md)
8. [Technology Stack](docs/architecture/technology-stack.md)
9. [Architecture Diagrams](docs/architecture/architecture-diagrams.md)
10. [ERD Draft](docs/diagrams/modern-sis-erd.md)
11. [OpenAPI Starter](docs/api/openapi.yaml)
12. [Setup Guide](docs/project/modern-sis-setup-guide.md)
13. [Version Control Guidance](docs/process/version-control.md)
14. [Pre-Implementation Design Summary](docs/superpowers/specs/2026-04-11-modern-sis-preimplementation-design.md)

## Repository Index

| Path | Role | Status |
|---|---|---|
| `docs/project/modern-sis-problem-statement-and-vision.md` | Strategic purpose, problem, and product vision | Authoritative |
| `docs/project/SRS_Modern_SIS.md` | Functional and non-functional requirements baseline | Authoritative |
| `docs/phases/phase-01-foundation/README.md` | Entry point for the frozen documentation baseline | Frozen |
| `docs/phases/phase-01-foundation/CHANGELOG.md` | Phase 1 scoped change history | Frozen |
| `docs/phases/phase-02-core-build/README.md` | Entry point for the completed core implementation slice | Complete |
| `docs/phases/phase-02-core-build/CHANGELOG.md` | Phase 2 scoped change history | Complete |
| `docs/phases/phase-03-moodle-integration/README.md` | Entry point for the active Moodle integration slice | Active |
| `docs/phases/phase-03-moodle-integration/CHANGELOG.md` | Phase 3 scoped change history | Active |
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
- Phase 3: Moodle local instance, REST connectivity, Lane A provisioning, Lane B LTI embedded tools, and Step 3.4 verification next
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
