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

### Changed
- Updated the shared Compose base so the Moodle placeholder services now carry bootstrap variables, MariaDB health checks, and persisted Moodle runtime storage.
- Updated repository and infra runbooks so Phase 3 Step 3.1 can be run without altering the default Phase 2 workflow.
- Updated the Step 3.1 runbook to keep local `MOODLE_HOST` empty, document the required service-user role capabilities, and note the safe `daemon` user for Moodle CLI debugging.
- Expanded the Moodle runbook for Step 3.2 with required Lane A web-service functions, additional least-privilege capabilities, role/category env settings, and retryable sync commands.

### Notes
- Step 3.2 keeps automated tests independent from a live Moodle instance. Grade pass-back is real but intentionally narrow: it requires an explicit Moodle grade target instead of guessing gradebook structure.
