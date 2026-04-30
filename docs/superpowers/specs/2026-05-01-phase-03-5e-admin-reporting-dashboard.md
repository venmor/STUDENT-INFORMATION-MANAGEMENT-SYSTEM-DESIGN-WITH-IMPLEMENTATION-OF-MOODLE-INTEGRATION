# Phase 3.5E Admin Reporting Dashboard Spec

## Status

Accepted for implementation on `feature/phase-03-5e-admin-reporting-dashboard`.

## Context

Step 3.5E follows the completed Phase 3.5A through 3.5D operational visibility slices:

- Step 3.5A: admin-only Moodle Sync monitoring at `/admin/moodle-sync`.
- Step 3.5B: in-app Notification Center at `/notifications`.
- Step 3.5C: admin-only Audit/Admin Activity Viewer at `/admin/audit-log`.
- Step 3.5D: role-aware Academic Calendar and Deadline Rules at `/calendar`.

The repository already has usable SIS records for students, courses, sections, enrollments, attendance, financial flags, grades, Moodle sync outbox events, Moodle mappings, Moodle engagement ingestion runs/snapshots, calendar events, notifications, and audit events. Step 3.5E must summarize those records. It must not create document management, admissions, AI, financial billing, external BI, or an at-risk scoring engine.

## Goals

1. Add an admin-only reporting API surface under `/api/v1/admin/reports/`.
2. Aggregate existing SIS, Moodle, calendar, notification, and audit data without creating new business workflows.
3. Add a practical admin dashboard at `/admin/reports` that supports institutional reporting workflows through summary cards, status chips, accessible chart-like bars, tables, filters, empty/error states, and next-action links.
4. Add focused backend and frontend tests for permissions, counts, calculations, secret safety, route protection, rendering, links, filters, empty states, and errors.
5. Update normal project docs and changelogs to mark Step 3.5E complete and Step 3.5F Student Document Management as the next planned slice.

## Non-Goals

- No Step 3.5F Student Document Management.
- No Step 3.5G Admissions.
- No AI co-pilot, AI audit review expansion, predictive analytics, or at-risk scoring engine.
- No financial billing module.
- No external BI tool integration.
- No heavy chart library.
- No fake hardcoded production data in the UI.
- No secrets, Moodle tokens, LTI keys, raw JWTs, passwords, private payloads, or unsafe metadata in API responses or CSV export.
- No stock photos, emoji icons, or decorative AI-looking gradients.

## Backend Design

Create `apps.reporting` with:

- `apps.reporting.services`: pure aggregation helpers over existing models.
- `apps.reporting.api.views`: admin-only GET views returning JSON plus one safe CSV export for capacity.
- `apps.reporting.api.urls`: routes under `/api/v1/admin/reports/`.
- `apps.reporting.management.commands.seed_reporting_demo`: optional local/demo command that reuses safe existing demo seeds and adds enough safe reporting records for Moodle, calendar, audit, and notifications where dependencies are simple.

No reporting database tables are required. This avoids schema churn and keeps reporting reversible.

### Endpoints

- `GET /api/v1/admin/reports/summary/`
- `GET /api/v1/admin/reports/enrollment/`
- `GET /api/v1/admin/reports/capacity/`
- `GET /api/v1/admin/reports/grades/`
- `GET /api/v1/admin/reports/moodle-sync/`
- `GET /api/v1/admin/reports/calendar/`
- `GET /api/v1/admin/reports/activity/`
- `GET /api/v1/admin/reports/capacity/export.csv`

All endpoints are admin-only. Unauthenticated users receive `401`; students, advisors, and faculty receive `403`.

### Filters

The JSON report endpoints accept these filters where relevant:

- `academic_year`
- `semester`
- `programme`
- `course`
- `status`

Filters are intentionally simple text filters because the existing frontend does not yet expose separate lookup APIs for report filter options.

### Aggregations

Summary includes:

- students: total, active, inactive, programme distribution
- enrollments: total, current-term, waitlisted-as-pending, enrolled-as-confirmed, dropped
- capacity: section total, near capacity, full or over capacity, average fill rate
- grades: draft, official, pending approval as `0` because only `DRAFT` and `OFFICIAL` exist, official completion rate
- Moodle: outbox pending/failed/processed counts, mappings, latest engagement run status
- calendar: upcoming deadlines, critical deadlines, next deadline
- activity: today's audit events and unread admin notifications

Enrollment, capacity, grades, Moodle, calendar, and activity report endpoints return more detailed table/list payloads for the UI.

Capacity status is derived from existing `CourseSection.max_capacity` and active enrolled enrollment counts:

- `Open`: below 80 percent fill
- `Near Capacity`: at least 80 percent and below 100 percent fill
- `Full`: exactly 100 percent fill
- `Over Capacity`: above 100 percent fill

Grade status is mapped only from existing `GradeStatus.DRAFT` and `GradeStatus.OFFICIAL`. `pendingApproval` is returned as `0` and documented as unavailable because no pending-approval grade state currently exists.

Operational risk indicators are simple counts based on existing data only: failed Moodle sync events, sections near/full/over capacity, grade completion gaps, low attendance flags, active financial flags, critical deadlines, and warning/error audit events. These are not a scoring engine.

### CSV Export

Implement capacity export only because it is straightforward and safe. The CSV includes course, section, term, faculty, capacity, enrolled count, remaining seats, fill percentage, and status. It must not include raw JSON metadata or secrets.

Record `ADMIN_REPORT_EXPORTED` audit events for capacity export using `AuditCategory.SYSTEM` and `AuditSeverity.INFO`. Do not log exported rows or report payloads.

## Frontend Design

Create:

- `frontend/src/types/reports.ts`
- `frontend/src/api/reports.ts`
- `frontend/src/hooks/useAdminReports.ts`
- `frontend/src/pages/admin/Reports.tsx`

Register `/admin/reports` as an admin-only route, add Reports to the admin sidebar, and add AppShell heading text:

- title: `Institution Reports`
- subtitle: `Monitor enrollment, capacity, grades, Moodle health, deadlines, and operational activity.`

The page uses existing Tailwind tokens, shared UI components, and Heroicons only.

### Page Layout

1. Quick action row: refresh, filters, optional capacity CSV export, links to Moodle Sync, Calendar, Audit Log.
2. Summary cards: Active Students, Current Enrollments, Sections Near Capacity, Official Grades, Moodle Sync Health, Upcoming Deadlines, Audit Events Today.
3. Operational health strip: text status chips for Moodle, grade completion, capacity, deadlines, and audit.
4. Report grid:
   - Students by Programme with text values and accessible horizontal bars.
   - Enrollment Status with counts and progress bars.
   - Section Capacity table.
   - Grade Submission Progress table.
   - Moodle Sync Health summary.
   - Upcoming Academic Deadlines list.
   - Operational Activity summary.
5. Empty state for no reporting data.
6. Error state for failed report loading.
7. Current Scope note clearly stating exclusions.

### Accessibility

- All filter controls have labels.
- Buttons and links have visible text or aria labels.
- Tables use proper header cells.
- Visual bars include text values and `aria-label` where appropriate.
- Status is communicated with text badges, not color alone.
- Wide tables scroll inside cards.
- Layout collapses to one column on small screens.
- No emoji characters are used in page text.

## Testing

Backend tests:

- Admin can access every report endpoint.
- Non-admins receive `403`.
- Unauthenticated users receive `401`.
- Summary counts match seeded records.
- Capacity report computes fill percentage, remaining seats, and status correctly.
- Grade report maps existing grade states correctly and keeps pending approval at zero.
- Moodle report returns outbox, mapping, latest ingestion, and recent failure data safely.
- Calendar report returns upcoming and critical deadlines.
- Activity report returns audit and notification counts.
- Capacity CSV export is admin-only, safe, and records an export audit event.
- Report outputs do not expose tokens, JWTs, keys, passwords, or unsafe metadata.

Frontend tests:

- `/admin/reports` route exists and is admin-only.
- Sidebar shows Reports for admins.
- Non-admins cannot access `/admin/reports`.
- Summary cards, operational health strip, filters, capacity table, grade progress table, Moodle link, calendar link, audit link, empty state, and error state render.
- Page text does not contain emoji characters.

## Documentation Updates

Update:

- `docs/phases/phase-03-moodle-integration/README.md`
- `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- `docs/project/modern-sis-setup-guide.md`
- `docs/project/SRS_Modern_SIS.md`
- `backend/README.md`
- `frontend/README.md`
- root `README.md`
- root `CHANGELOG.md`

Docs must state that Step 3.5E is implemented, summarizes existing SIS/Moodle/calendar/notification/audit data, is read-oriented with optional safe capacity CSV export, and does not implement Step 3.5F documents, Step 3.5G admissions, AI, at-risk scoring, financial billing, or external BI. Step 3.5F Student Document Management remains next.
