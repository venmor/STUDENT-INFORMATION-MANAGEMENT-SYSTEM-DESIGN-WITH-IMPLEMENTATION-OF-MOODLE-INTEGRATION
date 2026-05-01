# Phase 3.5F Student Document Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build secure, audit-logged, student-linked document management for institutional records without implementing admissions or document intelligence.

**Architecture:** Add a dedicated `apps.documents` Django app with model, validators, selectors, services, permissions, serializers, thin views, tests, and seed command. Add componentized React document features with route pages that compose reusable components and use TanStack Query hooks.

**Tech Stack:** Django 5, DRF, MySQL, local Django media storage, React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Heroicons, Vitest.

---

## Component Responsibility Map

### Backend Files

- `backend/apps/documents/models.py`: document choices and `StudentDocument` schema only.
- `backend/apps/documents/validators.py`: filename sanitization, file extension/content-type/size validation, checksum helper, upload path helper.
- `backend/apps/documents/permissions.py`: role and object-level access checks for admin, advisor, student, faculty, and unauthenticated users.
- `backend/apps/documents/selectors.py`: visible document querysets and filter application.
- `backend/apps/documents/services.py`: upload, update, approve, reject, archive, download permission, audit, notification, and summary/report aggregation.
- `backend/apps/documents/serializers.py`: request validation and camelCase response shaping.
- `backend/apps/documents/views.py`: thin API views that call selectors/services.
- `backend/apps/documents/urls.py`: route names registered with central RBAC.
- `backend/apps/documents/management/commands/seed_document_demo.py`: safe idempotent demo records and placeholder files.
- `backend/apps/documents/tests/`: model, validator, service, permission, API, download, notification, audit, summary, and seed command tests.
- `backend/sis_backend/settings.py`: install app, configure media root/url and max upload size.
- `backend/sis_backend/urls.py`: include document routes.
- `backend/apps/accounts/access.py`: register all document API route names.
- `backend/apps/audit/models.py`: add document audit category.
- `backend/apps/reporting/services.py`: include document counts in summary/activity indicators.
- `backend/apps/reporting/api/views.py` and `urls.py`: add document report endpoint.

### Frontend Files

- `frontend/src/types/documents.ts`: document response, request, filter, summary, and choice types.
- `frontend/src/api/documents.ts`: API request functions only, including safe Blob download.
- `frontend/src/hooks/useDocuments.ts`: TanStack Query hooks and mutations.
- `frontend/src/features/documents/components/DocumentSummaryCards.tsx`: reusable summary cards.
- `frontend/src/features/documents/components/DocumentFilters.tsx`: reusable labelled filters/search/date controls.
- `frontend/src/features/documents/components/DocumentTable.tsx`: reusable responsive admin/student table with permission-aware actions.
- `frontend/src/features/documents/components/DocumentDetailsPanel.tsx`: selected-document details and audit-safe metadata display.
- `frontend/src/features/documents/components/DocumentUploadDialog.tsx`: reusable upload form.
- `frontend/src/features/documents/components/DocumentReviewDialog.tsx`: approve/reject note flow.
- `frontend/src/features/documents/components/DocumentPrivacyNotice.tsx`: privacy and current-scope notes.
- `frontend/src/features/documents/utils/documentLabels.ts`: centralized type/status/visibility labels and badge tones.
- `frontend/src/features/documents/utils/documentFormatting.ts`: file size/date/download filename formatting.
- `frontend/src/pages/admin/Documents.tsx`: thin admin page composition.
- `frontend/src/pages/student/Documents.tsx`: thin student page composition.
- `frontend/src/router.tsx`, `Sidebar.tsx`, `AppShell.tsx`: route, navigation, and heading registration.
- `frontend/tests/unit/*documents*.test.tsx`: route, sidebar, page, component, empty/error/loading, permission, and accessibility basics.

### Reusable Pieces

- Document table, summary cards, filters, upload dialog, details panel, review dialog, badge helpers, and formatting helpers are shared between admin and student contexts.
- Backend selectors and permissions are reused by all document endpoints.
- Backend services centralize audit and notification behavior so lifecycle hooks are not duplicated in views.

### Intentionally Not Implemented In Step 3.5F

- Admissions/applicant intake and accepted-applicant conversion.
- OCR, AI document analysis, e-signatures, external cloud storage, permanent delete, email/SMS/push notifications.
- Advisor upload/review UI because existing relationships prove advisor read scope only.
- Faculty document access because no current requirement grants it.

## Implementation Tasks

### Task 1: Backend App Skeleton, Settings, and RBAC

- [ ] Add `apps.documents` package with `apps.py`, `__init__.py`, `admin.py`, `models.py`, `validators.py`, `permissions.py`, `selectors.py`, `services.py`, `serializers.py`, `views.py`, `urls.py`, management command directories, migrations directory, and tests directory.
- [ ] Add `apps.documents` to `INSTALLED_APPS`.
- [ ] Add `MEDIA_URL`, `MEDIA_ROOT`, and `STUDENT_DOCUMENT_MAX_UPLOAD_SIZE`.
- [ ] Add `media/` to `.gitignore`.
- [ ] Include `apps.documents.urls` under `/api/v1/`.
- [ ] Register route names in `PROTECTED_API_ROUTE_POLICIES`.
- [ ] Extend `AuditCategory` with `DOCUMENT`.
- [ ] Run `python manage.py makemigrations documents audit`.

### Task 2: Model and Validators

- [ ] Write failing tests for document model defaults, upload path safety, filename sanitization, valid files, invalid extension, invalid content type, empty file, and oversized file.
- [ ] Implement `StudentDocument`, choices, model clean/save sanitization, indexes, and model admin.
- [ ] Implement validator helpers and checksum helper.
- [ ] Run `pytest -q apps/documents/tests/test_validators.py apps/documents/tests/test_models.py`.

### Task 3: Permissions, Selectors, and Services

- [ ] Write failing tests for admin access, student own student-visible access, student admin-only denial, advisor assigned-advisee access, unassigned advisor denial, faculty denial, and lifecycle authorization.
- [ ] Implement object permission helpers in `permissions.py`.
- [ ] Implement visible querysets and filters in `selectors.py`.
- [ ] Implement upload/update/approve/reject/archive/download/summary/report services.
- [ ] Centralize audit metadata and notification creation in services.
- [ ] Run `pytest -q apps/documents/tests/test_permissions.py apps/documents/tests/test_services.py`.

### Task 4: APIs and Downloads

- [ ] Write failing API tests for list/detail/upload/update/download/approve/reject/archive/summary/student-specific/self endpoints and unauthorized access.
- [ ] Implement serializers with camelCase response fields and no raw path fields.
- [ ] Implement thin DRF views calling selectors/services.
- [ ] Implement secure `FileResponse` download with sanitized original filename.
- [ ] Run `pytest -q apps/documents/tests/test_documents_api.py`.

### Task 5: Reporting and Seed Command

- [ ] Write failing tests for document report counts and idempotent seed command with downloadable placeholder files.
- [ ] Add `/api/v1/admin/reports/documents/`.
- [ ] Extend admin reporting summary/activity with document counts.
- [ ] Implement `seed_document_demo`, calling existing `seed_demo_sis` when needed.
- [ ] Run `pytest -q apps/documents/tests/test_seed_document_demo_command.py apps/reporting/tests/`.

### Task 6: Frontend Types, API, Hooks, and Feature Components

- [ ] Add document types, API functions, and TanStack Query hooks.
- [ ] Add feature utilities for labels and formatting.
- [ ] Add reusable document summary cards, filters, table, details panel, upload dialog, review dialog, and privacy notice.
- [ ] Ensure all inputs are labelled and table/actions are keyboard accessible.
- [ ] Keep pages thin and avoid one oversized route component.

### Task 7: Frontend Routes, Pages, Navigation, and Tests

- [ ] Add `/admin/documents` and `/documents` routes.
- [ ] Add AppShell headings and sidebar links for admin/student only.
- [ ] Create admin and student document pages from reusable feature components.
- [ ] Add unit tests for route rendering, sidebar visibility, summary cards, filters, table rows, upload validation, action visibility, empty/error states, privacy note, and no emoji text.
- [ ] Run `npm run typecheck`, `npm run lint`, `npm run test`, and `npm run build`.

### Task 8: Documentation, Verification, and Git Workflow

- [ ] Update phase README/changelog, setup guide, SRS, backend README, frontend README, root README, root CHANGELOG, and OpenAPI contract.
- [ ] Run backend verification commands:
  - `python manage.py check`
  - `python manage.py makemigrations --check --dry-run`
  - `pytest -q apps/documents/tests/`
  - `pytest -q apps/reporting/tests/`
  - `pytest -q apps/calendar/tests/`
  - `pytest -q apps/audit/tests/`
  - `pytest -q apps/notifications/tests/`
  - `pytest -q apps/integration/tests/`
  - `ruff check .`
- [ ] Run frontend verification commands:
  - `npm run typecheck`
  - `npm run lint`
  - `npm run test`
  - `npm run build`
- [ ] Run `git diff --check`.
- [ ] Commit as `feat: add phase 3.5F student document management`.
- [ ] Merge to local `main`, push branch and main to GitHub, and update local main.

## Risks and Mitigations

- **Protected media in development:** Django media URLs are not used for protected document access. Downloads go through authenticated API views.
- **MIME spoofing:** Step 3.5F validates declared content type and extension but does not parse files. Production deployments should add malware scanning before accepting real institutional files.
- **Advisor scope:** Advisor access depends only on current `AdvisorAssignment`; no guessing is used.
- **Local storage:** Files live under `MEDIA_ROOT`, not git. External storage is future work because no abstraction exists yet.
- **Audit volume:** Download events are audited. If usage becomes high, retention and reporting indexes may need review.

## Test Coverage Targets

- Permission boundaries for admin, advisor, student, faculty, and anonymous clients.
- Invalid, oversized, empty, and unsupported files.
- Unauthorized downloads and no raw path leakage.
- Review and archive workflow.
- Audit event creation.
- Notification creation.
- Summary and reporting counts.
- Seed command idempotency and working placeholder files.
- Frontend loading, empty, error, and populated states.
- Labelled filters/buttons, text-bearing badges, and no color-only status.
