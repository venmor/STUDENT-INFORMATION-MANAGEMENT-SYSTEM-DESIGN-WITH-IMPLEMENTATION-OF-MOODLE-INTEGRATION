# Phase 3.5B Notification Center Spec

## Status

Approved for implementation by the 2026-04-30 Codex request. The user explicitly requested end-to-end implementation without repeated approval checkpoints, so this spec records the scoped design used for the slice.

## Context

Phase 3.1 established local Moodle and REST connectivity. Phase 3.2 added Moodle Lane A provisioning with outbox events and Moodle mappings. Phase 3.3 added Moodle Lane B LTI v1.3 tool-provider launch. Phase 3.4 added integration verification and Moodle engagement ingestion. Phase 3.5A added an admin-only Moodle Sync Monitoring Dashboard.

Phase 3.5B adds a role-based in-app Notification Center and the controlled AppShell/sidebar/topbar polish needed to make notifications discoverable. Later Phase 3.5 slices remain future scope:

- Step 3.5C Audit/Admin Activity Viewer
- Step 3.5D Academic Calendar
- Step 3.5E Admin Reporting Dashboard
- Step 3.5F Document Management
- Step 3.5G Admissions

## Goal

Create an authenticated in-app notification foundation for admins, students, advisors, and faculty. Notifications are stored in the SIS, shown in the topbar notification bell, and reviewed on a dedicated `/notifications` page.

## In Scope

- Notification model with recipient, category, severity, title, message, optional action, read state, source reference, sanitized metadata, and timestamps.
- In-app notification creation service helpers:
  - create one notification for a user
  - notify active admins
  - create safe Moodle sync failure notifications
- Authenticated notification APIs under `/api/v1/notifications`.
- User-scoped notification lists, summary, mark-one-read, and mark-all-read actions.
- Current-user-only authorization for all notification APIs.
- Moodle sync failure notifications for admins when Step 3.2 outbox processing fails.
- Student grade-release notifications when an existing grade is officialised.
- Student enrollment-confirmed notifications when an existing enrollment service creates an enrolled record.
- Student advising-note notifications when an existing advising note is approved.
- Frontend route `/notifications` for all authenticated primary roles.
- Topbar notification bell with unread count.
- Notification Center page with summary cards, filters, read actions, loading/error/empty states, and safe action links.
- Controlled AppShell/sidebar/topbar polish:
  - grouped sidebar navigation
  - clearer sidebar active/hover/focus state
  - sign out moved to the sidebar bottom
  - compact account card with password link
  - topbar command-bar spacing and notification bell
  - mobile navigation kept functional
- Backend, frontend, documentation, and changelog updates.

## Out Of Scope

- Email, SMS, push, webhook, or external message delivery.
- Notification preferences, templates, delivery channels, digests, or scheduling.
- Celery or background workers unless already required by existing patterns.
- Admin-wide notification management UI.
- Step 3.5C audit/admin activity viewer.
- Step 3.5D academic calendar.
- Step 3.5E admin reporting dashboard.
- Step 3.5F document management.
- Step 3.5G admissions.
- AI co-pilot, at-risk scoring, wellbeing workflows, or Phase 4 features.
- Exposing Moodle tokens, LTI keys, raw JWTs, private key material, or unsafe metadata.
- A new design system, stock photos, emoji icons, or decorative AI-style visuals.

## Backend API

Use the existing `/api/v1/` convention and access-policy middleware.

- `GET /api/v1/notifications`
- `GET /api/v1/notifications/summary`
- `POST /api/v1/notifications/<id>/read`
- `POST /api/v1/notifications/read-all`

All endpoints require authentication. Users only see and mutate their own notifications. Admins also see only their own notifications in this slice.

### List Filters

- `status=all|unread|read`
- `category=ACADEMIC|MOODLE|GRADES|ENROLLMENT|ADVISING|SYSTEM`
- `severity=INFO|SUCCESS|WARNING|ERROR`
- `limit`

Invalid filters should be ignored conservatively or rejected safely without exposing internals.

### Response Shape

Notification items use camelCase fields:

- `id`
- `category`
- `severity`
- `title`
- `message`
- `actionLabel`
- `actionUrl`
- `isRead`
- `readAt`
- `createdAt`
- `sourceType`
- `sourceId`

The summary returns:

- `unreadCount`
- `latest`
- `byCategory`

## Notification Events

### Moodle Sync Failure

When `process_outbox_event` fails or a retry leaves an outbox event failed, create an admin notification:

- Category: `MOODLE`
- Severity: `ERROR`
- Title: `Moodle sync failed`
- Action label: `Open Moodle Sync`
- Action URL: `/admin/moodle-sync`
- Source: `IntegrationOutboxEvent`

The message must include only the event type and a safe error summary. It must not include tokens, key material, raw JWTs, raw payload dumps, stack traces, or private Moodle details.

### Grade Released

When the existing grade service officialises a grade, create a student notification:

- Category: `GRADES`
- Severity: `SUCCESS`
- Title: `Grade released`
- Action label: `View grades`
- Action URL: `/student/grades`
- Source: `GradeRecord`

### Enrollment Confirmed

When the existing enrollment service creates an `ENROLLED` record, create a student notification:

- Category: `ENROLLMENT`
- Severity: `SUCCESS`
- Title: `Enrollment confirmed`
- Action label: `View courses`
- Action URL: `/student/courses`
- Source: `Enrollment`

Waitlist records are not "confirmed" and should not receive this notification.

### Advising Note Available

When the existing advising-note approval endpoint approves a note, create a student notification:

- Category: `ADVISING`
- Severity: `INFO`
- Title: `Advising note available`
- Action label: `Review advising notes`
- Action URL: `/student`
- Source: `AdvisingNote`

The notification must not include note text.

## Frontend

The frontend follows the existing shell, Tailwind tokens, `Card` styling, TanStack Query/Axios pattern, and Heroicons. It does not introduce a new visual system.

Route:

- `/notifications`

Exact page title:

- `Notifications`

Exact page subtitle:

- `Review academic, Moodle, grades, enrollment, advising, and system updates.`

The Notification Center includes:

- summary cards for Unread, Moodle, Grades, Enrollment, Advising, and System
- filters for status, category, and severity
- `Mark all as read` action
- notification list with category/severity badges, created time, unread state, optional action link, and mark-read button
- loading, error, and empty states

## Layout Polish

Sidebar changes are intentionally constrained:

- group navigation by role-specific section labels
- preserve existing routes and route order
- keep Moodle Sync after Courses and before Audit Log for admins
- improve active, hover, and focus-visible states
- move sign out from topbar to sidebar bottom
- show account name, role, and password link in the sidebar bottom card

Topbar changes are intentionally constrained:

- keep page title and subtitle
- add a Heroicons notification bell linked to `/notifications`
- show unread count badge
- keep account summary chip
- remove sign out from the topbar
- do not add fake global search or invented term state

## Secret Safety

Notification metadata and messages are sanitized before persistence. The implementation must redact common secret keys and known configured values such as Moodle tokens and LTI key material. API responses must not include notification metadata in this slice.

## Testing Strategy

Backend tests cover:

- service creation for a user
- list current user's notifications only
- denial for another user's notification mutation
- summary unread count, latest notifications, and category counts
- status/category/severity filters
- mark-one-read and mark-all-read
- Moodle sync failure creates admin notifications
- enrollment, grade, and approved advising note hooks create safe student notifications
- payloads do not expose Moodle tokens, LTI private keys, or raw JWT-like metadata
- unauthenticated requests rejected

Frontend tests cover:

- `/notifications` route registration
- summary cards and Notification Center rendering
- out-of-data empty state
- loading/error states
- failed/error-style notification and read actions
- sidebar grouped section labels
- Moodle Sync admin order remains stable
- visible active route marker/class
- sign out appears in sidebar and not topbar
- topbar notification bell unread count
- practical no-emoji text check

## Rollback

This slice is additive. Rollback removes the notifications app, notification API routes and policies, event-hook calls, frontend notification route/page/hooks/types, layout polish changes, tests, and docs. The only database rollback is the notifications table migration.
