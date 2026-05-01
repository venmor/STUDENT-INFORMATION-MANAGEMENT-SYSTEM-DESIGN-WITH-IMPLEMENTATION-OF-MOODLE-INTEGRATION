# Phase 3.5F Student Document Management Spec

## Status

Accepted for implementation in this slice.

## Context

Phase 3.5F follows the completed Phase 3.5E Admin Reporting Dashboard. The existing SIS already has:

- `StudentProfile` as the authoritative student record model.
- `AdvisorAssignment` for current advisor-to-student scope.
- central role codes on `accounts.User.primary_role`.
- named route-policy RBAC middleware.
- `apps.audit` with append-only `AuditEvent` and sanitized metadata.
- `apps.notifications` with in-app user notifications and admin fan-out helpers.
- `apps.reporting` with admin-only read-only reporting APIs.
- React, Vite, Tailwind, TanStack Query, Heroicons, and shared UI components.

The backend does not currently have a reusable external storage abstraction. Step 3.5F will therefore use Django local media storage through a protected download API. Files must be stored outside source control, and the API must never expose raw file-system paths.

## Goals

- Add secure student-linked documents for institutional records.
- Allow admins to upload, classify, review, reject, approve, archive, view, and download documents for any student.
- Allow students to view/download only their own `STUDENT_VISIBLE` documents.
- Allow students to upload their own supporting documents for review.
- Allow advisors to view/download assigned advisee documents only when visibility is `ADMIN_ADVISOR` or `STUDENT_VISIBLE`.
- Deny faculty by default.
- Audit upload, update, download, approve, reject, and archive events.
- Create useful in-app notifications where the existing notification service supports it.
- Add admin reporting counts for document review workload.
- Provide polished admin and student UIs using existing design system components.

## Non-Goals

- Do not implement Step 3.5G Admissions or applicant intake.
- Do not implement OCR, AI document analysis, e-signatures, permanent deletion, or external storage integrations.
- Do not expose document raw file paths, private media URLs, file contents in audit metadata, secrets, or raw request payloads.
- Do not create fake production data. Demo seeding must create safe local placeholder files only.

## Backend Design

Create `apps.documents` with service, selector, validator, permission, serializer, and view layers.

### Model

`StudentDocument` stores:

- UUID primary key.
- FK to `StudentProfile`.
- nullable FK to uploader `User`.
- document type choice: `NRC_ID`, `ADMISSION_LETTER`, `TRANSCRIPT`, `APPEAL_LETTER`, `CLEARANCE_FORM`, `MEDICAL_SUPPORT`, `OTHER`.
- title, description, protected local `FileField`.
- original filename, content type, file size, optional SHA-256 checksum.
- visibility choice: `ADMIN_ONLY`, `ADMIN_ADVISOR`, `STUDENT_VISIBLE`.
- status choice: `PENDING_REVIEW`, `APPROVED`, `REJECTED`, `ARCHIVED`.
- reviewed-by user, reviewed-at, review note.
- sanitized JSON metadata.
- created and updated timestamps.

No delete API is provided. Archiving is the lifecycle exit for Step 3.5F.

### Validation

Validation is centralized in `apps.documents.validators`:

- Allowed extensions: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.doc`, `.docx`.
- Allowed content types: `application/pdf`, `image/jpeg`, `image/png`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.
- Max file size defaults to 10 MB through `STUDENT_DOCUMENT_MAX_UPLOAD_SIZE`.
- Empty files are rejected.
- Original filenames are sanitized for display/download only and are not used as trusted paths.
- Metadata is sanitized through existing audit metadata sanitization.

### Access Rules

- Admin: list, view, download, upload, update metadata, approve, reject, and archive all documents.
- Advisor: list, view, and download assigned advisee documents if visibility is `ADMIN_ADVISOR` or `STUDENT_VISIBLE`; cannot upload, review, reject, or archive in Step 3.5F.
- Student: list, view, and download own `STUDENT_VISIBLE` documents; can upload own supporting documents, forced to `STUDENT_VISIBLE` and `PENDING_REVIEW`; cannot review or archive.
- Faculty: denied by default.
- Unauthenticated: denied by middleware.

Advisor access is implemented because `AdvisorAssignment` exists and is already used by student profile access. If that relationship is absent for a student, advisor access is denied.

### APIs

Use existing API style under `/api/v1`:

- `GET /documents`
- `POST /documents`
- `GET /documents/summary`
- `GET /documents/<id>`
- `PATCH /documents/<id>`
- `GET /documents/<id>/download`
- `POST /documents/<id>/approve`
- `POST /documents/<id>/reject`
- `POST /documents/<id>/archive`
- `GET /students/<student_id>/documents`
- `POST /students/<student_id>/documents`
- `GET /me/documents`
- `POST /me/documents`
- `GET /admin/reports/documents/`

The canonical list/create endpoints are `/documents`. Student-specific and self endpoints are thin convenience routes over the same services/selectors.

### Audit

`apps.documents.services` writes these audit actions using `record_audit_event_safely`:

- `STUDENT_DOCUMENT_UPLOADED`
- `STUDENT_DOCUMENT_DOWNLOADED`
- `STUDENT_DOCUMENT_UPDATED`
- `STUDENT_DOCUMENT_APPROVED`
- `STUDENT_DOCUMENT_REJECTED`
- `STUDENT_DOCUMENT_ARCHIVED`

Metadata includes document ID, student ID, document type, visibility, status, original filename, file size, and content type. It does not include file content, storage path, secrets, or raw request payloads.

### Notifications

Use the existing in-app notification service only:

- Admin upload of a `STUDENT_VISIBLE` document notifies the student.
- Student upload notifies active admins that a document awaits review.
- Approval or rejection notifies the student when the document is student-visible or was uploaded by that student.

No email, SMS, push, or notification-preference system is added.

### Reporting

Add a small admin-only document reporting endpoint and extend the existing admin reporting summary/activity indicators only with simple document counts:

- total documents.
- pending reviews.
- rejected documents.
- recent uploads.

This avoids changing reporting into a new BI surface.

### Demo Seed

`python manage.py seed_document_demo` creates safe placeholder PDF files under `MEDIA_ROOT/student_documents/` and idempotent document records for existing demo students. If demo users/students do not exist, it calls the existing `seed_demo_sis` command first. It is safe to rerun and does not create secrets.

## Frontend Design

The frontend will be componentized under `frontend/src/features/documents/`:

- summary cards.
- filters.
- reusable table.
- details panel.
- upload dialog.
- review dialog.
- privacy notice.
- label and formatting utilities.

Route pages stay thin:

- `frontend/src/pages/admin/Documents.tsx`
- `frontend/src/pages/student/Documents.tsx`

### Admin Page

Route: `/admin/documents`.

Sections:

- Summary cards: total, pending review, approved, rejected, archived, student visible, recent uploads.
- Workflow health strip: review queue, visibility posture, recent activity, storage mode.
- Document repository card with filters, search, upload, refresh.
- Responsive table with student, document, type, visibility, status, uploaded by, date, file, actions.
- Upload dialog.
- Review dialog for approve/reject notes.
- Details panel with audit-safe metadata and download action.
- Empty, loading, and error states.
- Current scope note.
- Privacy note: "Documents are access-controlled and audit logged."

### Student Page

Route: `/documents`.

Sections:

- Summary cards: shared documents, pending review, approved, rejected.
- My Documents card with student-visible records.
- Upload supporting document button because backend supports safe student uploads.
- Responsive document table.
- Details panel.
- Empty, loading, and error states.
- Current scope and privacy notes.

### Navigation

- Admin sidebar adds `Documents` under Academic Operations using `DocumentTextIcon`.
- Student sidebar adds `Documents` under Student using `DocumentTextIcon`.
- Advisor link is not shown in Step 3.5F because there is no dedicated advisor documents route.
- Faculty link is not shown.

## Accessibility and UX Requirements

- Every input has a visible label.
- File input is keyboard accessible, exposes allowed types and max size, and shows selected filename.
- Dialogs use the existing Radix-backed `Modal`, including focus management and keyboard close.
- Tables have headers and horizontal scroll on small screens.
- Badges include text labels; status is not communicated by color alone.
- Buttons use visible text or an aria-label.
- Errors are shown near fields where practical.
- Pending review records are visually and textually easy to find.
- Archived documents are muted without hiding their state.

## SRS Requirement Mapping

### Functional Requirements Addressed

- `FR-DOC-001`: secure student-linked document records with type, file reference, uploader, visibility, status, timestamps, role-based access, and audit events.
- `FR-STU-002`: advisor document reads are scoped to assigned advisees using the existing advisor relationship.
- `FR-STU-007`: document reads/downloads and lifecycle events are audit logged where Step 3.5F adds document workflows.
- `FR-OPS-002`: in-app notifications are used for document workflow events where the existing notification service supports them.
- `FR-OPS-003`: document audit events feed the admin activity viewer.
- `FR-OPS-005`: document review counts are added to admin operational reporting.

### Non-Functional Requirements Addressed

- `NFR-SEC-001` and `NFR-SEC-005`: all APIs require JWT authentication and route-policy RBAC.
- `NFR-SEC-006`: Django ORM is used for all document queries.
- `NFR-SEC-009`: no secrets are stored in document metadata or seed data.
- `NFR-PRI-001` and `NFR-PRI-002`: document metadata is limited to fields required by the workflow.
- `NFR-MNT-001` and `NFR-MNT-002`: documents are a separate Django app with versioned migrations.
- `NFR-MNT-003`: the API contract is updated.
- `NFR-USE-002`, `NFR-USE-003`, `NFR-USE-004`: responsive UI, visible validation, and plain-language errors are implemented.
- `NFR-ACC-001`, `NFR-ACC-002`, `NFR-ACC-003`: labelled fields, keyboard-operable dialogs/actions, focus-visible styles, semantic tables, and accessible error text are implemented.

### Security and Privacy Requirements Addressed

- Protected download endpoint checks permission before streaming files.
- Raw file paths and public media URLs are not returned by APIs.
- Allowed file type and max-size validation run before save.
- Metadata and notifications are sanitized.
- Audit records exclude file contents, file paths, secrets, and raw request payloads.

### Accessibility and Usability Requirements Addressed

- Admin and student workflows use summary cards, health strip, table actions, details panel, review dialog, empty/error states, and privacy notes.
- Status labels use text-bearing badges and table values, not color-only signals.
- Upload and review flows include labelled controls and inline errors.

### Deferred Requirements and Why

- Step 3.5G Admissions/applicant intake is deferred because applicant records and conversion workflows are optional/future scope.
- OCR, AI document analysis, and e-signatures are deferred because they are explicit non-goals and would introduce new risk and dependencies.
- External object storage is deferred because no storage abstraction exists in the repo.
- Advisor upload/review is deferred because existing requirements only prove assigned-student read scope, not advisor document-review authority.
- Permanent deletion is deferred to protect auditability and avoid unsafe destructive workflows.
