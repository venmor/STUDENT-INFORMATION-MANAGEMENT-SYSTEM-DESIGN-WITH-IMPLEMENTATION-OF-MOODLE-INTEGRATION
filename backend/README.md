# Backend

This directory contains the Django backend for Modern SIS.

## Phase 2 Status

Step 2.1 establishes the project baseline:

- Django project scaffold
- environment-driven settings
- MySQL-backed initial migrations
- dependency management under `requirements/`

Step 2.2 adds the authentication and RBAC baseline:

- custom Django user model with primary-role enforcement
- seeded role catalog for `STUDENT`, `ADVISOR`, `FACULTY`, and `ADMIN`
- `wellbeing_coordinator` capability flags
- JWT login and refresh endpoints under `/api/v1/auth/`
- bcrypt-backed password storage via Django's built-in `BCryptSHA256PasswordHasher`
- central API access-control middleware with named route policies instead of view-level role decorators
- advisor/admin and capability-gated probe endpoints for access-control verification

Step 2.3 extends the backend into the first usable SIS domain baseline:

- full `FR-USR-007` password complexity validation and password change/reset workflows
- user administration APIs, deactivation, capability assignment, and access logging
- student profiles, dedicated student-record deactivation, advisor assignments, financial flags, approval-aware advising notes, and student correction-request submission plus admin review
- course catalog, section/timetable management, section roster reads, enrollment, drop, transfer, and CSV bulk enrollment
- attendance capture, attendance percentages on student detail, grade entry/update/officialisation, role-scoped grade list reads, GPA recalculation, and academic standing rules
- transcript PDF generation and integration outbox records for later Moodle synchronization
- field-level student change logging plus explicit audit coverage for student updates and advising-note updates
- route-policy middleware is the authoritative RBAC enforcement path; the stale pre-middleware `permissions.py` helper was removed during alignment

Step 2.4 adds the minimal backend contract support required for the React frontend:

- login responses now include `student_profile_id` when the authenticated user has a linked student record
- student section reads now expose programme-relevant active sections so the registration UI can list available targets
- `/api/v1/enrollments` now supports `GET` so the frontend can list current enrollments and obtain enrollment IDs for drop actions
- the Step 2.4 frontend uses these additions together with the existing Step 2.3 APIs to avoid inventing unsupported client-side workflows
- local testing now has a repeatable demo-data command: `python manage.py seed_demo_sis`

Step 2.5 adds the container and CI baseline for the backend runtime:

- `backend/Dockerfile` builds a Python 3.11 image for CI and Compose-based staging
- WhiteNoise now serves Django static assets for containerized environments
- `gunicorn` is the default backend container entrypoint
- the required CI workflow runs `manage.py check`, migration-drift verification, `ruff check`, and pytest with an 80% backend coverage gate

Step 3.1 adds the first Moodle integration verification hook:

- `python manage.py verify_moodle_rest` performs a narrow `core_user_get_users` call against a locally running Moodle instance
- the command reads `MOODLE_BASE_URL` and `MOODLE_WS_TOKEN` from the environment
- the command is intentionally limited to connectivity proof and does not implement provisioning sync, retries, or persistence yet

Step 3.2 adds the first real Moodle Lane A sync engine:

- `apps.integration.services.MoodleSyncService` wraps Moodle REST calls for users, sections, enrollments, and official grades
- `IntegrationOutboxEvent` now tracks attempts, last error, and processed timestamps for retryable sync processing
- `MoodleUserMap` and `MoodleCourseMap` persist Moodle IDs and minimal grade-target metadata
- `python manage.py process_moodle_sync` processes pending sync work and retries failed events
- automatic tests for Step 3.2 use mocked Moodle HTTP responses and do not require a live Moodle container

Step 3.3 adds the Moodle Lane B LTI v1.3 tool-provider baseline:

- `GET /lti/jwks` exposes only the SIS tool public key in JWKS format
- `GET /lti/login` validates Moodle OIDC login initiation and creates state/nonce records
- `POST /lti/launch` validates signed Moodle LTI launch JWTs and creates hashed SIS-side launch sessions
- `GET /lti/api/session` returns protected launch context to the embedded frontend tools
- `LtiOidcState` and `LtiLaunchSession` keep replay protection and embedded-session state minimal
- automatic tests for Step 3.3 use generated keys and mocked JWTs; no live Moodle instance is required

Step 3.4 adds the Moodle integration-verification and engagement ingestion foundation:

- `MoodleEngagementIngestionRun` records each manual or scheduled Moodle engagement ETL attempt
- `MoodleEngagementSnapshot` stores mapped Moodle user/course access snapshots linked back to SIS user, student, and section records where possible
- `python manage.py ingest_moodle_engagement` pulls `core_enrol_get_enrolled_users` data for mapped Moodle courses and stores access timestamps
- `python manage.py verify_phase_3_integrations` prints a local, non-live readiness report for Moodle config, LTI config, mappings, outbox state, and latest engagement ingestion
- automatic tests for Step 3.4 use mocked Moodle HTTP responses; no live Moodle instance is required

Step 3.5A adds admin-only Moodle sync monitoring APIs:

- `GET /api/v1/integration/moodle/summary`
- `GET /api/v1/integration/moodle/outbox-events`
- `POST /api/v1/integration/moodle/outbox-events/<id>/retry`
- `GET /api/v1/integration/moodle/user-maps`
- `GET /api/v1/integration/moodle/course-maps`
- `GET /api/v1/integration/moodle/engagement-runs`
- `GET /api/v1/integration/moodle/engagement-snapshots`
- these endpoints expose safe operational state only and never return Moodle tokens, LTI private keys, raw launch tokens, or full unsafe outbox payloads
- retry actions call the existing Step 3.2 `process_outbox_event` processor for failed and pending events

Step 3.5B adds the in-app Notification Center backend:

- `apps.notifications` stores user-scoped in-app notifications with category, severity, read state, optional action link, source reference, sanitized metadata, and timestamps
- `GET /api/v1/notifications`
- `GET /api/v1/notifications/summary`
- `POST /api/v1/notifications/<id>/read`
- `POST /api/v1/notifications/read-all`
- users can only list or mark their own notifications; admins do not receive global notification-management access in this slice
- Moodle sync failures create safe admin notifications, and confirmed enrollments, official grade releases, and approved advising notes create student notifications
- notifications are in-app only; email, SMS, push delivery, notification preferences, AI, at-risk scoring, wellbeing, and Step 3.5D-3.5G remain future scope

Step 3.5C adds the admin-only Audit/Admin Activity Viewer backend:

- `apps.audit` stores append-only `AuditEvent` records with actor, category, action, severity, summary, target, sanitized metadata, request context, and timestamps
- `GET /api/v1/admin/activity`
- `GET /api/v1/admin/activity/summary`
- `GET /api/v1/admin/activity/<id>`
- only admins can read audit activity; students, advisors, faculty, and unauthenticated clients are denied
- audit writes are internal service calls only; no public create/update/delete API exists
- metadata redaction removes Moodle tokens, LTI key material, raw JWT-like values, passwords, authorization values, `wstoken`, `access`, and `refresh` secrets
- audit hooks cover Moodle sync failure/processed/retry events, notification read/read-all actions, safe LTI launch-session creation, admin user actions, enrollment create/drop, and grade officialisation where clean existing hooks exist
- `python manage.py seed_audit_activity_demo` creates optional local demo audit records without live Moodle or secrets
- Step 3.5C does not implement Step 3.5D-3.5G, AI audit review beyond a placeholder category, at-risk scoring, wellbeing, external compliance export, or editable audit records

Step 3.5D adds the central Academic Calendar and Deadline Rules backend:

- `apps.calendar` stores institutional academic calendar events with audience, priority, status, source, academic year, semester, start/end dates, optional course-section links, and sanitized metadata
- `GET /api/v1/calendar/events/`
- `GET /api/v1/calendar/events/<id>/`
- `POST /api/v1/calendar/events/`
- `PATCH /api/v1/calendar/events/<id>/`
- `POST /api/v1/calendar/events/<id>/cancel/`
- `GET /api/v1/calendar/summary/`
- students, faculty, and advisors see active events relevant to their role; admins can see active, draft, and cancelled events
- admin create/update/cancel actions write audit records for `ACADEMIC_CALENDAR_EVENT_CREATED`, `ACADEMIC_CALENDAR_EVENT_UPDATED`, and `ACADEMIC_CALENDAR_EVENT_CANCELLED`
- `python manage.py seed_academic_calendar_demo` creates safe local demo dates and is safe to rerun
- `python manage.py sync_academic_calendar_from_sections` idempotently creates registration-open, registration-deadline, and drop-deadline events from existing course-section date fields
- optional notification fan-out is limited to admin-created high-priority or critical events when the admin explicitly requests it
- Step 3.5D does not implement Step 3.5E-3.5G, AI, at-risk scoring, wellbeing workflows, recurring rules, external calendar sync, personal reminders, timetable conflict detection, or Moodle assignment deadline import

## Local Verification Notes

- Use the application database user for `manage.py check` and `manage.py migrate`.
- Use a MySQL account that can create temporary databases when running `pytest`, because Django creates a separate test schema by default.
- Verify model drift with `python manage.py makemigrations --check --dry-run` before declaring Step 2.3 complete.
- For a fresh Step 3.3 LTI verification path, including `.env.local`, RSA keys, MySQL startup, mocked pytest checks, and optional Moodle launch testing, use `../docs/phases/phase-03-moodle-integration/STEP_3_3_TESTING.md`.
- The final Step 2.3 close-out verification used `python -m compileall apps sis_backend`, `python manage.py check`, `python manage.py migrate --noinput`, and `pytest -q --cov=apps --cov-report=term-missing`.
- The final Step 2.3 verification pass reached 93% total backend coverage across 43 passing tests.
- The Step 2.4 backend support additions were re-verified on a disposable `mysql:8` instance with `manage.py check`, `manage.py makemigrations --check --dry-run`, `manage.py migrate --noinput`, and `pytest -q --cov=apps --cov-report=term-missing`, yielding 46 passing tests and 93.58% backend coverage.
- The Step 2.5 CI gate uses the existing backend verification commands together with `ruff check .` and `--cov-fail-under=80`.
- The Step 3.1 command verification adds `pytest -q apps/integration/tests/test_verify_moodle_rest_command.py`.
- The Step 3.2 sync verification adds `pytest -q apps/integration/tests/test_moodle_sync_service.py apps/integration/tests/test_process_moodle_sync_command.py`.
- The Step 3.3 LTI verification adds `pytest -q apps/integration/tests/test_lti_tool_provider.py`.
- The Step 3.4 analytics verification adds `pytest -q apps/integration/tests/test_moodle_engagement_service.py apps/integration/tests/test_ingest_moodle_engagement_command.py apps/integration/tests/test_verify_phase_3_integrations_command.py`.
- The Step 3.5A monitoring API verification adds `pytest -q apps/integration/tests/test_moodle_sync_monitoring_api.py`.
- The Step 3.5B notification API verification adds `pytest -q apps/notifications/tests/`.
- The Step 3.5C audit API verification adds `pytest -q apps/audit/tests/`.
- The Step 3.5D calendar API verification adds `pytest -q apps/calendar/tests/`.

## Run and Test Step 3.5C UI With Backend Database

Use this path when you want the `/admin/audit-log` UI backed by real database records. Linux and Arch Linux can run these commands directly from the repository root. On Windows, use WSL2 with Ubuntu and Docker Desktop WSL integration.

Pull latest:

```bash
git status
git pull origin main
```

Start full dev stack:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d --build db backend frontend proxy moodle_db moodle
```

Run migrations:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py migrate
```

Create/reset admin:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py createsuperuser
```

If the admin user already exists:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py changepassword admin
```

Seed safe local audit demo activity:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py seed_audit_activity_demo
```

The demo command creates safe USER, MOODLE, NOTIFICATION, LTI, SYSTEM, and AI placeholder category records. It does not require live Moodle and does not create or store secrets.

Open the SIS UI:

- SIS URL: `http://127.0.0.1:8080`
- Audit page URL: `http://127.0.0.1:8080/admin/audit-log`
- Moodle URL: `http://127.0.0.1:8090`

Log in as an `ADMIN`. The audit viewer uses real backend API/database data, not static fake UI data.

Frontend hot reload option:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173/admin/audit-log
```

Backend test commands:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/audit/tests/
pytest -q apps/integration/tests/
pytest -q apps/notifications/tests/
ruff check .
```

Frontend test commands:

```bash
cd frontend
npm run typecheck
npm run lint
npm run test
npm run build
```

Tear down:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down
```

## Container Build

Build the backend image locally:

```bash
docker build -f backend/Dockerfile -t modern-sis-backend:test ./backend
```

If a Linux machine has noticeably slower package-download throughput inside Docker than on the host, a local-only fallback is `docker build --network host -f backend/Dockerfile -t modern-sis-backend:test ./backend`. The committed CI workflow still uses a standard `docker build`.

## Demo Data

Seed a repeatable local dataset after migrations:

```bash
python manage.py seed_demo_sis
```

Default demo credentials:

- `admin.demo / DemoPass123!`
- `advisor.demo / DemoPass123!`
- `faculty.demo / DemoPass123!`
- `student.demo1 / DemoPass123!`
- `student.demo2 / DemoPass123!`

The command is idempotent and refreshes the demo users, student profiles, advisor assignments, sections, enrollments, attendance, grades, advising notes, financial flags, and a correction request.

## Moodle REST Verification

After the local Moodle instance is running and a token has been created in Moodle admin:

```bash
export MOODLE_BASE_URL='http://127.0.0.1:8090'
export MOODLE_WS_TOKEN='paste-the-generated-token-here'
python manage.py verify_moodle_rest
```

Optional explicit username lookup:

```bash
python manage.py verify_moodle_rest --username admin
```

## Moodle Sync Processing

Step 3.2 extends the backend environment with:

```bash
export MOODLE_DEFAULT_CATEGORY_ID=1
export MOODLE_STUDENT_ROLE_ID=5
export MOODLE_EDITING_TEACHER_ROLE_ID=3
export MOODLE_INSTITUTION='Student Information System'
export MOODLE_GRADE_SOURCE='modern_sis'
```

These values should match the local Moodle instance you prepared through the Phase 3 runbook. The role IDs shown above are the typical local defaults; verify them in Moodle before relying on them.

Process pending sync work:

```bash
python manage.py process_moodle_sync
```

Retry failed sync work:

```bash
python manage.py process_moodle_sync --failed
```

Retry one specific outbox event:

```bash
python manage.py process_moodle_sync --event-id <outbox-event-uuid>
```

Known Step 3.2 limitation:

- official numeric grades can be pushed only when the mapped Moodle course has an explicit grade target (`grade_component`, `grade_activity_id`, `grade_item_number`)
- the service calls `gradereport_user_get_grade_items`, but it will not guess a write target if the local Moodle gradebook configuration is ambiguous

## Moodle LTI Tool Provider

Step 3.3 adds these environment values:

```bash
export LTI_PLATFORM_ISSUER_ALLOWLIST='http://127.0.0.1:8090'
export LTI_CLIENT_ID='paste-moodle-client-id-here'
export LTI_DEPLOYMENT_ID='paste-moodle-deployment-id-here'
export LTI_PRIVATE_KEY_FILE='../local-secrets/lti_private.pem'
export LTI_PUBLIC_KEY_FILE='../local-secrets/lti_public.pem'
export LTI_KEY_ID='modern-sis-lti-local'
export LTI_PLATFORM_AUTH_LOGIN_URL='http://127.0.0.1:8090/mod/lti/auth.php'
export LTI_PLATFORM_AUTH_TOKEN_URL='http://127.0.0.1:8090/mod/lti/token.php'
export LTI_PLATFORM_JWKS_URL='http://127.0.0.1:8090/mod/lti/certs.php'
export LTI_LAUNCH_SUCCESS_REDIRECT_BASE=''
```

Generate local keys outside tracked source:

```bash
mkdir -p ../local-secrets
openssl genrsa -out ../local-secrets/lti_private.pem 2048
openssl rsa -in ../local-secrets/lti_private.pem -pubout -out ../local-secrets/lti_public.pem
```

Do not commit private keys, copied Moodle tokens, or generated launch tokens. The JWKS endpoint derives or reads the public key and never exposes private key parameters.

For host-run live Moodle launches with Django on `127.0.0.1:8000` and Vite on `127.0.0.1:5173`, set `LTI_LAUNCH_SUCCESS_REDIRECT_BASE='http://127.0.0.1:5173'` before starting Django. The full Linux/Arch and Windows walkthrough is in `../docs/phases/phase-03-moodle-integration/STEP_3_3_TESTING.md`.

## Moodle Engagement Ingestion

Step 3.4 uses the existing Moodle REST config:

```bash
export MOODLE_BASE_URL='http://127.0.0.1:8090'
export MOODLE_WS_TOKEN='paste-the-generated-token-here'
```

The Moodle custom service also needs `core_enrol_get_enrolled_users`. Run a non-writing check first:

```bash
python manage.py ingest_moodle_engagement --dry-run
```

Create engagement snapshots:

```bash
python manage.py ingest_moodle_engagement
```

Optional scoping:

```bash
python manage.py ingest_moodle_engagement --section-id <section-uuid>
python manage.py ingest_moodle_engagement --user-id <sis-user-id>
python manage.py ingest_moodle_engagement --limit 10
python manage.py ingest_moodle_engagement --since 2026-04-30T00:00:00Z
```

Check local readiness without live Moodle calls:

```bash
python manage.py verify_phase_3_integrations
```

Step 3.4 stores access snapshots only. Assignment, quiz, and forum metrics are nullable placeholders for a later analytics expansion; the at-risk engine is not implemented here. Step 3.5A adds admin monitoring for the stored ingestion state, not analytics scoring or reporting.
