# Phase 3 Changelog

## [Unreleased]

### Added
- Phase 3 README to track Moodle integration separately from the Phase 2 core build.
- Dedicated Moodle Compose overlay at `infra/docker-compose.moodle.yml`.
- Moodle env template at `infra/moodle.env.example`.
- `python manage.py verify_moodle_rest` for narrow Step 3.1 REST verification.
- Backend regression coverage for the Moodle REST verification command.
- `MoodleSyncService` and `process_moodle_sync` for the first Moodle Lane A provisioning baseline.
- Retry metadata on integration outbox events plus Moodle user and course mapping models.
- Mocked backend tests for Moodle user provisioning, course provisioning, enrollment sync, grade pass-back foundations, and command-driven retry handling.
- Step 3.3 Moodle Lane B LTI v1.3 provider endpoints:
  - `GET /lti/jwks`
  - `GET /lti/login`
  - `POST /lti/launch`
  - `GET /lti/api/session`
- DB-backed LTI state/nonce replay protection and hashed launch sessions.
- LTI frontend pages for advising and registration launched at `/lti/tools/advising-dashboard` and `/lti/tools/registration`.
- Mocked backend tests for JWKS, OIDC login, JWT claim validation, replay rejection, missing mappings, mapped launches, and protected tool access.
- Dedicated Step 3.3 testing guide at `STEP_3_3_TESTING.md` covering Linux, Arch Linux, Windows with WSL2 or PowerShell, `.env.local`, RSA keys, MySQL, backend tests, frontend checks, optional JWKS probing, optional live Moodle launches, expected results, and common fixes.
- Phase 3 Step 3.4 Moodle engagement ingestion foundation:
  - `MoodleEngagementIngestionRun`
  - `MoodleEngagementSnapshot`
  - `python manage.py ingest_moodle_engagement`
  - `python manage.py verify_phase_3_integrations`
- LTI advising roster engagement context and read-only frontend student-selection panel.
- Dedicated Step 3.4 test matrix at `STEP_3_4_TEST_MATRIX.md`.
- Mocked backend tests for engagement ingestion success, missing config, HTTP failure, Moodle exception payload, invalid JSON, unmapped users, command dry run, command summaries, readiness reporting, and token safety.
- Frontend unit coverage for the advising LTI roster-selection and engagement display flow.
- Phase 3.5A Moodle sync monitoring dashboard:
  - admin-only backend APIs under `/api/v1/integration/moodle/`
  - frontend admin route `/admin/moodle-sync`
  - summary cards, integration readiness, operational notes, outbox operations, Moodle mappings, engagement ingestion, and current-scope panels
  - safe failed/pending outbox retry through the existing Step 3.2 `process_outbox_event` processor
  - mocked backend and frontend tests for permissions, secret safety, filters, retry actions, route registration, sidebar navigation, empty states, and UI rendering

### Changed
- Updated the shared Compose base so the Moodle placeholder services now carry bootstrap variables, MariaDB health checks, and persisted Moodle runtime storage.
- Updated repository and infra runbooks so Phase 3 Step 3.1 can be run without altering the default Phase 2 workflow.
- Updated the Step 3.1 runbook to keep local `MOODLE_HOST` empty, document the required service-user role capabilities, and note the safe `daemon` user for Moodle CLI debugging.
- Expanded the Moodle runbook for Step 3.2 with required Lane A web-service functions, additional least-privilege capabilities, role/category env settings, and retryable sync commands.
- Documented a planned post-Step-3.4 `Phase 3.5 — SIS Operational Visibility and Completion Layer` in the Phase 3 roadmap.
- Expanded the Moodle runbook for Step 3.3 with LTI RSA key handling, Moodle external-tool registration values, SIS LTI environment variables, and manual launch verification steps.
- Updated Phase 3 sequencing so Step 3.3 is implemented, Step 3.4 has since been implemented, and Phase 3.5 remains future scope after Step 3.4.
- Added README and docs-index pointers to the dedicated Step 3.3 testing guide and clarified the local host-run launch redirect setup for Django plus Vite verification.
- Updated Phase 3 sequencing so Step 3.4 is implemented and Phase 3.5 remains future scope.
- Expanded the Moodle runbook with `core_enrol_get_enrolled_users`, engagement ingestion command examples, non-live readiness verification, and optional live Step 3.4 verification.
- Updated Phase 3 sequencing so Step 3.5A is implemented and Step 3.5B Notification Center is next. Steps 3.5B through 3.5G remain future scope.

### Notes
- Step 3.2 keeps automated tests independent from a live Moodle instance. Grade pass-back is real but intentionally narrow: it requires an explicit Moodle grade target instead of guessing gradebook structure.
- Step 3.3 keeps automated tests independent from a live Moodle instance. The embedded registration page is intentionally read-oriented in this slice and does not expose iframe-based enrollment mutations yet.
- Step 3.4 keeps automated tests independent from a live Moodle instance. It stores access snapshots from `core_enrol_get_enrolled_users`; assignment, quiz, and forum metrics remain nullable until a later analytics expansion. No at-risk scoring or Phase 3.5 dashboard is implemented.
- Step 3.5A keeps automated tests independent from a live Moodle instance. It monitors existing Step 3.2 and Step 3.4 records only; it does not implement notifications, academic calendar, admin reporting, document management, admissions, AI, at-risk scoring, or wellbeing.
