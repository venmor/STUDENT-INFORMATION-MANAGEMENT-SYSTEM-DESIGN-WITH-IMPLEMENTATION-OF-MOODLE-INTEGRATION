# Infrastructure

This directory contains the Docker Compose definitions, Nginx reverse-proxy configuration, and environment templates used for development, staging, and CI across all implementation phases.

## Assets

- `docker-compose.yml`
  - shared service definitions for the Phase 2 core stack
- `docker-compose.dev.yml`
  - local containerized stack overlay
- `docker-compose.staging.yml`
  - staging-oriented overlay with a separate entrypoint and env template
- `.env.example`
  - local dev variable template
- `staging.env.example`
  - staging variable template
- `docker-compose.moodle.yml`
  - dedicated Phase 3 overlay that activates Moodle without changing the default dev stack
- `moodle.env.example`
  - Moodle bootstrap plus SIS-side verification and Step 3.2 sync variables for the local Moodle slice
- `nginx/default.conf`
  - reverse-proxy config routing `/api`, `/admin`, and `/static` to Django and `/` to the frontend container

## Current Service Model

### Core Services (always started)

- `db` — MySQL 8.0 primary data store
- `backend` — Django REST API (gunicorn)
- `frontend` — React SPA (Nginx)
- `proxy` — Nginx reverse proxy (routes `/api` to backend, `/` to frontend)

### Profile-Gated Services (`--profile later-phase`)

These services support Moodle integration, AI/RAG features, and background processing:

- `redis` — Celery broker
- `celery_worker` — Background task worker
- `celery_beat` — Periodic task scheduler
- `qdrant` — Vector store for RAG/knowledge retrieval
- `moodle` — Bitnami Moodle 4.5 LMS
- `moodle_db` — MariaDB 11 for Moodle

## Phase 3 Moodle Overlay

Start Moodle only when Phase 3 integration work is needed:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

Moodle is published on `127.0.0.1:${MOODLE_HTTP_PORT:-8090}`.
`moodle_db` remains internal to the Compose network.

Environment values are documented in `infra/moodle.env.example`. For local work, copy that file into your preferred local env workflow or pass it to Compose with `--env-file`. Set `MOODLE_WS_TOKEN` only after you create the token in Moodle admin.

For a fresh Linux/Arch or Windows Step 3.3 test run, including local `.env.local` loading, MySQL startup, LTI key generation, automated checks, and optional live Moodle launch verification, use `../docs/phases/phase-03-moodle-integration/STEP_3_3_TESTING.md`.

For Step 3.4 integration verification and Moodle engagement ingestion, use `../docs/phases/phase-03-moodle-integration/STEP_3_4_TEST_MATRIX.md`.

Important bootstrap detail:

- leave `MOODLE_HOST` empty for the local overlay so Moodle uses the incoming `Host` header, including `:8090`
- set `MOODLE_HOST` only if you are serving Moodle behind a stable hostname or external reverse proxy
- the Bitnami image uses `MOODLE_HOST` only on first initialization when it writes Moodle `wwwroot`
- for Step 3.1 verification, the dedicated service user also needs a system role that grants `webservice/rest:use` and the capabilities required by `core_user_get_users`
- Step 3.2 adds sync-specific environment values:
  - `MOODLE_DEFAULT_CATEGORY_ID`
  - `MOODLE_STUDENT_ROLE_ID`
  - `MOODLE_EDITING_TEACHER_ROLE_ID`
  - `MOODLE_INSTITUTION`
  - `MOODLE_GRADE_SOURCE`
  - `MOODLE_SYNC_TIMEOUT`
- Step 3.3 adds LTI-specific environment values:
  - `LTI_PLATFORM_ISSUER_ALLOWLIST`
  - `LTI_CLIENT_ID`
  - `LTI_DEPLOYMENT_ID`
  - `LTI_PRIVATE_KEY` or `LTI_PRIVATE_KEY_FILE`
  - `LTI_PUBLIC_KEY` or `LTI_PUBLIC_KEY_FILE`
  - `LTI_KEY_ID`
  - `LTI_PLATFORM_AUTH_LOGIN_URL`
  - `LTI_PLATFORM_AUTH_TOKEN_URL`
  - `LTI_PLATFORM_JWKS_URL`
  - `LTI_LAUNCH_SUCCESS_REDIRECT_BASE`
  - `LTI_STATE_TTL_SECONDS`
  - `LTI_SESSION_TTL_SECONDS`
  - `LTI_SESSION_COOKIE_NAME`
  - `LTI_SESSION_COOKIE_SECURE`
  - `LTI_SESSION_COOKIE_SAMESITE`
- Step 3.4 uses the same Moodle REST token and adds no new required env vars. The Moodle custom external service must include `core_enrol_get_enrolled_users` for `python manage.py ingest_moodle_engagement`.
- if Moodle loads as unstyled HTML or asset links point to `http://127.0.0.1/` without `:8090`, recreate the Moodle volumes:

```bash
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase down
docker volume rm modern-sis_moodle_data modern-sis_moodle_runtime_data modern-sis_moodle_db_data
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase up -d moodle_db moodle
```

If you run ad hoc Moodle PHP CLI commands in the container, prefer `docker exec -u daemon ...` so runtime caches stay writable by the web process.

## Step 3.2 Moodle Service Expansion

Step 3.2 keeps Moodle optional for day-to-day Phase 2 development, but it expands the documented manual Moodle setup for Lane A sync work.

Additional Moodle web-service functions required for Step 3.2:

- `core_user_create_users`
- `core_user_get_users`
- `core_user_update_users`
- `core_course_create_courses`
- `core_course_update_courses`
- `enrol_manual_enrol_users`
- `enrol_manual_unenrol_users`
- `gradereport_user_get_grade_items`
- `core_grades_update_grades`
- `core_enrol_get_enrolled_users` for Step 3.4 engagement ingestion and optional enrollment reconciliation

Additional Moodle capabilities required for the dedicated service role:

- `webservice/rest:use`
- `moodle/user:viewdetails`
- `moodle/user:viewhiddendetails`
- `moodle/course:useremail`
- `moodle/user:create`
- `moodle/user:update`
- `moodle/course:create`
- `moodle/course:changefullname`
- `moodle/course:changeshortname`
- `moodle/grade:viewall`
- `moodle/grade:edit`
- `moodle/course:viewparticipants`

Least-privilege note:

- grant only the capabilities needed for the exact functions above
- verify the local Moodle role IDs before exporting `MOODLE_STUDENT_ROLE_ID` or `MOODLE_EDITING_TEACHER_ROLE_ID`
- the course-creation and course-update capabilities may need the correct category or course context assignment in Moodle, not just a generic system role
- `core_enrol_get_enrolled_users` may require the service role to view course participants in the relevant course/category context

## Step 3.3 LTI Tool Provider Expansion

Step 3.3 keeps the existing reverse-proxy split:

- `/lti/jwks`, `/lti/login`, `/lti/launch`, and `/lti/api/*` route to Django
- `/lti/tools/*` routes to the React frontend

For local key files, use an untracked directory such as `local-secrets/`:

```bash
mkdir -p local-secrets
openssl genrsa -out local-secrets/lti_private.pem 2048
openssl rsa -in local-secrets/lti_private.pem -pubout -out local-secrets/lti_public.pem
```

Then set:

```bash
LTI_PRIVATE_KEY_FILE=./local-secrets/lti_private.pem
LTI_PUBLIC_KEY_FILE=./local-secrets/lti_public.pem
```

Use `LTI_SESSION_COOKIE_SECURE=true` and `LTI_SESSION_COOKIE_SAMESITE=None` when the SIS is served over HTTPS and embedded cross-site in Moodle. The local HTTP runbook keeps `Lax` for browser compatibility on `127.0.0.1`.

The dedicated Step 3.3 testing guide documents the recommended host-run live launch path with Django on `127.0.0.1:8000`, Vite on `127.0.0.1:5173`, Moodle on `127.0.0.1:8090`, and `LTI_LAUNCH_SUCCESS_REDIRECT_BASE='http://127.0.0.1:5173'`.

## Step 3.4 Engagement Ingestion

Step 3.4 keeps Moodle optional for automated tests. The live Moodle overlay is needed only when you want to verify the actual local Moodle service.

The ingestion command uses the existing REST endpoint and token:

```bash
cd backend
python manage.py ingest_moodle_engagement --dry-run
python manage.py ingest_moodle_engagement
```

The readiness command is non-live by default:

```bash
python manage.py verify_phase_3_integrations
```

Least-privilege guidance:

- add only `core_enrol_get_enrolled_users` for this Step 3.4 ingestion foundation
- grant the dedicated service user participant-view access only in the needed course/category/system context
- do not add the richer assignment, quiz, or forum functions until a later analytics slice implements and tests those calls
- do not store real Moodle tokens, LTI private keys, or generated launch JWTs in tracked files

## Commands

From the repository root, the easiest local demonstration command is:

```bash
./scripts/dev-up.sh
```

That command starts the core development stack, runs migrations, seeds demo SIS data, and tries to open `http://127.0.0.1:8080`. Use `./scripts/dev-up.sh --full` when you also want Moodle, Qdrant, and richer AI demo data.

The first run has to download Docker Hub images before Compose can start. The script pre-pulls the required service and build-base images with retries, so transient errors such as Docker Hub auth token timeouts are usually fixed by rerunning the same command after the connection recovers. To wait longer between retry attempts, run for example `DOCKER_PULL_RETRIES=5 DOCKER_PULL_RETRY_DELAY=10 ./scripts/dev-up.sh --full`.

Validate the local containerized stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
```

Validate the Moodle overlay:

```bash
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase config
```

Start the local containerized stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build -d db backend frontend proxy
```

The dev overlay publishes:

- MySQL on `127.0.0.1:${DEV_DB_PORT:-3313}`
- the reverse proxy on `127.0.0.1:${DEV_HTTP_PORT:-8080}`

Validate the staging stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml config
```

Start the staging-oriented stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml up --build -d db backend frontend proxy
```

The staging overlay publishes the reverse proxy on `127.0.0.1:${STAGING_HTTP_PORT:-8088}` and keeps the database internal to the Compose network.

Smoke-check the staging entrypoint:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml ps
curl -I http://127.0.0.1:8088
curl http://127.0.0.1:8088/api/v1/auth/login
```

Tear down either stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml down
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml down
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase down
```
