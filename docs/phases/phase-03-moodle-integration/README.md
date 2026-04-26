# Phase 3 Moodle Integration

## Objective

Phase 3 introduces Moodle integration in controlled slices so Lane A REST provisioning and Lane B LTI work can build on the stable Phase 2 SIS baseline.

## Scope

- stand up a local Moodle development environment
- prove SIS-to-Moodle REST connectivity
- implement Lane A provisioning after connectivity is proven
- implement Lane B LTI only after Lane A is stable

## Status

- Status: In Progress
- Source guide: `docs/project/modern-sis-setup-guide.md` Phase 3
- Completed steps:
  - Step 3.1 Moodle development instance and REST connectivity proof
  - Step 3.2 Moodle Lane A provisioning sync baseline
- Next step: Step 3.3 LTI v1.3 tool-provider delivery
- After Step 3.4: planned Phase 3.5 SIS operational visibility and completion layer

## Current Step

- Step 3.1 is complete on this implementation slice: Moodle starts through a dedicated overlay and REST connectivity is proven through the SIS verification command.
- Step 3.2 extends that baseline with a retryable Moodle sync engine for SIS users, sections, enrollments, and official numeric grades.
- Step 3.3 remains the immediate next implementation step.
- Step 3.4 remains the integration-verification and analytics-ingestion gate before any Phase 3.5 work starts.

## Planned Phase 3.5 After Step 3.4

Phase 3.5 is documented future scope only. It is not implemented in the repository today and it does not change the immediate execution order:

1. Step 3.3 LTI v1.3 tool-provider delivery
2. Step 3.4 full integration verification and analytics ingestion
3. Phase 3.5 operational visibility and completion enhancements

Planned Phase 3.5 slices:

- `Step 3.5A` Moodle sync monitoring dashboard: admin UI over the Step 3.2 outbox, mappings, retry counts, and failed-event retry actions.
- `Step 3.5B` Notification center: in-app notifications for students, advisors, faculty, and admins around enrollment, grades, sync failures, and later alert-driven flows.
- `Step 3.5C` Audit/admin activity viewer: read-only admin interface for student-record, user, grade, sync, and later AI audit activity.
- `Step 3.5D` Academic calendar and deadline rules: central academic dates for registration, drop/add, grading, exam periods, and later AI deadline answers.
- `Step 3.5E` Admin reporting dashboard: aggregate operational reporting for enrollment, standing, capacity, attendance, financial flags, grade completion, and Moodle sync health.
- `Step 3.5F` Student document management: secure student-linked supporting-document storage with role-based access and audit events.
- `Step 3.5G` Admissions / applicant intake: optional/future applicant-stage workflow and accepted-applicant conversion into SIS user and student records.

`Step 3.5G` is explicitly optional/future. It should only be considered later if time and supervisor scope allow, and it must not block Step 3.3, Step 3.4, or the core AI phases.

## Expected Deliverables

- dedicated Moodle Compose overlay
- Moodle-specific env template
- manual admin runbook for web services and REST
- SIS-side `core_user_get_users` verification command
- `MoodleSyncService`
- retryable integration outbox processing
- Moodle user and course mapping models
- a manual retry/processing command for Lane A sync work

## Implementation Progress

- dedicated Moodle overlay added at `infra/docker-compose.moodle.yml`
- isolated Moodle env template added at `infra/moodle.env.example`
- base placeholder services tightened to include Moodle bootstrap variables, MariaDB health checks, and persisted `/bitnami/moodledata`
- SIS-side verification command added at `python manage.py verify_moodle_rest`
- backend regression tests added for missing config, network failure, invalid JSON, Moodle exception payloads, and success output
- `MoodleSyncService` added under `backend/apps/integration/services.py`
- `IntegrationOutboxEvent` extended with retry metadata (`attempts`, `last_error`, `last_attempt_at`, `processed_at`)
- `MoodleUserMap` and `MoodleCourseMap` added for persistent Moodle ID mapping
- user creation/update/deactivation, section creation/update, enrollment events, and official grades now emit retryable Moodle sync work
- `python manage.py process_moodle_sync` added for pending-event processing and failed-event retry
- mocked backend tests added for user provisioning, duplicate lookup fallback, course creation, enrollment sync, grade pass-back foundations, and token-safe failure handling

## Manual Runbook

### 1. Start The Local Moodle Slice

From the repository root:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

Check status:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  ps
```

Moodle is published on `http://127.0.0.1:8090`.

### 2. Wait For The First-Run Moodle Bootstrap

- The Bitnami container performs the initial Moodle installation from the bootstrap values in `infra/moodle.env.example`
- leave `MOODLE_HOST` empty for this local slice so Moodle follows the incoming host and port from the browser request
- Wait until the container stops running `admin/cli/install.php` and the site responds on `http://127.0.0.1:8090`
- Then sign in with the bootstrap admin account
- The default bootstrap values for this slice are:
  - username: `admin`
  - password: `ChangeMe123!`
  - email: `admin@example.com`
  - site name: `Student Information System Moodle`

For local Step 3 testing, the Moodle login is `admin / ChangeMe123!`.

If the page loads as unstyled HTML or asset links point to `http://127.0.0.1/` without `:8090`, the site was initialized with the wrong `MOODLE_HOST`. Reset the Moodle volumes, keep `MOODLE_HOST` empty for local use, and start again:

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

### 3. Enable Web Services

In Moodle admin:

- go to `Site administration > Advanced features`
- enable `Enable web services`
- save changes

### 4. Enable The REST Protocol

- go to `Site administration > Server > Web services > Manage protocols`
- enable `REST`

### 5. Create A Dedicated Service User

- go to `Site administration > Users > Accounts > Add a new user`
- create a dedicated non-human account such as `sis.service`
- use a strong password and a non-personal email address
- record that password locally; the repo does not seed `sis.service` and does not commit a default password for it

### 6. Create And Assign The Integration Role

`core_user_get_users` is not usable with a bare user account, and Step 3.2 broadens the local service account from read-only verification into Lane A provisioning. Create a dedicated integration role and assign it to the service user:

- go to `Site administration > Users > Permissions > Define roles`
- add a new role with no archetype, for example:
  - name: `SIS Web Service Integration`
  - short name: `siswebservice`
- allow these capabilities:
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
- assign that role to `sis.service` at `Site administration > Users > Permissions > Assign system roles`

Least-privilege note:

- the list above is intentionally narrow to the Moodle functions used in Step 3.2
- the course creation and course update capabilities may also need the correct category or course context assignment in Moodle
- avoid granting unrelated site-admin capabilities just to “make it work”

### 7. Create A Custom External Service

- go to `Site administration > Server > Web services`
- choose `Add a new custom service`
- recommended name: `Modern SIS REST`
- enable `Authorised users only`
- save the service

### 8. Add The Step 3.2 Functions

- open the new service
- add these functions:
  - `core_user_create_users`
  - `core_user_get_users`
  - `core_user_update_users`
  - `core_course_create_courses`
  - `core_course_update_courses`
  - `enrol_manual_enrol_users`
  - `enrol_manual_unenrol_users`
  - `gradereport_user_get_grade_items`
  - `core_grades_update_grades`

Step 3.1 verified only `core_user_get_users`. Step 3.2 requires the broader set above and nothing more.

### 9. Authorise The Service User

- open the service's `Authorised users` screen
- add the dedicated `sis.service` user you created

### 10. Generate A Token

- go to `Site administration > Server > Web services > Manage tokens`
- add a token for the dedicated service user and the `Modern SIS REST` service
- copy the generated token immediately

### 11. Store The Token And Lane A Settings For The SIS Backend

In the backend terminal:

```bash
export MOODLE_BASE_URL='http://127.0.0.1:8090'
export MOODLE_WS_TOKEN='paste-the-generated-token-here'
export MOODLE_DEFAULT_CATEGORY_ID=1
export MOODLE_STUDENT_ROLE_ID=5
export MOODLE_EDITING_TEACHER_ROLE_ID=3
export MOODLE_INSTITUTION='Student Information System'
export MOODLE_GRADE_SOURCE='modern_sis'
```

If you maintain a local untracked env file for backend commands, store the same values there instead.

Role-ID note:

- `5` and `3` are the typical local defaults for `student` and `editingteacher`
- verify them in your Moodle instance before relying on them

### 12. Verify REST Connectivity

With the backend virtualenv active:

```bash
cd backend
python manage.py verify_moodle_rest
```

Expected success output:

- `Moodle REST connectivity verified.`
- matched user count
- first matched username and Moodle user id

Optional explicit lookup:

```bash
python manage.py verify_moodle_rest --username sis.service
```

### 13. Process Moodle Sync Work

Process pending sync events:

```bash
cd backend
python manage.py process_moodle_sync
```

Retry failed events:

```bash
python manage.py process_moodle_sync --failed
```

Retry one event explicitly:

```bash
python manage.py process_moodle_sync --event-id <outbox-event-uuid>
```

Grade pass-back limitation for Step 3.2:

- only official numeric SIS grades are eligible
- the service calls `gradereport_user_get_grade_items`
- the Moodle write will proceed only when the mapped Moodle course has an explicit grade target (`grade_component`, `grade_activity_id`, `grade_item_number`)
- if that target is missing, the outbox event fails safely and remains retryable

### 14. Tear Down The Moodle Slice

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down
```

## Verification Snapshot

- overlay config resolves cleanly through `docker compose ... config`
- targeted backend command tests pass in `backend/apps/integration/tests/test_verify_moodle_rest_command.py`
- targeted Step 3.2 sync tests pass in:
  - `backend/apps/integration/tests/test_moodle_sync_service.py`
  - `backend/apps/integration/tests/test_process_moodle_sync_command.py`
- default Phase 2 dev and staging overlays remain unchanged
- Step 3.2 adds the first real provisioning baseline without making live Moodle mandatory for automated tests
- live REST proof succeeded against the documented Compose overlay on `http://127.0.0.1:8090`
- live REST proof succeeded against a real Moodle token with `python manage.py verify_moodle_rest --username sis.service`

## Troubleshooting

- if Moodle serves a blank or unstyled page after local bootstrap, reset the Moodle-specific volumes and keep `MOODLE_HOST` empty for local use
- if you run PHP CLI commands inside the Moodle container for debugging, run them as the web user to avoid cache permission regressions:

```bash
docker exec -u daemon <moodle-container> php -r 'define("CLI_SCRIPT", true); require "/opt/bitnami/moodle/config.php";'
```

## Exit Criteria

- local Moodle starts without changing default Phase 2 startup
- manual Moodle web-services setup is documented clearly
- the verification command proves REST connectivity with a real token
- the sync engine persists retryable Moodle failures and can retry them through `process_moodle_sync`
- automated tests prove user provisioning, course provisioning, enrollment sync, and grade pass-back foundations without requiring a live Moodle instance

## Tracking

- [Phase 3 Changelog](CHANGELOG.md)
- [Setup Guide](../../project/modern-sis-setup-guide.md)
- [SRS](../../project/SRS_Modern_SIS.md)
