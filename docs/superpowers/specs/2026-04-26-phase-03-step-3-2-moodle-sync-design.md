# Phase 3 Step 3.2 Moodle Lane A Sync Design

## Status

Approved for implementation on 2026-04-26 in the active Codex session. This spec is written from the current repository state, the setup guide, and the SRS Lane A requirements.

## Context

Phase 3 Step 3.1 is complete on `main`. The repository already has:

- a local Moodle overlay in `infra/docker-compose.moodle.yml`
- a Moodle env template in `infra/moodle.env.example`
- a narrow verification command at `python manage.py verify_moodle_rest`
- an `apps.integration` Django app
- an existing `IntegrationOutboxEvent` model
- existing enrollment and grade services that already emit Moodle-facing outbox events

The current gap is that there is still no provisioning sync engine. The SIS can prove REST connectivity, but it cannot yet:

- provision Moodle users from SIS users
- provision Moodle course shells from SIS sections
- sync SIS enrollments into Moodle
- push official SIS grades into Moodle
- record retryable sync failures in a way the team can reprocess

Step 3.2 must build that baseline without overreaching into LTI, AI, analytics ETL, or mandatory live-Moodle test dependencies.

## Goal

Implement a narrow but real Moodle Lane A provisioning baseline for:

- user provisioning
- course shell provisioning
- enrollment sync
- official-grade pass-back foundation
- persistent retryable failure logging

The implementation must use mocked Moodle HTTP responses for automated tests and must remain safe for normal backend/frontend development when Moodle is not running.

## Scope

### In Scope

- add a `MoodleSyncService` in the integration app
- extend the existing integration outbox into a retryable sync record
- add Moodle user and course mapping models
- wire SIS user, course section, enrollment, and official-grade events into the sync path
- implement best-effort immediate processing when Moodle configuration is present
- keep failed sync events persisted for manual retry
- add a management command for processing pending or failed Moodle sync events
- add mocked backend tests for success, failure, duplicate handling, and token-safe errors
- update Phase 3, backend, infra, and repository documentation/changelogs

### Out Of Scope

- LTI v1.3
- Moodle engagement ETL
- AI features
- automated Moodle admin UI setup
- mandatory live Moodle in CI
- Celery worker orchestration as a required runtime dependency for this slice
- a full reconciliation engine or nightly drift scan

## Requirements Mapping

### Setup Guide Alignment

This step must satisfy `Step 3.2 — Build the provisioning sync engine (Lane A)` in [docs/project/modern-sis-setup-guide.md](/home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/docs/project/modern-sis-setup-guide.md):

1. create a `MoodleSyncService`
2. implement user provisioning
3. implement course shell provisioning
4. implement enrollment sync
5. implement grade pass-back
6. implement failure handling and retryability
7. write automated tests without requiring a live Moodle instance

### SRS Alignment

This step directly advances Section `5.1 Lane A — Provisioning & Synchronisation` in [docs/project/SRS_Modern_SIS.md](/home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/docs/project/SRS_Modern_SIS.md):

- `MI-A-001` token in environment variable
- `MI-A-003` / `MI-A-005` user creation and Moodle user ID mapping
- `MI-A-006` user suspension on SIS deactivation
- `MI-A-007` course creation and Moodle course ID mapping
- `MI-A-008` course update
- `MI-A-010` enrollment sync
- `MI-A-011` unenrollment sync
- `MI-A-013` grade pass-back
- `MI-A-014` grade item discovery baseline

This step also supports `FR-GRD-006` and the non-functional latency intent, but it does not claim the final under-30-second production guarantee until a later background-worker slice exists.

## Repository-State Findings

The current repository behavior matters for the design:

- `apps.integration.models.IntegrationOutboxEvent` already exists, but it is too thin for retryable sync processing
- `apps.academics.services.create_enrollment()` already emits `ENROLLMENT_SYNC_REQUESTED`
- `apps.academics.services.officialise_grade()` already emits `GRADE_SYNC_REQUESTED`
- there is no existing Moodle user map or course map
- there is no existing sync processor, no retry metadata, and no management command beyond `verify_moodle_rest`
- user creation/update/deactivation and section creation/update currently happen in serializers/views, not in a shared domain-event framework

The Step 3.2 design should therefore extend the existing patterns rather than replacing them.

## Design Decisions

### 1. Reuse And Extend The Existing Integration Outbox

The repo already has `IntegrationOutboxEvent`. Step 3.2 will keep that model and add the minimum fields needed for retryable processing:

- `attempts`
- `last_error`
- `last_attempt_at`
- `processed_at`

The outbox will remain the durable record of requested Moodle sync work.

Why this design:

- it preserves the current repo direction
- it avoids inventing a second queue model
- it gives us persistence for retryable failures now
- it leaves room for later Celery-backed orchestration without deleting Step 3.2 work

### 2. Add Two Minimal Mapping Models

Step 3.2 will add:

- `MoodleUserMap`
- `MoodleCourseMap`

#### MoodleUserMap

Purpose:

- link SIS `accounts.User` to Moodle `user.id`

Minimal fields:

- `user`
- `moodle_user_id`
- `moodle_username`
- `last_synced_at`

#### MoodleCourseMap

Purpose:

- link SIS `academics.CourseSection` to Moodle `course.id`
- hold the minimum grade-target metadata required for grade pass-back

Minimal fields:

- `section`
- `moodle_course_id`
- `moodle_shortname`
- `moodle_category_id`
- `last_synced_at`
- nullable grade-target fields:
  - `grade_component`
  - `grade_activity_id`
  - `grade_item_number`
  - `grade_item_label`

These grade-target fields are justified because `core_grades_update_grades` does not accept only a course ID and user ID. Moodle requires a concrete grade item target. Step 3.2 will implement the storage and validation path, but it will not invent automatic gradebook targeting where Moodle configuration is ambiguous.

### 3. Keep The Sync Engine In The Integration App

Step 3.2 will add `backend/apps/integration/services.py` containing:

- a safe `MoodleSyncService`
- a small outbox processor using that service

The service will:

- read `MOODLE_BASE_URL` and `MOODLE_WS_TOKEN` from settings
- never log or raise the token value
- make Moodle REST calls through `requests`
- handle:
  - missing configuration
  - connection errors
  - HTTP errors
  - invalid JSON
  - Moodle exception payloads
  - unexpected payload shapes

### 4. Use Best-Effort Immediate Processing Plus Persistent Retry

This slice will not require Celery for correctness.

Behavior:

- when an outbox event is created and Moodle config is present, Step 3.2 will schedule best-effort processing after database commit
- if processing succeeds, the outbox event becomes `PROCESSED`
- if processing fails, the outbox event becomes `FAILED` with retry metadata
- if Moodle config is absent, the event stays `PENDING` until an operator runs the retry/process command

Why this design:

- it keeps default development safe when Moodle is not configured
- it still delivers real near-real-time sync when Moodle config exists
- it avoids introducing Celery as a hard dependency before the repo is ready for it

This design is intentionally reversible: a later Celery worker can consume the same outbox records without redesigning the domain models.

### 5. Emit Sync Events From The Existing Mutation Boundaries

Step 3.2 will not introduce model signals as the primary event framework.

Instead it will extend the existing explicit mutation boundaries:

- `UserCreateSerializer.create()` → user sync requested
- `UserUpdateSerializer.update()` → user sync requested when name/email changes or the account is suspended
- `UserDeactivateView.post()` → user suspend sync requested
- `CourseSectionSerializer.create()` / `update()` → course sync requested
- existing enrollment services keep emitting enrollment sync requests
- existing official grade service keeps emitting grade sync requests

Why this design:

- it matches the repository’s current style
- it is easier to reason about than implicit signals
- it keeps the Step 3.2 slice smaller and more testable

### 6. User Provisioning Will Prefer Idempotent Map Creation

User sync behavior:

- if a `MoodleUserMap` already exists, update the Moodle user
- if no map exists:
  - call `core_user_create_users`
  - then call `core_user_get_users`
  - store the Moodle user ID in `MoodleUserMap`

Duplicate/existing-user behavior:

- if Moodle reports that the username already exists, the sync layer will fall back to `core_user_get_users` by username
- if exactly one Moodle user is returned, the map is created and the sync proceeds

This gives a narrow reconciliation path without claiming to solve every manual Moodle drift scenario.

### 7. Course Shell Provisioning Will Use Returned IDs Directly

Course sync behavior:

- create active SIS sections in Moodle through `core_course_create_courses`
- store the returned Moodle course ID in `MoodleCourseMap`
- update mapped sections through `core_course_update_courses`

The course short name will be generated deterministically from the SIS section:

- `COURSECODE-SECTIONCODE-ACADEMICYEAR-SEMESTER`

This keeps the mapping readable and predictable for administrators.

Category behavior:

- Step 3.2 will use a configured Moodle category ID from environment/settings
- it will not create Moodle categories in this slice

### 8. Enrollment Sync Will Be Student-Focused In This Slice

Enrollment sync behavior:

- `ENROLLMENT_SYNC_REQUESTED` with `action=ENROLL` calls `enrol_manual_enrol_users`
- `ENROLLMENT_SYNC_REQUESTED` with `action=DROP` calls `enrol_manual_unenrol_users`

Role behavior:

- Step 3.2 will read the Moodle student role ID from settings
- it will support a generic role ID parameter in the service for future faculty/editing-teacher use
- it will not yet auto-enrol faculty based on section assignment changes

This keeps the slice aligned to the current SIS enrollment domain instead of expanding into broader course staffing automation.

### 9. Grade Pass-Back Will Be Real But Narrow

Grade sync behavior:

- only official SIS grades are eligible
- the service will first call `gradereport_user_get_grade_items`
- then it will call `core_grades_update_grades` only when the mapped course has an explicit usable grade target

Important limitation:

- Moodle grade update requires `component`, `activityid`, and `itemnumber`
- Step 3.2 will implement:
  - the service wrapper
  - payload construction
  - failure handling
  - persistence for grade-target metadata
  - mocked tests
- Step 3.2 will not fake automatic grade target discovery if the local Moodle course does not yet expose a clearly configured grade item target

If the required grade target is missing, the sync event must fail clearly and remain retryable. That is the safest behavior for this slice.

### 10. Add A Demonstration And Retry Command

Step 3.2 will add a management command to process or retry Moodle sync work, for example:

- `python manage.py process_moodle_sync`

Expected capabilities:

- process pending events
- optionally include failed events for retry
- optionally scope to one outbox event ID
- print a concise summary of processed / failed counts

This command is sufficient for demonstration and local verification without turning Step 3.2 into a scheduler implementation.

## Required Moodle Functions And Least-Privilege Notes

Step 3.2 broadens the Moodle external service from the Step 3.1 read-only proof. The documented runbook must add exactly these functions:

- `core_user_create_users`
- `core_user_get_users`
- `core_user_update_users`
- `core_course_create_courses`
- `core_course_update_courses`
- `enrol_manual_enrol_users`
- `enrol_manual_unenrol_users`
- `gradereport_user_get_grade_items`
- `core_grades_update_grades`

Step 3.2 also requires broader Moodle capabilities than Step 3.1. The runbook should document only the capabilities justified by the Moodle core function guards used in this slice:

- `webservice/rest:use`
- read-user capabilities already required by Step 3.1
- `moodle/user:create`
- `moodle/user:update`
- `moodle/course:create`
- `moodle/course:changefullname`
- `moodle/course:changeshortname`
- `moodle/grade:viewall`
- `moodle/grade:edit`

Course-category and course-context permissions may need to be granted in the specific category/course contexts used by the local Moodle instance. Step 3.2 docs must explain that the exact role assignment scope matters and that this slice intentionally avoids granting unrelated admin-wide capabilities.

## Configuration Additions

Step 3.2 will extend backend settings and env documentation with:

- `MOODLE_DEFAULT_CATEGORY_ID`
- `MOODLE_STUDENT_ROLE_ID`
- `MOODLE_EDITING_TEACHER_ROLE_ID`
- `MOODLE_INSTITUTION`
- optional grade sync source label, for example `MOODLE_GRADE_SOURCE`

These values belong in environment/configuration, not in source control logic.

## File Plan

### Create

- `backend/apps/integration/services.py`
- `backend/apps/integration/tests/test_moodle_sync_service.py`
- `backend/apps/integration/tests/test_process_moodle_sync_command.py`
- `backend/apps/integration/management/commands/process_moodle_sync.py`
- `docs/superpowers/plans/2026-04-26-phase-03-step-3-2-moodle-sync.md`

### Modify

- `backend/apps/integration/models.py`
- `backend/apps/integration/migrations/`
- `backend/apps/integration/apps.py` if startup wiring is needed
- `backend/apps/academics/services.py`
- `backend/apps/academics/api/serializers.py`
- `backend/apps/accounts/api/serializers.py`
- `backend/apps/accounts/api/views.py`
- `backend/sis_backend/settings.py`
- `docs/phases/phase-03-moodle-integration/README.md`
- `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- `backend/README.md`
- `infra/README.md`
- `README.md`
- `CHANGELOG.md`
- `docs/README.md`
- `docs/phases/README.md`

## Verification Strategy

Step 3.2 completion requires evidence for:

- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- targeted integration tests for Moodle sync service and command behavior
- full backend pytest run if practical
- coverage output if practical
- `ruff check`
- command smoke tests that do not require a live Moodle instance

Optional but non-blocking:

- a live local Moodle smoke path using Step 3.1 overlay and manual token if available

Automated tests must not require a live Moodle container.

## Risks And Mitigations

### Risk 1: Over-automating The Wrong Runtime

If Step 3.2 introduces Celery as a hard dependency now, the phase becomes more about worker orchestration than Moodle sync correctness.

Mitigation:

- persist retryable outbox state now
- keep command-driven retry in Step 3.2
- leave background worker orchestration for a later hardening slice

### Risk 2: Moodle Gradebook Ambiguity

`core_grades_update_grades` requires a concrete grade target. A blanket “push to Moodle gradebook” implementation can silently write to the wrong place if the target is guessed.

Mitigation:

- store explicit grade-target metadata
- call `gradereport_user_get_grade_items`
- fail clearly when a safe target is not configured

### Risk 3: Token Leakage In Errors

It is easy to accidentally log the Moodle token inside payload dumps.

Mitigation:

- never include request payloads with `wstoken` in exception messages
- keep logged error summaries safe and function-oriented

### Risk 4: Sync Failure Breaking SIS Mutations

The SIS is the source of truth. Moodle outage must not block user creation, enrollment, or official grading in the SIS.

Mitigation:

- create the outbox event inside the SIS mutation path
- process best-effort after commit
- store failures for retry instead of raising them back into the main transaction
