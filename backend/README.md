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

## Local Verification Notes

- Use the application database user for `manage.py check` and `manage.py migrate`.
- Use a MySQL account that can create temporary databases when running `pytest`, because Django creates a separate test schema by default.
- Verify model drift with `python manage.py makemigrations --check --dry-run` before declaring Step 2.3 complete.
- The final Step 2.3 close-out verification used `python -m compileall apps sis_backend`, `python manage.py check`, `python manage.py migrate --noinput`, and `pytest -q --cov=apps --cov-report=term-missing`.
- The final Step 2.3 verification pass reached 93% total backend coverage across 43 passing tests.
- The Step 2.4 backend support additions were re-verified on a disposable `mysql:8` instance with `manage.py check`, `manage.py makemigrations --check --dry-run`, `manage.py migrate --noinput`, and `pytest -q --cov=apps --cov-report=term-missing`, yielding 46 passing tests and 93.58% backend coverage.
- The Step 2.5 CI gate uses the existing backend verification commands together with `ruff check .` and `--cov-fail-under=80`.
- The Step 3.1 command verification adds `pytest -q apps/integration/tests/test_verify_moodle_rest_command.py`.
- The Step 3.2 sync verification adds `pytest -q apps/integration/tests/test_moodle_sync_service.py apps/integration/tests/test_process_moodle_sync_command.py`.

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
