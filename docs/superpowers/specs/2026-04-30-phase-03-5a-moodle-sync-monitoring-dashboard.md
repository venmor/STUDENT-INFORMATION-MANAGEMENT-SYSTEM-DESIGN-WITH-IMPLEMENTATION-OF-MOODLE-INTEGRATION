# Phase 3.5A Moodle Sync Monitoring Dashboard Spec

## Status

Approved for implementation by the 2026-04-30 Codex request. The user explicitly requested end-to-end implementation without repeated approval checkpoints, so this spec records the scoped design used for the slice.

## Context

Phase 3.1 established local Moodle and REST connectivity. Phase 3.2 added Moodle Lane A provisioning with outbox events, retry processing, and Moodle user/course mappings. Phase 3.3 added Moodle Lane B LTI v1.3 tool-provider launch. Phase 3.4 added the integration-verification gate and Moodle engagement ingestion foundation.

Phase 3.5 begins with Step 3.5A only: an admin-only Moodle Sync Monitoring Dashboard. Later Phase 3.5 slices remain future scope:

- Step 3.5B Notification Center
- Step 3.5C Audit/Admin Activity Viewer
- Step 3.5D Academic Calendar
- Step 3.5E Admin Reporting Dashboard
- Step 3.5F Document Management
- Step 3.5G Admissions

## Goal

Create a professional admin-only dashboard that monitors and operates the existing Moodle integration state without adding new integration behaviors beyond retrying failed or pending outbox events through the existing Step 3.2 processor.

## In Scope

- Admin-only backend monitoring APIs under the existing API prefix.
- Summary counts for outbox statuses, retryable events, user maps, course maps, latest engagement ingestion status, and safe readiness status.
- Outbox event list with status/type/search filters and safe payload summaries.
- Retry endpoint for failed and pending outbox events using `process_outbox_event`.
- Read-only lists for Moodle user mappings and course mappings.
- Read-only lists for Moodle engagement ingestion runs and recent snapshots.
- Frontend route `/admin/moodle-sync`.
- Admin sidebar item `Moodle Sync` after `Courses` and before `Audit Log`.
- Page sections:
  - Header summary strip
  - Integration health panel
  - Outbox event operations panel
  - Moodle mappings panel
  - Engagement ingestion panel
  - Safe limitations/help panel
- Mocked backend and frontend tests; live Moodle is not required for automated tests.
- Documentation and changelog updates.

## Out Of Scope

- Notifications, notification preferences, or message delivery.
- Audit/admin activity viewer.
- Academic calendar.
- Admin reporting dashboard or BI dashboard.
- Document management.
- Admissions.
- AI, at-risk scoring, wellbeing, or co-pilot flows.
- Moodle grade-target editing.
- Running engagement ingestion from the UI.
- New Moodle sync algorithms.
- Displaying Moodle tokens, LTI private keys, raw launch tokens, raw JWTs, or full unsafe payload dumps.
- Requiring live Moodle for normal tests.

## Backend API

Use the existing `/api/v1/` convention and access-policy middleware.

- `GET /api/v1/integration/moodle/summary`
- `GET /api/v1/integration/moodle/outbox-events`
- `POST /api/v1/integration/moodle/outbox-events/<id>/retry`
- `GET /api/v1/integration/moodle/user-maps`
- `GET /api/v1/integration/moodle/course-maps`
- `GET /api/v1/integration/moodle/engagement-runs`
- `GET /api/v1/integration/moodle/engagement-snapshots`

All endpoints are admin-only. Non-admin roles and unauthenticated requests must be denied by the existing policy layer.

### Retry Behavior

The retry endpoint accepts failed and pending events only. It calls the existing `process_outbox_event` function and returns the updated safe event representation. Processed events are rejected with a safe client error. Retry failures return a safe error payload without tokens, private keys, stack traces, or raw request secrets.

### Secret Safety

The summary reports configuration presence only:

- `moodleRestConfig`: `present` or `missing`
- `ltiConfig`: `present` or `missing`

No endpoint returns Moodle service tokens, LTI private key material, raw launch tokens, raw JWTs, or raw full outbox payloads.

## Frontend

The frontend follows the existing admin shell, Tailwind tokens, `Card` styling, TanStack Query/Axios pattern, and Heroicons. It does not introduce a new visual system.

Route:

- `/admin/moodle-sync`

Exact page title:

- `Moodle Sync`

Exact page subtitle:

- `Monitor provisioning, retries, mappings, and Moodle engagement ingestion.`

The dashboard is monitoring plus retry only. It does not add edit forms, reporting charts, notifications, or ingestion-run controls.

## Data Presentation

Outbox rows expose only safe operational fields:

- event type
- event id
- related record summary
- status
- attempts
- last attempt timestamp
- safe truncated last error
- created timestamp
- retry/process/completed action state

Mapping and engagement tables show linkage and operational timestamps. Nullable assignment, quiz, and forum metrics are represented honestly as not collected by Step 3.4 when relevant.

## Testing Strategy

Backend tests cover:

- admin summary access and count correctness
- non-admin and unauthenticated denial
- secret safety
- outbox filtering and safe payload summaries
- retry success, processed-event rejection, and retry failure safety
- map, run, and snapshot list endpoints
- denial across all monitoring endpoints for non-admin users

Frontend tests cover:

- route registration
- admin sidebar navigation
- summary cards
- outbox table and retry button
- mappings section
- engagement ingestion section
- empty states
- loading/error states
- practical no-emoji label check

## Rollback

This slice is additive. Rollback removes the new integration API module, frontend route/page/hooks/types, related tests, and docs. It does not require Moodle schema or runtime changes because it reuses existing Step 3.2 and Step 3.4 data.
