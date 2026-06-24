# Modern SIS Explained

This document explains the system in human terms first, then connects each feature back to the code. It is meant for contributors, supervisors, reviewers, and future developers who need to understand what the AI-assisted implementation produced.

For a folder-by-folder technical onboarding, use [CODEBASE_ONBOARDING.md](CODEBASE_ONBOARDING.md). For project purpose and run commands, use [README.md](../README.md).

## The Short Version

Modern SIS is the source of truth for academic operations. It stores users, student records, courses, enrollments, grades, documents, reports, audit events, AI interactions, at-risk alerts, and wellbeing check-ins. Moodle is connected as the learning platform, not as the main student-record system.

The system is organized around four user groups:

| User group | What they do |
|---|---|
| Student | View courses, grades, documents, notifications, calendar deadlines, correction requests, AI co-pilot, and wellbeing check-ins. |
| Advisor | Review advisees, advising notes, student profiles, and at-risk alerts. |
| Faculty | Review teaching sections, rosters, attendance, and grade entry flows. |
| Admin | Manage users, courses, Moodle sync, audit logs, reports, documents, AI foundation, and staff summarisation. |

The main code boundary is:

- Browser screens live in [frontend/src/pages](../frontend/src/pages/).
- Browser data hooks live in [frontend/src/hooks](../frontend/src/hooks/).
- Browser API clients live in [frontend/src/api](../frontend/src/api/).
- Backend routes live in each Django app's `urls.py`.
- Backend request handling lives in `views.py` or `api/views.py`.
- Backend business logic lives in `services.py`.
- Backend database tables live in `models.py`.
- Backend access rules are centralized in [backend/apps/accounts/access.py](../backend/apps/accounts/access.py).

## How A Feature Connects From Screen To Database

Most features follow this path:

1. A user opens a route declared in [frontend/src/router.tsx](../frontend/src/router.tsx).
2. A page component under [frontend/src/pages](../frontend/src/pages/) renders the workflow.
3. The page calls a hook under [frontend/src/hooks](../frontend/src/hooks/).
4. The hook calls an API client under [frontend/src/api](../frontend/src/api/).
5. The API client sends a JWT-authenticated request through [frontend/src/api/axios.ts](../frontend/src/api/axios.ts).
6. Django routes the request through [backend/sis_backend/urls.py](../backend/sis_backend/urls.py).
7. [backend/apps/accounts/middleware.py](../backend/apps/accounts/middleware.py) checks the named route policy in [backend/apps/accounts/access.py](../backend/apps/accounts/access.py).
8. The app view validates input and calls a service.
9. The service reads or writes database models and records audit/notification side effects where required.
10. The frontend receives JSON and updates the screen.

That pattern is the best way to read the code. Pick a user action and follow the chain from route to page to hook to API client to backend URL to view to service to model.

## Use Case Map

### Student Logs In

The student enters credentials on [frontend/src/pages/Login.tsx](../frontend/src/pages/Login.tsx). The form component is [frontend/src/components/auth/LoginForm.tsx](../frontend/src/components/auth/LoginForm.tsx). The login request uses [frontend/src/api/auth.ts](../frontend/src/api/auth.ts), then stores the JWT session in [frontend/src/stores/authStore.ts](../frontend/src/stores/authStore.ts).

On the backend, [backend/apps/accounts/api/urls.py](../backend/apps/accounts/api/urls.py) maps `/api/v1/auth/login` to [backend/apps/accounts/api/views.py](../backend/apps/accounts/api/views.py). User, role, capability, and access-log data are modeled in [backend/apps/accounts/models.py](../backend/apps/accounts/models.py). Route-level authorization is controlled in [backend/apps/accounts/access.py](../backend/apps/accounts/access.py).

Tests: [backend/apps/accounts/tests](../backend/apps/accounts/tests/) and [frontend/tests/unit/login-form.test.tsx](../frontend/tests/unit/login-form.test.tsx).

### Student Registers For Courses

The route `/student/register` renders [frontend/src/pages/student/CourseRegistration.tsx](../frontend/src/pages/student/CourseRegistration.tsx). The registration UI uses [frontend/src/components/student/EnrollmentWizard.tsx](../frontend/src/components/student/EnrollmentWizard.tsx), [frontend/src/api/courses.ts](../frontend/src/api/courses.ts), [frontend/src/api/enrollments.ts](../frontend/src/api/enrollments.ts), [frontend/src/hooks/useCourses.ts](../frontend/src/hooks/useCourses.ts), and [frontend/src/hooks/useEnrollments.ts](../frontend/src/hooks/useEnrollments.ts).

The backend routes live in [backend/apps/academics/api/urls.py](../backend/apps/academics/api/urls.py). The academic tables are defined in [backend/apps/academics/models.py](../backend/apps/academics/models.py): courses, sections, enrollments, attendance, grades, and transcripts. Business rules and Moodle outbox side effects are coordinated in [backend/apps/academics/services.py](../backend/apps/academics/services.py).

Moodle provisioning is not done directly by the frontend. Academic actions create sync work that the Moodle integration app processes through [backend/apps/integration/services.py](../backend/apps/integration/services.py).

Tests: [backend/apps/academics/tests](../backend/apps/academics/tests/) and [frontend/tests/e2e/step-2-4-flows.spec.ts](../frontend/tests/e2e/step-2-4-flows.spec.ts).

### Faculty Manages A Section

Faculty users start at `/faculty`, rendered by [frontend/src/pages/faculty/Dashboard.tsx](../frontend/src/pages/faculty/Dashboard.tsx). A section detail route `/faculty/sections/:sectionId` renders [frontend/src/pages/faculty/SectionDetail.tsx](../frontend/src/pages/faculty/SectionDetail.tsx). Faculty-specific components live in [frontend/src/components/faculty](../frontend/src/components/faculty/).

The backend uses the academics app: [backend/apps/academics/api/views.py](../backend/apps/academics/api/views.py), [backend/apps/academics/api/serializers.py](../backend/apps/academics/api/serializers.py), [backend/apps/academics/models.py](../backend/apps/academics/models.py), and [backend/apps/academics/services.py](../backend/apps/academics/services.py).

### Advisor Reviews A Student

Advisor dashboard pages live in [frontend/src/pages/advisor](../frontend/src/pages/advisor/). The student profile page [frontend/src/pages/advisor/StudentProfile.tsx](../frontend/src/pages/advisor/StudentProfile.tsx) combines student profile data, advising notes, academic records, AI summarisation, and at-risk context. Advisor components live in [frontend/src/components/advisor](../frontend/src/components/advisor/).

Student records and advising data are owned by [backend/apps/students](../backend/apps/students/). At-risk alerts are owned by [backend/apps/atrisk](../backend/apps/atrisk/). Staff summarisation is owned by [backend/apps/summarisation](../backend/apps/summarisation/).

Tests: [backend/apps/students/tests/test_students_api.py](../backend/apps/students/tests/test_students_api.py), [backend/apps/atrisk/tests](../backend/apps/atrisk/tests/), and [backend/apps/summarisation/tests](../backend/apps/summarisation/tests/).

### Admin Manages Users

The `/admin/users` page is [frontend/src/pages/admin/Users.tsx](../frontend/src/pages/admin/Users.tsx). It uses [frontend/src/api/users.ts](../frontend/src/api/users.ts), [frontend/src/hooks/useUsers.ts](../frontend/src/hooks/useUsers.ts), and [frontend/src/components/admin/UserTable.tsx](../frontend/src/components/admin/UserTable.tsx).

The backend user API is in [backend/apps/accounts/api](../backend/apps/accounts/api/). Password policy is in [backend/apps/accounts/validators.py](../backend/apps/accounts/validators.py). Admin actions create access/audit records through [backend/apps/accounts/audit.py](../backend/apps/accounts/audit.py) and [backend/apps/audit](../backend/apps/audit/).

### Admin Monitors Moodle Sync

The `/admin/moodle-sync` page is [frontend/src/pages/admin/MoodleSync.tsx](../frontend/src/pages/admin/MoodleSync.tsx). It uses [frontend/src/api/moodleSync.ts](../frontend/src/api/moodleSync.ts), [frontend/src/hooks/useMoodleSync.ts](../frontend/src/hooks/useMoodleSync.ts), and admin UI helpers such as [frontend/src/components/admin/SyncStatusBadge.tsx](../frontend/src/components/admin/SyncStatusBadge.tsx).

The backend integration app is [backend/apps/integration](../backend/apps/integration/). Key files are:

- [backend/apps/integration/models.py](../backend/apps/integration/models.py) for outbox events, Moodle maps, engagement runs, snapshots, and LTI sessions.
- [backend/apps/integration/services.py](../backend/apps/integration/services.py) for Moodle REST calls, retry processing, and engagement ingestion.
- [backend/apps/integration/api/views.py](../backend/apps/integration/api/views.py) for admin monitoring endpoints.
- [backend/apps/integration/management/commands](../backend/apps/integration/management/commands/) for verification, sync, and ingestion commands.

Tests: [backend/apps/integration/tests](../backend/apps/integration/tests/).

### Moodle Launches An Embedded SIS Tool

Moodle LTI launch starts at `/lti/login`, then posts an id token to `/lti/launch`. The backend validates issuer, client ID, deployment, nonce/state, JWT signature, target link, and role context in [backend/apps/integration/lti.py](../backend/apps/integration/lti.py). The HTTP views are in [backend/apps/integration/lti_views.py](../backend/apps/integration/lti_views.py), and routes are in [backend/apps/integration/lti_urls.py](../backend/apps/integration/lti_urls.py).

After validation, the user is redirected to a frontend tool route such as [frontend/src/pages/lti/AdvisingTool.tsx](../frontend/src/pages/lti/AdvisingTool.tsx) or [frontend/src/pages/lti/RegistrationTool.tsx](../frontend/src/pages/lti/RegistrationTool.tsx). The frontend reads launch context through [frontend/src/api/lti.ts](../frontend/src/api/lti.ts).

Tests: [backend/apps/integration/tests/test_lti_tool_provider.py](../backend/apps/integration/tests/test_lti_tool_provider.py) and [frontend/tests/unit/lti-advising-tool.test.tsx](../frontend/tests/unit/lti-advising-tool.test.tsx).

### Student Uses The AI Co-pilot

The student route `/student/copilot` renders [frontend/src/pages/student/Copilot.tsx](../frontend/src/pages/student/Copilot.tsx). Feature components live in [frontend/src/features/copilot](../frontend/src/features/copilot/). The API client is [frontend/src/api/copilot.ts](../frontend/src/api/copilot.ts), and data state is managed by [frontend/src/hooks/useCopilot.ts](../frontend/src/hooks/useCopilot.ts).

Backend routes are in [backend/apps/copilot/urls.py](../backend/apps/copilot/urls.py), views in [backend/apps/copilot/views.py](../backend/apps/copilot/views.py), and orchestration in [backend/apps/copilot/services.py](../backend/apps/copilot/services.py). The co-pilot retrieves institutional knowledge through [backend/apps/knowledge/services.py](../backend/apps/knowledge/services.py), adds safe student context from [backend/apps/copilot/selectors.py](../backend/apps/copilot/selectors.py), calls a deterministic or external provider through [backend/apps/copilot/providers.py](../backend/apps/copilot/providers.py), and stores sessions/messages/audit logs in [backend/apps/copilot/models.py](../backend/apps/copilot/models.py).

The co-pilot is intentionally non-mutating. It can suggest links and explain records, but it does not create official records, change grades, register courses, or expose private document contents.

Tests: [backend/apps/copilot/tests](../backend/apps/copilot/tests/) and [frontend/tests/unit/student-copilot-page.test.tsx](../frontend/tests/unit/student-copilot-page.test.tsx).

### Admin Reviews AI Foundation

The `/admin/ai-foundation` page is [frontend/src/pages/admin/AIFoundation.tsx](../frontend/src/pages/admin/AIFoundation.tsx). It combines analytics readiness and knowledge-base retrieval using [frontend/src/api/aiFoundation.ts](../frontend/src/api/aiFoundation.ts), [frontend/src/hooks/useAIFoundation.ts](../frontend/src/hooks/useAIFoundation.ts), and [frontend/src/features/ai-foundation](../frontend/src/features/ai-foundation/).

Analytics snapshots are built by [backend/apps/analytics/services.py](../backend/apps/analytics/services.py). Knowledge ingestion and retrieval are handled by [backend/apps/knowledge/services.py](../backend/apps/knowledge/services.py), [backend/apps/knowledge/chunking.py](../backend/apps/knowledge/chunking.py), [backend/apps/knowledge/embeddings.py](../backend/apps/knowledge/embeddings.py), and [backend/apps/knowledge/vector_store.py](../backend/apps/knowledge/vector_store.py).

Tests: [backend/apps/analytics/tests](../backend/apps/analytics/tests/) and [backend/apps/knowledge/tests](../backend/apps/knowledge/tests/).

### Admin And Student Manage Documents

Admins use `/admin/documents`, rendered by [frontend/src/pages/admin/Documents.tsx](../frontend/src/pages/admin/Documents.tsx). Students use `/documents`, rendered by [frontend/src/pages/student/Documents.tsx](../frontend/src/pages/student/Documents.tsx). Shared document UI lives in [frontend/src/features/documents](../frontend/src/features/documents/), with data through [frontend/src/api/documents.ts](../frontend/src/api/documents.ts) and [frontend/src/hooks/useDocuments.ts](../frontend/src/hooks/useDocuments.ts).

The backend app [backend/apps/documents](../backend/apps/documents/) owns document upload, validation, visibility, review, archive, protected download, audit, and notifications. Permission rules live in [backend/apps/documents/permissions.py](../backend/apps/documents/permissions.py). Query filtering lives in [backend/apps/documents/selectors.py](../backend/apps/documents/selectors.py). Business workflows live in [backend/apps/documents/services.py](../backend/apps/documents/services.py).

Document downloads stream through protected API responses. The system does not expose raw storage paths to the frontend.

Tests: [backend/apps/documents/tests](../backend/apps/documents/tests/) and [frontend/tests/unit/documents-pages.test.tsx](../frontend/tests/unit/documents-pages.test.tsx).

### Everyone Uses Notifications And Calendar

Notifications appear through the topbar [frontend/src/components/layout/Topbar.tsx](../frontend/src/components/layout/Topbar.tsx) and the page [frontend/src/pages/Notifications.tsx](../frontend/src/pages/Notifications.tsx). Backend notifications live in [backend/apps/notifications](../backend/apps/notifications/).

The academic calendar page [frontend/src/pages/AcademicCalendar.tsx](../frontend/src/pages/AcademicCalendar.tsx) uses [frontend/src/api/calendar.ts](../frontend/src/api/calendar.ts) and [frontend/src/hooks/useAcademicCalendar.ts](../frontend/src/hooks/useAcademicCalendar.ts). Backend calendar data and rules live in [backend/apps/calendar](../backend/apps/calendar/).

Notifications are in-app only. They do not send email, SMS, or push notifications.

### Admin Uses Reports And Audit Logs

Reports are shown at `/admin/reports`, rendered by [frontend/src/pages/admin/Reports.tsx](../frontend/src/pages/admin/Reports.tsx). Backend report aggregation lives in [backend/apps/reporting/services.py](../backend/apps/reporting/services.py).

Audit logs are shown at `/admin/audit-log`, rendered by [frontend/src/pages/admin/AuditLog.tsx](../frontend/src/pages/admin/AuditLog.tsx). Backend audit storage and redaction live in [backend/apps/audit](../backend/apps/audit/).

Audit events are append-only from the API perspective. The UI is for review, filtering, and governance visibility.

### Student Uses Wellbeing Support

The student route `/student/wellbeing` renders [frontend/src/pages/student/Wellbeing.tsx](../frontend/src/pages/student/Wellbeing.tsx). The UI uses [frontend/src/components/wellbeing](../frontend/src/components/wellbeing/), [frontend/src/features/wellbeing/MoodSelector.tsx](../frontend/src/features/wellbeing/MoodSelector.tsx), [frontend/src/api/wellbeing.ts](../frontend/src/api/wellbeing.ts), and [frontend/src/hooks/useWellbeing.ts](../frontend/src/hooks/useWellbeing.ts).

The backend app [backend/apps/wellbeing](../backend/apps/wellbeing/) owns consent, check-ins, triage, escalation notifications, student history deletion, coordinator alerts, and anonymized reporting. The triage flow is deterministic and policy-gated; it is not an unrestricted LLM crisis classifier.

Tests: [backend/apps/wellbeing/tests/test_wellbeing.py](../backend/apps/wellbeing/tests/test_wellbeing.py) and [frontend/tests/unit/wellbeing-page.test.tsx](../frontend/tests/unit/wellbeing-page.test.tsx).

## Cross-Cutting Integration Points

| Integration point | What connects | Code |
|---|---|---|
| Route authorization | Every protected API route to role/capability rules | [backend/apps/accounts/access.py](../backend/apps/accounts/access.py), [backend/apps/accounts/middleware.py](../backend/apps/accounts/middleware.py) |
| JWT session | Login, refresh, frontend route guards, API requests | [frontend/src/stores/authStore.ts](../frontend/src/stores/authStore.ts), [frontend/src/api/axios.ts](../frontend/src/api/axios.ts), [frontend/src/components/auth/ProtectedRoute.tsx](../frontend/src/components/auth/ProtectedRoute.tsx) |
| Audit logging | Admin actions, sync events, AI actions, documents, reporting | [backend/apps/audit](../backend/apps/audit/), plus app service calls |
| Notifications | Moodle failures, grades, enrollment, advising, documents, calendar, wellbeing | [backend/apps/notifications](../backend/apps/notifications/) |
| Moodle sync | SIS user/course/enrollment/grade events to Moodle REST | [backend/apps/integration/services.py](../backend/apps/integration/services.py) |
| Moodle engagement | Moodle course/user activity into SIS analytics snapshots | [backend/apps/integration/services.py](../backend/apps/integration/services.py), [backend/apps/analytics/services.py](../backend/apps/analytics/services.py) |
| AI retrieval | Knowledge sources to chunks to embeddings to co-pilot answers | [backend/apps/knowledge](../backend/apps/knowledge/), [backend/apps/copilot](../backend/apps/copilot/) |
| Protected files | Student document upload/review/download with role visibility | [backend/apps/documents](../backend/apps/documents/) |

## What Is Implemented

The repository currently contains working code for:

- Authentication, JWT refresh, RBAC, user management, password policy, and access logs.
- Student profiles, advisor assignments, financial flags, advising notes, and correction requests.
- Courses, sections, enrollments, attendance, grades, transcript generation, and Moodle sync outbox events.
- Moodle REST provisioning, Moodle engagement ingestion, LTI 1.3 tool launch flow, and admin sync monitoring.
- Notifications, audit log, academic calendar, admin reporting, and student document management.
- Analytics ETL, institutional knowledge ingestion/retrieval, student AI co-pilot, and staff summarisation.
- At-risk alert engine and opt-in wellbeing support.
- Docker Compose local/staging infrastructure and automated backend/frontend tests.

## What Is Intentionally Not Implemented

The current system does not implement:

- Admissions/applicant intake.
- Billing/payment processing.
- Email, SMS, or push notification delivery.
- OCR or AI document extraction.
- Permanent document deletion workflows.
- AI actions that mutate official SIS records.
- Production-grade Celery task implementations. The Compose services are placeholders for later background worker expansion.
- A fully automated live Moodle web-service bootstrap. Moodle service-role/token setup still requires the Phase 3 runbooks.

## How To Run It As A New Contributor

The simple path from the repository root is:

```bash
./scripts/dev-up.sh
```

That command starts the core Docker Compose stack, runs migrations, seeds demo SIS data, and tries to open `http://127.0.0.1:8080`.

Use these demo accounts:

```text
admin.demo    / DemoPass123!
advisor.demo  / DemoPass123!
faculty.demo  / DemoPass123!
student.demo1 / DemoPass123!
student.demo2 / DemoPass123!
```

For optional Moodle, Qdrant, knowledge ingestion, co-pilot demo data, summarisation data, and at-risk demo data:

```bash
./scripts/dev-up.sh --full
```

The first `--full` run pulls Docker Hub service and build-base images before Compose starts. [scripts/dev-up.sh](../scripts/dev-up.sh) retries those pulls and caches any completed layers, so a timeout such as `failed to fetch anonymous token` usually means Docker Hub or the local network stalled rather than the codebase being broken. Rerun the command when the connection is stable, or extend retries with `DOCKER_PULL_RETRIES=5 DOCKER_PULL_RETRY_DELAY=10 ./scripts/dev-up.sh --full`.

For a headless server:

```bash
./scripts/dev-up.sh --no-open
```

## Best First Reading Path

1. Read [README.md](../README.md) for project overview and commands.
2. Read this document for the human system explanation.
3. Read [CODEBASE_ONBOARDING.md](CODEBASE_ONBOARDING.md) for folder and file ownership.
4. Open [frontend/src/router.tsx](../frontend/src/router.tsx) to see every screen.
5. Open [backend/sis_backend/urls.py](../backend/sis_backend/urls.py) to see every backend route group.
6. Open [backend/apps/accounts/access.py](../backend/apps/accounts/access.py) to see which roles can call which APIs.
7. Follow one complete feature path, such as documents or co-pilot, from frontend page to backend service.
