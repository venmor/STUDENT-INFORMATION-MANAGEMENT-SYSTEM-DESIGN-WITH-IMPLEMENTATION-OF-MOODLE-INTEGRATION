# Changelog

All notable changes to this repository should be documented in this file.

The format follows a simple `Keep a Changelog` style adapted for a documentation-first project baseline.

## [Unreleased]

### Added
- VS Code Web and GitHub fork buttons in the repository README for collaborators.
- Phase 2 documentation path under `docs/phases/phase-02-core-build/`.
- Phase 2 Step 2.1 backend bootstrap under `backend/`.
- `frontend/` and `infra/` placeholder directories to preserve the agreed repo structure.
- Phase 2 Step 2.2 authentication baseline with a custom Django user model, seeded primary-role catalog, capability flags, and JWT auth endpoints.
- A tracked `infra/.env.example` file so the backend environment template is version-controlled.
- Central API access-policy enforcement for Step 2.2, backed by route policies and Django system checks.
- Explicit bcrypt dependency and password-hash verification coverage for Step 2.2.
- Phase 2 Step 2.3 password complexity enforcement, user administration APIs, and access logging in the Django backend.
- Phase 2 Step 2.3 student, academics, and integration apps covering profiles, advising, courses, sections, enrollments, attendance, grades, transcripts, and Moodle-facing outbox events.
- Shared backend test utilities and coverage tooling for the Step 2.3 core-module slice.
- Phase 2 Step 2.3 alignment pass covering student-record deactivation, field-level student audit logging, explicit read-list audit events, and removal of the stale pre-middleware RBAC helper.
- Step 2.3 contract refresh so `docs/api/openapi.yaml` and `docs/diagrams/modern-sis-erd.md` match the implemented backend rather than future planned phases.
- Phase 2 Step 2.4 React frontend implementation with role-aware dashboards, protected routes, API wiring, and frontend verification tooling.
- Step 2.4 frontend-support backend additions for login `student_profile_id`, student registration-target section reads, and enrollment list reads.
- Phase 2 Step 2.5 CI workflows for backend quality, frontend quality, container validation, and separate Playwright browser verification.
- Backend and frontend Dockerfiles plus Nginx configuration for the Step 2.5 containerized runtime baseline.
- `infra/docker-compose.yml`, `infra/docker-compose.dev.yml`, and `infra/docker-compose.staging.yml` with later-phase placeholder services modelled as profile-gated Compose services.
- `infra/docker-compose.moodle.yml` and `infra/moodle.env.example` for the isolated Phase 3 Step 3.1 Moodle slice.
- `python manage.py verify_moodle_rest` for narrow local Moodle REST verification against `core_user_get_users`.
- Phase 3 documentation path under `docs/phases/phase-03-moodle-integration/`.
- The Phase 3 Step 3.2 Moodle Lane A sync baseline: retryable integration outbox metadata, Moodle user/course mapping models, `MoodleSyncService`, and `process_moodle_sync`.
- Mocked backend test coverage for Moodle provisioning, enrollment sync, grade pass-back foundations, and command-driven retry processing.
- Phase 3 Step 3.3 Moodle Lane B LTI v1.3 tool-provider baseline with JWKS, OIDC login, launch validation, DB-backed nonce/state replay protection, hashed launch sessions, and protected LTI context API.
- Usable LTI frontend pages for `/lti/tools/advising-dashboard` and `/lti/tools/registration`.
- Mocked backend test coverage for LTI JWKS, OIDC login, launch JWT validation, replay rejection, mapping behavior, and protected embedded tool access.
- Dedicated Phase 3 Step 3.3 LTI testing guide for Linux, Arch Linux, Windows with WSL2 or PowerShell, local `.env.local` setup, RSA keys, MySQL startup, backend and frontend verification, optional JWKS probing, optional live Moodle launch testing, expected results, and common fixes.
- Phase 3 Step 3.4 integration-verification and Moodle engagement analytics-ingestion foundation with `MoodleEngagementIngestionRun`, `MoodleEngagementSnapshot`, `ingest_moodle_engagement`, and `verify_phase_3_integrations`.
- Step 3.4 LTI advising roster engagement context plus a read-only frontend student-selection panel.
- Dedicated Phase 3 Step 3.4 test matrix covering Lane A, Lane B, analytics ETL, failure/retry paths, unmapped contexts, secret safety, mocked automation, and optional live Moodle verification.
- Phase 3.5A Moodle sync monitoring dashboard with admin-only backend APIs, `/admin/moodle-sync`, summary cards, integration readiness, outbox operations, Moodle mappings, engagement ingestion state, safe current-scope guidance, and failed/pending outbox retry through the existing processor.
- Backend and frontend tests for the Phase 3.5A dashboard, including admin-only access, non-admin denial, secret-safety checks, outbox filters, retry behavior, route registration, sidebar navigation, empty/error states, and no-emoji UI label coverage.
- Phase 3.5B in-app Notification Center with the `apps.notifications` backend app, user-scoped notification APIs, `/notifications`, topbar unread bell, filters, mark-read actions, and safe in-app notification rendering for all authenticated roles.
- Moodle sync failure notifications for admins plus enrollment-confirmed, grade-released, and approved advising-note notifications for students through clean existing service/view hooks.
- Controlled AppShell/sidebar/topbar polish for Step 3.5B, including grouped sidebar navigation, stronger active/focus states, sidebar account card, sidebar sign out, and removal of topbar sign out.
- Phase 3.5C Audit/Admin Activity Viewer with the `apps.audit` backend app, append-only `AuditEvent` records, admin-only audit APIs, `/admin/audit-log`, summary cards, filters, read-only table, sanitized details panel, and optional safe demo audit data.
- Audit hooks for Moodle sync failure/processed/retry events, notification read/read-all actions, safe LTI launch sessions, admin user changes, enrollment create/drop, and grade officialisation.
- Run/test documentation for Step 3.5C UI backed by the backend database, including Docker Compose, migration, admin, demo audit data, frontend hot reload, test, and teardown commands.
- Phase 3.5D Academic Calendar and Deadline Rules with the `apps.calendar` backend app, central `AcademicCalendarEvent` records, role-aware calendar APIs, `/calendar`, summary cards, month/list views, filters, deadline urgency labels, priority/source display, role-specific My Deadlines, and admin create/update/cancel actions.
- Safe academic calendar demo data and course-section deadline sync commands: `python manage.py seed_academic_calendar_demo` and `python manage.py sync_academic_calendar_from_sections`.
- Calendar audit hooks for create, update, cancel, and course-section sync activity, with optional admin-triggered in-app notifications for high-priority or critical events.
- Phase 3.5E Admin Reporting Dashboard with the `apps.reporting` backend app, admin-only reporting APIs under `/api/v1/admin/reports/`, `/admin/reports`, filters, summary cards, operational health indicators, accessible bar summaries, capacity and grade tables, Moodle/calendar/activity panels, workflow links, and safe capacity CSV export.
- Safe reporting demo data command `python manage.py seed_reporting_demo`, plus report-view/export audit hooks that avoid storing report payloads or secrets.
- Backend and frontend tests for Step 3.5E reporting permissions, counts, capacity calculations, grade status mapping, Moodle/calendar/activity aggregation, secret safety, route registration, sidebar navigation, filters, links, empty/error states, and UI rendering.
- Phase 3.5F Student Document Management with the `apps.documents` backend app, protected local media storage, document validation, role-scoped selectors/permissions/services, secure download APIs, `/admin/documents`, `/documents`, summary/workflow cards, reusable document feature components, upload/review/details dialogs, and privacy/scope notes.
- Document audit hooks for upload, update, download, approve, reject, and archive events; in-app notifications for supported student-visible upload/review workflows; and document reporting counts under the existing admin reporting surface.
- Safe document demo data command `python manage.py seed_document_demo`, plus backend and frontend tests for document permissions, invalid files, downloads, review/archive workflows, audit/notification hooks, seed data, route registration, sidebar navigation, labelled filters/forms, empty/error states, and no-emoji UI rendering.
- Phase 4.1 Unified Analytics Schema and Vector Store Foundation with `apps.analytics`, `apps.knowledge`, analytics ETL snapshots, institutional knowledge source/chunk ingestion, deterministic local embeddings, Qdrant/in-memory vector-store wrappers, admin-only APIs, and retrieval-only test commands.
- Safe Phase 4.1 demo commands: `python manage.py seed_analytics_demo`, `python manage.py run_analytics_etl`, `python manage.py seed_knowledge_demo`, `python manage.py ingest_knowledge_base`, and `python manage.py query_knowledge_base "What is the deadline to drop a course?"`.
- Admin-only `/admin/ai-foundation` UI with analytics readiness, knowledge base status, vector-store health, ingestion runs, retrieval-only testing, and explicit no-LLM/no-co-pilot scope guidance.
- Phase 4.2 Student Service Co-pilot with `apps.copilot`, student-owned chat sessions/messages, AI audit records, optional assistant-message feedback, source-grounded retrieval orchestration over Step 4.1 knowledge chunks, safe authenticated-student context, deterministic local provider, optional OpenAI-compatible provider configuration, and student APIs under `/api/v1/ai/copilot/`.
- Student `/student/copilot` chat UI with sidebar/dashboard navigation, accessible transcript, labelled composer, example prompts, thinking/error states, source panel, confidence badges, low-confidence disclaimer, and suggested workflow links.
- Safe Phase 4.2 demo commands: `python manage.py seed_copilot_demo` and `python manage.py test_copilot_query "What is the deadline to drop a course?"`.

- Phase 4.3 Staff Workflow Acceleration (Summarisation) with `apps.summarisation`, structured extraction via deterministic/OpenAI-compatible providers, `POST /api/v1/ai/summarise/` and `/approve/` endpoints, AI audit logging, advising note creation on approval, live advisor `AISummarisationPanel`, standalone `/admin/summarise` page, 5 demo advising scenarios, and full backend/frontend test coverage.

- Phase 5.1 At-Risk Student Insight Engine with `apps.atrisk`, 9 signal evaluators (attendance, academic standing, financial hold, grade decline, incomplete grades, Moodle inactivity, assignment misses, quiz failures, forum disengagement), weighted severity classification (HIGH/MEDIUM/LOW), deterministic explanation provider, advisor-only API endpoints (`GET /api/v1/advisor/at-risk/alerts`, `GET /api/v1/advisor/at-risk/history`, `POST .../acknowledge`), auto-close for resolved alerts, management commands (`run_at_risk_engine`, `seed_at_risk_demo`), AI audit logging with `AT_RISK_EVALUATION` action, and live frontend `AtRiskAlertQueue`/`AlertHistory` components.

### Changed
- Activated OpenAI-compatible co-pilot provider (`gpt-4o-mini`) for local development via `.env.local` configuration. Tests and CI remain on the deterministic provider. The API key is git-ignored.
- Updated `infra/moodle.env.example` with improved AI provider documentation and explicit default model value.
- Replaced the non-working README VS Code web link with the official `vscode.dev/github/<owner>/<repo>` format.
- Replaced the unreliable desktop `vscode://` badge with explicit desktop clone guidance.
- Corrected phase sequencing so Phase 1 remains documentation-only and implementation planning/work is classified under Phase 2.
- Reserved the active implementation slice for Step 2.1 only on `feat/phase-02-step-2-1-bootstrap`.
- Moved the active isolated implementation slice to `feat/phase-02-step-2-2-auth-rbac` for auth and RBAC delivery.
- Moved the active isolated implementation slice to `feat/phase-02-step-2-2-security-hardening` for the Step 2.2 security hardening pass.
- Moved the active isolated implementation slice to `feat/phase-02-step-2-3-core-modules` for the Step 2.3 core SIS backend modules.
- Reconciled the setup guide with the SRS by standardizing on Django's built-in bcrypt hasher and central API RBAC enforcement.
- Updated repository and phase documentation to reflect that `main` now carries the approved Step 2.2 baseline while Step 2.3 remains under isolated review.
- Narrowed the published API contract back to the real Step 2.3 backend surface by removing unimplemented AI and LTI endpoints from the OpenAPI document.
- Advanced the active implementation slice from Step 2.3 backend close-out to Step 2.4 frontend delivery.
- Updated phase and frontend documentation so Step 2.4 is recorded as complete and Step 2.5 is recorded as next.
- Expanded the tracked infra environment template and runbooks so the Step 2.5 CI and staging baseline is documented alongside the manual local runbook.
- Updated the repository and phase runbooks to record Step 2.5 as complete and Phase 3 Step 3.1 as the next implementation target.
- Updated the repository, backend, infra, and phase runbooks so Moodle can be started through a dedicated overlay without changing the default Phase 2 startup path.
- Tightened the shared Moodle placeholder services with bootstrap variables, a MariaDB health check, and persisted Moodle runtime storage.
- Corrected the Moodle overlay bootstrap guidance so local first-run `wwwroot` follows the incoming browser host and port instead of hardcoding an invalid local origin.
- Expanded the Moodle runbooks and backend env documentation for Step 3.2 with Lane A service functions, least-privilege capabilities, retry commands, role/category config, and grade pass-back limitations.
- Clarified the local testing credentials in the repository and Phase 3 runbooks so the seeded SIS demo accounts and the local Moodle bootstrap login are documented in one place.
- Documented a planned `Phase 3.5 — SIS Operational Visibility and Completion Layer` after Phase 3 Step 3.4 and before Phase 4.
- Updated Moodle registration runbooks with Step 3.3 LTI external-tool setup, key handling, and launch-test guidance. Step 3.4 has since been implemented, and Phase 3.5 remains future scope after Step 3.4.
- Linked the dedicated Step 3.3 testing guide from the repository, docs indexes, backend, frontend, infra, and Phase 3 documentation, and corrected the short root README external-tool target-link wording to point at `/lti/tools/*` instead of `/lti/launch`.
- Updated Moodle runbooks and docs indexes for Step 3.4 analytics ingestion, readiness verification, `core_enrol_get_enrolled_users`, and the new test matrix. Phase 3.5 remains future scope after Step 3.4.
- Updated Moodle integration documentation for Step 3.5A as implemented and Step 3.5B Notification Center as the next planned slice.
- Updated Moodle integration, setup, backend, frontend, and SRS documentation for Step 3.5B as implemented and Step 3.5C Audit/Admin Activity Viewer as the next planned slice.
- Updated Moodle integration, setup, backend, frontend, and SRS documentation for Step 3.5C as implemented and Step 3.5D Academic Calendar as the next planned slice.
- Updated Moodle integration, setup, backend, frontend, and SRS documentation for Step 3.5D as implemented and Step 3.5E Admin Reporting Dashboard as the next planned slice.
- Updated Moodle integration, setup, backend, frontend, and SRS documentation for Step 3.5E as implemented and Step 3.5F Student Document Management as the next planned slice.
- Updated project documentation to mark Step 3.5G Admissions / Applicant Intake as skipped optional/future scope and Phase 4 Step 4.1 as the active analytics/vector-store foundation.
- Updated repository, backend, frontend, setup-guide, SRS, and Phase 4 documentation to record Step 4.2 as the active student-facing co-pilot slice built on the Step 4.1 analytics and knowledge foundation.

### Notes
- Phase 2 Step 2.1 verification now includes a fresh `mysql:8` container-backed `manage.py check` and `manage.py migrate` run.
- Phase 2 Step 2.2 verification uses a temporary `mysql:8` container, the application database user for runtime checks, and a database user with test-schema creation rights for `pytest`.
- The Step 2.2 security hardening pass was re-verified with `manage.py check`, `manage.py migrate`, `pytest apps/accounts/tests -q`, and `ruff check backend`.
- Phase 2 Step 2.3 verification used temporary `mysql:8` on `127.0.0.1:3313`, `python -m compileall apps sis_backend`, `manage.py check`, `manage.py migrate`, `pytest -q --cov=apps --cov-report=term-missing`, and `ruff check backend`, yielding 35 passing tests and 91% total backend coverage.
- The Step 2.3 alignment pass adds targeted backend verification for student deactivation, field-level audit diffs, and route-policy coverage before Step 2.4.
- Phase 2 Step 2.4 verification used a disposable `mysql:8` database for backend checks plus `npm test`, `npm run lint`, and `npm run build` for the frontend.
- Phase 2 Step 2.5 verification used `workflow-yaml-ok`, backend quality checks with 46 passing tests and 93.58% backend coverage, frontend quality checks with 14 unit/component tests and 9 Playwright tests, Docker image builds, Compose config validation, and a staging proxy smoke test on `127.0.0.1:8088`.
- Phase 3 Step 3.1 intentionally stops at manual Moodle admin setup and local REST connectivity proof. The final close-out was re-verified on the documented Compose overlay at `http://127.0.0.1:8090`, and provisioning sync, LTI, and retry orchestration remain later steps.
- Phase 3 Step 3.2 keeps automated verification independent from live Moodle. Grade pass-back is intentionally narrow and requires explicit Moodle grade-target metadata instead of guessed gradebook writes.
- Phase 3 Step 3.3 keeps automated verification independent from live Moodle by signing mocked LTI launch JWTs with generated test keys. Registration is read-oriented in this slice; mutating registration actions remain governed by the normal SIS enrollment engine and should be hardened in Step 3.4 before exposing iframe writes.
- Phase 3 Step 3.4 keeps automated verification independent from live Moodle. It ingests Moodle access snapshots only; assignment, quiz, and forum metrics remain nullable until a later analytics expansion, and no at-risk scoring or Phase 3.5 dashboard is implemented.
- Phase 3.5A keeps automated verification independent from live Moodle and does not implement notifications, academic calendar, admin reporting, document management, admissions, AI, at-risk scoring, or wellbeing.
- Phase 3.5B implements in-app notifications only. It does not implement email, SMS, push delivery, audit/admin activity viewer, academic calendar, admin reporting, document management, admissions, AI, at-risk scoring, or wellbeing.
- Phase 3.5C implements an admin-only, read-only audit viewer over real database records. It does not implement Step 3.5D-3.5G, AI audit review beyond a placeholder category, external compliance export, SIEM integration, reports, document management, admissions, at-risk scoring, or wellbeing.
- Phase 3.5D implements central academic calendar and deadline rules only. It does not implement Step 3.5E-3.5G, AI co-pilot, at-risk scoring, wellbeing workflows, Google Calendar or Outlook sync, recurring rules, personal reminders, timetable conflict detection, email/SMS/push reminders, or Moodle assignment deadline import.
- Phase 3.5E implements read-only admin institutional reporting plus safe capacity CSV export only. It does not implement Step 3.5F document management, Step 3.5G admissions, AI, at-risk scoring, financial billing, external BI, or PDF generation.
- Phase 3.5F implements secure student-linked document management only. It does not implement Step 3.5G admissions/applicant intake, OCR, AI document analysis, e-signatures, permanent deletion, external cloud storage, email/SMS/push notifications, or faculty document access.
- Phase 4.1 implements analytics and vector-store foundations only. It does not implement `/ai/copilot/query`, student co-pilot UI, staff summarisation, at-risk scoring, wellbeing workflows, admissions, paid-provider calls by default, or private student document embedding.
- Phase 4.2 implements student-facing source-grounded question answering only. It does not implement Step 4.3 staff summarisation, at-risk scoring, wellbeing workflows, admissions/applicant intake, grade prediction, OCR, AI document analysis, automated enrollment/drop actions, SIS record mutation, or private student document embedding/exposure.
- Phase 5.1 implements the at-risk insight engine with deterministic provider only. It does not implement email/SMS/push alert delivery, Celery periodic scheduling (provides management command only), AI-generated intervention recommendations, wellbeing referral workflows, student self-service risk dashboard, or predictive analytics beyond threshold-based signal detection.

## [0.1.0] - 2026-04-12

### Added
- Repository-level README with project purpose, baseline stack, and document index.
- Mermaid-based architecture diagram pack covering context, components, sequences, activities, states, and deployment.
- Phase documentation structure under `docs/phases/`.
- Version-control guidance under `docs/process/version-control.md`.
- Release checklist and frozen-deliverables tracking for Phase 1.

### Changed
- Reorganized documentation assets into a clearer structure under `docs/`.
- Consolidated rendered diagram outputs under `docs/diagrams/rendered/`.
- Moved source Word documents into `docs/archive/source-docx/`.

### Removed
- None.
