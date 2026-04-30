# Phase 3.5C Audit/Admin Activity Viewer Spec

## Status

Approved for implementation by the 2026-04-30 Codex request. The user explicitly requested end-to-end implementation without repeated approval checkpoints, so this spec records the scoped design used for the slice.

## Context

Phase 3.1 established local Moodle and REST connectivity. Phase 3.2 added Moodle Lane A provisioning with outbox events and Moodle mappings. Phase 3.3 added Moodle Lane B LTI v1.3 tool-provider launch. Phase 3.4 added integration verification and Moodle engagement ingestion. Phase 3.5A added an admin-only Moodle Sync Monitoring Dashboard. Phase 3.5B added in-app notifications and controlled shell polish.

Phase 3.5C adds a read-only admin activity viewer. Later Phase 3.5 slices remain future scope:

- Step 3.5D Academic Calendar
- Step 3.5E Admin Reporting Dashboard
- Step 3.5F Student Document Management
- Step 3.5G Admissions

## Goal

Create a practical read-only admin activity/audit viewer backed by real SIS database records. Administrators can review important activity across user administration, enrollment and grade operations, Moodle sync, notifications, safe LTI activity, and system events.

## In Scope

- `AuditEvent` persistence model with category, action, severity, actor, target, sanitized metadata, and timestamp fields.
- Audit service helpers:
  - `record_audit_event(...)`
  - `sanitize_audit_metadata(...)`
- Admin-only read APIs:
  - `GET /api/v1/admin/activity`
  - `GET /api/v1/admin/activity/summary`
  - `GET /api/v1/admin/activity/<id>`
- Filters for category, severity, action, actor, search, date range, and bounded limit.
- Clean, low-risk audit hooks:
  - Moodle sync failed, processed, and retried events
  - notification read and read-all events
  - safe LTI launch session creation
  - admin user create/update/deactivate/password-reset-required actions
  - enrollment created/dropped actions through the existing academic service
  - grade officialisation through the existing academic service
- Optional local demo seed command: `python manage.py seed_audit_activity_demo`.
- Frontend implementation of `/admin/audit-log` as the real Step 3.5C viewer.
- Summary cards, filters, activity table, details panel, loading/error/empty states, and scope note.
- Documentation with exact commands to run and test the UI against the backend database.
- Backend, frontend, documentation, and changelog updates.

## Out Of Scope

- Step 3.5D academic calendar.
- Step 3.5E admin reporting dashboard.
- Step 3.5F document management.
- Step 3.5G admissions.
- AI co-pilot, AI audit review, at-risk scoring, or wellbeing workflows.
- Immutable external audit storage, SIEM export, or compliance archive integrations.
- Email, SMS, push, or external notification delivery.
- Edit or delete actions for audit records.
- Raw payload dumps, Moodle tokens, LTI private keys, raw JWTs, passwords, or sensitive values in persistence or API responses.
- A new frontend design system, chart libraries, stock photos, emoji icons, or decorative AI-style visuals.

## Backend Model

If no existing model matches the Step 3.5C contract, add `apps.audit.models.AuditEvent`.

Fields:

- `id`: UUID primary key
- `actor`: nullable FK to `accounts.User`
- `actor_username`: denormalized string
- `actor_role`: denormalized primary role
- `category`: one of `USER`, `STUDENT_RECORD`, `COURSE`, `ENROLLMENT`, `GRADE`, `MOODLE`, `NOTIFICATION`, `LTI`, `SYSTEM`, `AI`
- `action`: machine-readable action string
- `summary`: human-readable summary
- `target_type`: optional string
- `target_id`: optional string
- `severity`: one of `INFO`, `SUCCESS`, `WARNING`, `ERROR`
- `metadata`: sanitized JSON object
- `ip_address`: optional
- `user_agent`: optional
- `created_at`: timestamp

The model is append-only at the app/API layer. No public create, update, or delete APIs are exposed.

## Backend API

Use the existing `/api/v1/` convention and access-policy middleware.

- `GET /api/v1/admin/activity`
- `GET /api/v1/admin/activity/summary`
- `GET /api/v1/admin/activity/<uuid:event_id>`

All endpoints require an authenticated admin user. Students, advisors, and faculty receive 403. Unauthenticated clients receive 401.

### List Filters

- `category`
- `severity`
- `action`
- `actor`
- `search`
- `date_from`
- `date_to`
- `limit`

Invalid filters are ignored conservatively where appropriate. `limit` is bounded to avoid unbounded list responses.

### Response Shape

Activity items use camelCase fields:

- `id`
- `actor`
- `category`
- `action`
- `severity`
- `summary`
- `targetType`
- `targetId`
- `metadata`
- `createdAt`

The summary returns:

- `total`
- `errors`
- `warnings`
- `today`
- `byCategory`

## Secret Safety

Metadata is sanitized before persistence and again before serialization. The sanitizer redacts keys and text values containing common secret markers:

- `token`
- `password`
- `secret`
- `private_key`
- `jwt`
- `authorization`
- `wstoken`
- `access`
- `refresh`

Known configured values such as Moodle tokens and LTI key material are also redacted from text. JWT-like values are redacted by pattern.

## Frontend

Use the existing admin route:

- `/admin/audit-log`

Topbar title:

- `Audit Log`

Topbar subtitle:

- `Review administrative activity, sync events, notifications, and governed system actions.`

The page follows the existing Step 3.5A/3.5B design system: Tailwind tokens, `Card`, `Badge`, `Button`, `Input`, `Select`, `Table`, Heroicons, restrained neutral backgrounds, and no emojis.

Page structure:

- Summary cards:
  - Total Events
  - Errors
  - Warnings
  - Today
  - Moodle
  - User Activity
  - Notifications
- Main card:
  - title `Admin Activity Viewer`
  - subtitle `Read-only timeline of important SIS, Moodle, notification, and governance activity.`
  - category and severity dropdowns
  - action/search input
  - refresh button
  - activity table
- Details panel:
  - action
  - category
  - severity
  - actor
  - target
  - created time
  - sanitized metadata key-value list
- Empty, loading, and error states.
- Scope note explaining current limits and Step 3.5D next.

## Demo Data

Add `seed_audit_activity_demo` as an optional local command. It creates safe audit events for USER, MOODLE, NOTIFICATION, LTI, SYSTEM, and AI placeholder categories without requiring live Moodle and without storing secrets. The AI event is a placeholder category only; no AI feature is implemented.

## Testing Strategy

Backend tests cover:

- admin can list activity
- non-admin and unauthenticated access is denied
- admin can fetch summary
- filters by category, severity, action, actor/search, and date range
- detail endpoint returns safe metadata
- sanitizer redacts tokens, passwords, private keys, JWTs, `wstoken`, `access`, and `refresh`
- Moodle sync failure creates an audit event
- notification read creates an audit event
- API output does not expose Moodle token, LTI key material, or raw JWT-like strings

Frontend tests cover:

- `/admin/audit-log` renders the real activity viewer
- summary cards render
- filters render
- table renders audit events
- details panel renders sanitized metadata
- empty and error states render
- sidebar still contains Audit Log
- practical no-emoji assertion for audit page text

## Documentation

Document that Step 3.5C:

- implements the read-only Audit/Admin Activity Viewer
- is admin-only
- uses real backend API/database records
- includes optional local demo data
- does not implement Step 3.5D-3.5G
- does not implement AI audit review beyond a placeholder category
- leaves Step 3.5D Academic Calendar as the next planned slice
