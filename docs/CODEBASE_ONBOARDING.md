# Codebase Onboarding Guide

This guide is the practical map for the Modern Student Information System repository. It explains what the system does, where each feature lives, how the folders are organized, and how a developer who is new to Django, React, Vite, TypeScript, Docker, or Moodle integration can start making changes without getting lost.

## Quick Orientation

Modern SIS is a multi-role academic operations platform. The SIS owns student records, courses, enrollments, grades, documents, audit history, reporting, AI-assisted support, at-risk alerts, wellbeing check-ins, and integration state. Moodle is treated as the learning environment that receives provisioning data and sends engagement signals back into the SIS.

The repository is split into four main areas:

| Area | Purpose |
|---|---|
| [backend](../backend/) | Django 5 + Django REST Framework API, database models, Moodle/LTI integration, AI services, management commands, and backend tests. |
| [frontend](../frontend/) | React 18 + TypeScript + Vite SPA, role-based pages, API clients, hooks, shared UI components, and frontend tests. |
| [docs](../docs/) | Architecture decisions, phase documentation, API contracts, diagrams, specs, and this onboarding guide. |
| [infra](../infra/) | Docker Compose stacks, environment examples, and Nginx reverse proxy configuration. |

The most useful entry points are [README.md](../README.md), [docs/SYSTEM_EXPLAINED.md](SYSTEM_EXPLAINED.md), [backend/README.md](../backend/README.md), [frontend/README.md](../frontend/README.md), [backend/sis_backend/urls.py](../backend/sis_backend/urls.py), and [frontend/src/router.tsx](../frontend/src/router.tsx).

## Repository Root Files

| Path | Purpose |
|---|---|
| [README.md](../README.md) | Main project overview, current phase status, local run instructions, Moodle/AI phase runbooks, demo account notes, and verification commands. |
| [CHANGELOG.md](../CHANGELOG.md) | Repository-level change history. |
| [scripts/dev-up.sh](../scripts/dev-up.sh) | One-command local demonstration startup: Compose up, migrations, demo data, and browser open attempt. |
| [backend](../backend/) | Backend application folder. |
| [frontend](../frontend/) | Frontend application folder. |
| [docs](../docs/) | Documentation folder. |
| [infra](../infra/) | Infrastructure and Docker Compose folder. |

## Technology Stack In Plain English

The stack is documented in [docs/architecture/technology-stack.md](architecture/technology-stack.md) and accepted in [docs/architecture/ADR-001-technology-baseline.md](architecture/ADR-001-technology-baseline.md).

| Technology | Where | What it does |
|---|---|---|
| Django | [backend](../backend/) | Python web framework. It defines models, database migrations, URL routes, API views, settings, middleware, and management commands. |
| Django REST Framework | [backend/apps](../backend/apps/) | API layer used by the React frontend. Most endpoints return JSON and are mounted under `/api/v1/`. |
| MySQL | [infra/docker-compose.yml](../infra/docker-compose.yml) | Main relational database for authoritative SIS data. |
| Simple JWT | [backend/apps/accounts](../backend/apps/accounts/) | Access and refresh token authentication for the SPA. |
| React | [frontend/src](../frontend/src/) | Browser UI broken into pages, layout components, feature components, hooks, and API clients. |
| TypeScript | [frontend/tsconfig.json](../frontend/tsconfig.json) | Adds static types to frontend data contracts and component props. |
| Vite | [frontend/vite.config.ts](../frontend/vite.config.ts) | Frontend dev server, build tool, and local API proxy. |
| TanStack Query | [frontend/src/hooks](../frontend/src/hooks/) | Fetching, caching, and mutating server data in React. |
| Zustand | [frontend/src/stores/authStore.ts](../frontend/src/stores/authStore.ts) | Lightweight frontend session store. |
| Tailwind CSS | [frontend/tailwind.config.js](../frontend/tailwind.config.js), [frontend/src/index.css](../frontend/src/index.css) | Utility-first styling and project design tokens. |
| Docker Compose | [infra](../infra/) | Local and staging service orchestration for MySQL, backend, frontend, proxy, Moodle, and Qdrant. |
| Moodle REST + LTI 1.3 | [backend/apps/integration](../backend/apps/integration/) | Provisioning sync, engagement ingestion, and embedded Moodle tool launches. |
| Qdrant/vector search | [backend/apps/knowledge](../backend/apps/knowledge/) | Retrieval layer for institutional knowledge used by AI features. |

## How The App Starts

Backend startup:

1. [backend/manage.py](../backend/manage.py) starts Django commands and the development server.
2. [backend/sis_backend/settings.py](../backend/sis_backend/settings.py) loads installed apps, middleware, database settings, JWT settings, Moodle settings, LTI settings, document limits, vector-store settings, and AI-provider settings from environment variables.
3. [backend/sis_backend/urls.py](../backend/sis_backend/urls.py) mounts the Django admin, LTI routes, and every `/api/v1/` app route.
4. [backend/apps/accounts/middleware.py](../backend/apps/accounts/middleware.py) authenticates protected API routes and applies centralized role/capability policies from [backend/apps/accounts/access.py](../backend/apps/accounts/access.py).

Frontend startup:

1. [frontend/src/main.tsx](../frontend/src/main.tsx) creates the React root, TanStack Query client, and browser router.
2. [frontend/src/App.tsx](../frontend/src/App.tsx) renders the application router.
3. [frontend/src/router.tsx](../frontend/src/router.tsx) declares all routes and role gates.
4. [frontend/src/components/layout/AppShell.tsx](../frontend/src/components/layout/AppShell.tsx) wraps authenticated pages with sidebar, topbar, and content area.
5. [frontend/src/api/axios.ts](../frontend/src/api/axios.ts) creates the shared Axios clients and handles JWT refresh.

## Request Flow

The common browser-to-database flow looks like this:

1. A page such as [frontend/src/pages/student/Copilot.tsx](../frontend/src/pages/student/Copilot.tsx) renders role-specific UI.
2. A hook such as [frontend/src/hooks/useCopilot.ts](../frontend/src/hooks/useCopilot.ts) calls an API client.
3. An API client such as [frontend/src/api/copilot.ts](../frontend/src/api/copilot.ts) sends a request through [frontend/src/api/axios.ts](../frontend/src/api/axios.ts).
4. Django matches the URL in a backend URL file such as [backend/apps/copilot/urls.py](../backend/apps/copilot/urls.py).
5. The access middleware checks route policy in [backend/apps/accounts/access.py](../backend/apps/accounts/access.py).
6. A backend view such as [backend/apps/copilot/views.py](../backend/apps/copilot/views.py) validates request data through serializers and calls service logic.
7. Service files such as [backend/apps/copilot/services.py](../backend/apps/copilot/services.py) use models/selectors/providers to read or write database records.
8. The view serializes the response and the frontend hook updates the UI.

## Feature Map

| Feature | Backend location | Frontend location | Main routes/pages |
|---|---|---|---|
| Authentication, RBAC, users, password reset | [backend/apps/accounts](../backend/apps/accounts/) | [frontend/src/api/auth.ts](../frontend/src/api/auth.ts), [frontend/src/hooks/useAuth.ts](../frontend/src/hooks/useAuth.ts), [frontend/src/stores/authStore.ts](../frontend/src/stores/authStore.ts), [frontend/src/pages/Login.tsx](../frontend/src/pages/Login.tsx), [frontend/src/pages/admin/Users.tsx](../frontend/src/pages/admin/Users.tsx) | `/login`, `/account/password`, `/admin/users`, `/api/v1/auth/login`, `/api/v1/users` |
| Student profiles, advisor assignments, financial flags, advising notes, correction requests | [backend/apps/students](../backend/apps/students/) | [frontend/src/api/students.ts](../frontend/src/api/students.ts), [frontend/src/hooks/useStudents.ts](../frontend/src/hooks/useStudents.ts), [frontend/src/pages/advisor/StudentProfile.tsx](../frontend/src/pages/advisor/StudentProfile.tsx), [frontend/src/pages/student/Corrections.tsx](../frontend/src/pages/student/Corrections.tsx) | `/advisor/students/:studentId`, `/student/corrections`, `/api/v1/students` |
| Courses, sections, enrollment, attendance, grades, transcript | [backend/apps/academics](../backend/apps/academics/) | [frontend/src/api/courses.ts](../frontend/src/api/courses.ts), [frontend/src/api/enrollments.ts](../frontend/src/api/enrollments.ts), [frontend/src/api/grades.ts](../frontend/src/api/grades.ts), [frontend/src/pages/student/MyCourses.tsx](../frontend/src/pages/student/MyCourses.tsx), [frontend/src/pages/student/MyGrades.tsx](../frontend/src/pages/student/MyGrades.tsx), [frontend/src/pages/student/CourseRegistration.tsx](../frontend/src/pages/student/CourseRegistration.tsx), [frontend/src/pages/admin/Courses.tsx](../frontend/src/pages/admin/Courses.tsx), [frontend/src/pages/faculty/SectionDetail.tsx](../frontend/src/pages/faculty/SectionDetail.tsx) | `/student/courses`, `/student/grades`, `/student/register`, `/admin/courses`, `/faculty/sections/:sectionId` |
| Moodle sync monitoring and engagement ingestion | [backend/apps/integration](../backend/apps/integration/) | [frontend/src/api/moodleSync.ts](../frontend/src/api/moodleSync.ts), [frontend/src/hooks/useMoodleSync.ts](../frontend/src/hooks/useMoodleSync.ts), [frontend/src/pages/admin/MoodleSync.tsx](../frontend/src/pages/admin/MoodleSync.tsx) | `/admin/moodle-sync`, `/api/v1/integration/moodle/...` |
| Moodle LTI embedded tools | [backend/apps/integration/lti.py](../backend/apps/integration/lti.py), [backend/apps/integration/lti_views.py](../backend/apps/integration/lti_views.py), [backend/apps/integration/lti_urls.py](../backend/apps/integration/lti_urls.py) | [frontend/src/api/lti.ts](../frontend/src/api/lti.ts), [frontend/src/pages/lti/AdvisingTool.tsx](../frontend/src/pages/lti/AdvisingTool.tsx), [frontend/src/pages/lti/RegistrationTool.tsx](../frontend/src/pages/lti/RegistrationTool.tsx) | `/lti/login`, `/lti/launch`, `/lti/api/session`, `/lti/tools/advising-dashboard`, `/lti/tools/registration` |
| In-app notifications | [backend/apps/notifications](../backend/apps/notifications/) | [frontend/src/api/notifications.ts](../frontend/src/api/notifications.ts), [frontend/src/hooks/useNotifications.ts](../frontend/src/hooks/useNotifications.ts), [frontend/src/pages/Notifications.tsx](../frontend/src/pages/Notifications.tsx), [frontend/src/components/layout/Topbar.tsx](../frontend/src/components/layout/Topbar.tsx) | `/notifications`, `/api/v1/notifications` |
| Audit/admin activity | [backend/apps/audit](../backend/apps/audit/) | [frontend/src/api/audit.ts](../frontend/src/api/audit.ts), [frontend/src/hooks/useAuditActivity.ts](../frontend/src/hooks/useAuditActivity.ts), [frontend/src/pages/admin/AuditLog.tsx](../frontend/src/pages/admin/AuditLog.tsx) | `/admin/audit-log`, `/api/v1/admin/activity` |
| Academic calendar and deadline rules | [backend/apps/calendar](../backend/apps/calendar/) | [frontend/src/api/calendar.ts](../frontend/src/api/calendar.ts), [frontend/src/hooks/useAcademicCalendar.ts](../frontend/src/hooks/useAcademicCalendar.ts), [frontend/src/pages/AcademicCalendar.tsx](../frontend/src/pages/AcademicCalendar.tsx) | `/calendar`, `/api/v1/calendar/events/` |
| Admin reports | [backend/apps/reporting](../backend/apps/reporting/) | [frontend/src/api/reports.ts](../frontend/src/api/reports.ts), [frontend/src/hooks/useAdminReports.ts](../frontend/src/hooks/useAdminReports.ts), [frontend/src/pages/admin/Reports.tsx](../frontend/src/pages/admin/Reports.tsx) | `/admin/reports`, `/api/v1/admin/reports/...` |
| Student document management | [backend/apps/documents](../backend/apps/documents/) | [frontend/src/api/documents.ts](../frontend/src/api/documents.ts), [frontend/src/hooks/useDocuments.ts](../frontend/src/hooks/useDocuments.ts), [frontend/src/features/documents](../frontend/src/features/documents/), [frontend/src/pages/admin/Documents.tsx](../frontend/src/pages/admin/Documents.tsx), [frontend/src/pages/student/Documents.tsx](../frontend/src/pages/student/Documents.tsx) | `/admin/documents`, `/documents`, `/api/v1/documents` |
| Analytics ETL | [backend/apps/analytics](../backend/apps/analytics/) | [frontend/src/api/aiFoundation.ts](../frontend/src/api/aiFoundation.ts), [frontend/src/hooks/useAIFoundation.ts](../frontend/src/hooks/useAIFoundation.ts), [frontend/src/pages/admin/AIFoundation.tsx](../frontend/src/pages/admin/AIFoundation.tsx) | `/admin/ai-foundation`, `/api/v1/admin/analytics/...` |
| Knowledge base and vector retrieval | [backend/apps/knowledge](../backend/apps/knowledge/) | [frontend/src/features/ai-foundation](../frontend/src/features/ai-foundation/) | `/admin/ai-foundation`, `/api/v1/admin/knowledge/...` |
| Student AI Co-pilot | [backend/apps/copilot](../backend/apps/copilot/) | [frontend/src/api/copilot.ts](../frontend/src/api/copilot.ts), [frontend/src/hooks/useCopilot.ts](../frontend/src/hooks/useCopilot.ts), [frontend/src/features/copilot](../frontend/src/features/copilot/), [frontend/src/pages/student/Copilot.tsx](../frontend/src/pages/student/Copilot.tsx) | `/student/copilot`, `/api/v1/ai/copilot/...` |
| Staff summarisation | [backend/apps/summarisation](../backend/apps/summarisation/) | [frontend/src/hooks/useSummarisation.ts](../frontend/src/hooks/useSummarisation.ts), [frontend/src/features/summarisation](../frontend/src/features/summarisation/), [frontend/src/pages/admin/Summarise.tsx](../frontend/src/pages/admin/Summarise.tsx) | `/admin/summarise`, `/api/v1/ai/summarise/` |
| At-risk student engine | [backend/apps/atrisk](../backend/apps/atrisk/) | [frontend/src/api/ai.ts](../frontend/src/api/ai.ts), [frontend/src/hooks/useAtRiskAlerts.ts](../frontend/src/hooks/useAtRiskAlerts.ts), [frontend/src/components/advisor/AtRiskAlertQueue.tsx](../frontend/src/components/advisor/AtRiskAlertQueue.tsx), [frontend/src/pages/advisor/AlertHistory.tsx](../frontend/src/pages/advisor/AlertHistory.tsx) | `/advisor`, `/advisor/alerts`, `/api/v1/advisor/at-risk/...` |
| Opt-in wellbeing support | [backend/apps/wellbeing](../backend/apps/wellbeing/) | [frontend/src/api/wellbeing.ts](../frontend/src/api/wellbeing.ts), [frontend/src/hooks/useWellbeing.ts](../frontend/src/hooks/useWellbeing.ts), [frontend/src/components/wellbeing](../frontend/src/components/wellbeing/), [frontend/src/features/wellbeing/MoodSelector.tsx](../frontend/src/features/wellbeing/MoodSelector.tsx), [frontend/src/pages/student/Wellbeing.tsx](../frontend/src/pages/student/Wellbeing.tsx) | `/student/wellbeing`, `/api/v1/wellbeing/...`, `/api/v1/ai/wellbeing/triage` |

## Backend Folder Guide

The backend follows a Django app-per-domain structure under [backend/apps](../backend/apps/). A typical app contains:

| File or folder | Meaning |
|---|---|
| `models.py` | Database tables and enums. Changes here usually require migrations. |
| `services.py` | Business logic and workflows. This is where most non-trivial backend behavior should live. |
| `selectors.py` | Query helpers for read paths. Not every app has this file. |
| `serializers.py` or `api/serializers.py` | DRF serializers that validate input and shape output JSON. |
| `views.py` or `api/views.py` | DRF API views. These should stay thin and call services/selectors. |
| `urls.py` or `api/urls.py` | URL patterns for that app. |
| `permissions.py` | App-specific object permission helpers, where needed. |
| `admin.py` | Django admin registration for local inspection. |
| `management/commands` | `python manage.py ...` commands for seeds, ETL, sync, and verification. |
| `tests` | Pytest/Django tests for the app. |
| `migrations` | Django migration history. Do not edit old migrations casually. |

### Backend Root Files

| Path | Purpose |
|---|---|
| [backend/manage.py](../backend/manage.py) | Django command entry point. Use it for `runserver`, `migrate`, `check`, and custom management commands. |
| [backend/pytest.ini](../backend/pytest.ini) | Pytest configuration for Django tests. |
| [backend/Dockerfile](../backend/Dockerfile) | Backend container image definition. |
| [backend/README.md](../backend/README.md) | Backend phase notes, endpoint summaries, and verification commands. |
| [backend/requirements/base.txt](../backend/requirements/base.txt) | Runtime Python dependencies. |
| [backend/requirements/dev.txt](../backend/requirements/dev.txt) | Development and test Python dependencies. |
| [backend/sis_backend/settings.py](../backend/sis_backend/settings.py) | Main Django settings. Environment variables are loaded here. |
| [backend/sis_backend/test_settings.py](../backend/sis_backend/test_settings.py) | Test-specific Django settings. |
| [backend/sis_backend/urls.py](../backend/sis_backend/urls.py) | Root URL composition for all backend apps. |
| [backend/sis_backend/asgi.py](../backend/sis_backend/asgi.py) | ASGI application entry point. |
| [backend/sis_backend/wsgi.py](../backend/sis_backend/wsgi.py) | WSGI application entry point used by Gunicorn. |

### Backend Apps

| Folder | Files it carries | Purpose |
|---|---|---|
| [backend/apps/accounts](../backend/apps/accounts/) | [models.py](../backend/apps/accounts/models.py), [constants.py](../backend/apps/accounts/constants.py), [managers.py](../backend/apps/accounts/managers.py), [validators.py](../backend/apps/accounts/validators.py), [access.py](../backend/apps/accounts/access.py), [middleware.py](../backend/apps/accounts/middleware.py), [audit.py](../backend/apps/accounts/audit.py), [checks.py](../backend/apps/accounts/checks.py), [api](../backend/apps/accounts/api/), [management](../backend/apps/accounts/management/), [tests](../backend/apps/accounts/tests/) | Users, roles, capabilities, JWT login/refresh, password policy, centralized route authorization, and access logs. |
| [backend/apps/students](../backend/apps/students/) | [models.py](../backend/apps/students/models.py), [api](../backend/apps/students/api/), [admin.py](../backend/apps/students/admin.py), [tests](../backend/apps/students/tests/) | Student profiles, advisor assignments, financial flags, advising notes, correction requests, and student-record access. |
| [backend/apps/academics](../backend/apps/academics/) | [models.py](../backend/apps/academics/models.py), [services.py](../backend/apps/academics/services.py), [api](../backend/apps/academics/api/), [admin.py](../backend/apps/academics/admin.py), [tests](../backend/apps/academics/tests/) | Courses, prerequisites, sections, timetables, enrollments, waitlists, attendance, grading, academic standing, and transcripts. |
| [backend/apps/integration](../backend/apps/integration/) | [models.py](../backend/apps/integration/models.py), [services.py](../backend/apps/integration/services.py), [lti.py](../backend/apps/integration/lti.py), [lti_views.py](../backend/apps/integration/lti_views.py), [lti_urls.py](../backend/apps/integration/lti_urls.py), [api](../backend/apps/integration/api/), [management](../backend/apps/integration/management/), [tests](../backend/apps/integration/tests/) | Moodle REST sync, outbox retry state, Moodle user/course maps, engagement ingestion, integration readiness checks, and LTI 1.3 launch/session flow. |
| [backend/apps/notifications](../backend/apps/notifications/) | [models.py](../backend/apps/notifications/models.py), [services.py](../backend/apps/notifications/services.py), [api](../backend/apps/notifications/api/), [tests](../backend/apps/notifications/tests/) | User-scoped in-app notifications, unread summaries, mark-as-read workflows, and notification creation helpers. |
| [backend/apps/audit](../backend/apps/audit/) | [models.py](../backend/apps/audit/models.py), [services.py](../backend/apps/audit/services.py), [api](../backend/apps/audit/api/), [management](../backend/apps/audit/management/), [tests](../backend/apps/audit/tests/) | Append-only audit events, metadata redaction, admin audit browsing, and demo audit seed data. |
| [backend/apps/calendar](../backend/apps/calendar/) | [models.py](../backend/apps/calendar/models.py), [services.py](../backend/apps/calendar/services.py), [api](../backend/apps/calendar/api/), [management](../backend/apps/calendar/management/), [tests](../backend/apps/calendar/tests/) | Academic calendar events, deadlines, role-scoped visibility, event cancellation, summaries, and section-date synchronization. |
| [backend/apps/reporting](../backend/apps/reporting/) | [services.py](../backend/apps/reporting/services.py), [api](../backend/apps/reporting/api/), [management](../backend/apps/reporting/management/), [tests](../backend/apps/reporting/tests/) | Admin reporting aggregation across SIS records, Moodle sync, engagement, calendar, notifications, audit, grades, capacity, and documents. |
| [backend/apps/documents](../backend/apps/documents/) | [models.py](../backend/apps/documents/models.py), [validators.py](../backend/apps/documents/validators.py), [permissions.py](../backend/apps/documents/permissions.py), [selectors.py](../backend/apps/documents/selectors.py), [serializers.py](../backend/apps/documents/serializers.py), [services.py](../backend/apps/documents/services.py), [views.py](../backend/apps/documents/views.py), [urls.py](../backend/apps/documents/urls.py), [management](../backend/apps/documents/management/), [tests](../backend/apps/documents/tests/) | Student-linked document upload, review, visibility, protected download, audit, notification, and reporting support. |
| [backend/apps/analytics](../backend/apps/analytics/) | [models.py](../backend/apps/analytics/models.py), [selectors.py](../backend/apps/analytics/selectors.py), [serializers.py](../backend/apps/analytics/serializers.py), [services.py](../backend/apps/analytics/services.py), [views.py](../backend/apps/analytics/views.py), [urls.py](../backend/apps/analytics/urls.py), [management](../backend/apps/analytics/management/), [tests](../backend/apps/analytics/tests/) | Analytics ETL runs and student analytics snapshots derived from SIS and Moodle engagement signals. |
| [backend/apps/knowledge](../backend/apps/knowledge/) | [models.py](../backend/apps/knowledge/models.py), [chunking.py](../backend/apps/knowledge/chunking.py), [embeddings.py](../backend/apps/knowledge/embeddings.py), [vector_store.py](../backend/apps/knowledge/vector_store.py), [services.py](../backend/apps/knowledge/services.py), [serializers.py](../backend/apps/knowledge/serializers.py), [views.py](../backend/apps/knowledge/views.py), [urls.py](../backend/apps/knowledge/urls.py), [management](../backend/apps/knowledge/management/), [tests](../backend/apps/knowledge/tests/) | Institutional knowledge sources, chunking, deterministic/OpenAI-compatible embeddings, Qdrant/in-memory vector search, ingestion, and retrieval testing. |
| [backend/apps/copilot](../backend/apps/copilot/) | [models.py](../backend/apps/copilot/models.py), [selectors.py](../backend/apps/copilot/selectors.py), [serializers.py](../backend/apps/copilot/serializers.py), [services.py](../backend/apps/copilot/services.py), [providers.py](../backend/apps/copilot/providers.py), [prompts.py](../backend/apps/copilot/prompts.py), [safety.py](../backend/apps/copilot/safety.py), [retry.py](../backend/apps/copilot/retry.py), [suggestions.py](../backend/apps/copilot/suggestions.py), [audit.py](../backend/apps/copilot/audit.py), [views.py](../backend/apps/copilot/views.py), [urls.py](../backend/apps/copilot/urls.py), [management](../backend/apps/copilot/management/), [tests](../backend/apps/copilot/tests/) | Student-facing, retrieval-grounded AI co-pilot with safe context assembly, provider abstraction, audit logging, sessions, messages, feedback, and suggested actions. |
| [backend/apps/summarisation](../backend/apps/summarisation/) | [models.py](../backend/apps/summarisation/models.py), [serializers.py](../backend/apps/summarisation/serializers.py), [services.py](../backend/apps/summarisation/services.py), [providers.py](../backend/apps/summarisation/providers.py), [prompts.py](../backend/apps/summarisation/prompts.py), [views.py](../backend/apps/summarisation/views.py), [urls.py](../backend/apps/summarisation/urls.py), [management](../backend/apps/summarisation/management/), [tests](../backend/apps/summarisation/tests/) | Staff workflow summarisation requests, AI provider calls, urgency handling, approval flow, and demo seed data. |
| [backend/apps/atrisk](../backend/apps/atrisk/) | [models.py](../backend/apps/atrisk/models.py), [signals.py](../backend/apps/atrisk/signals.py), [config.py](../backend/apps/atrisk/config.py), [services.py](../backend/apps/atrisk/services.py), [serializers.py](../backend/apps/atrisk/serializers.py), [views.py](../backend/apps/atrisk/views.py), [urls.py](../backend/apps/atrisk/urls.py), [management](../backend/apps/atrisk/management/), [tests](../backend/apps/atrisk/tests/) | Deterministic at-risk signal evaluation, severity classification, advisor alert queue, acknowledgements, auto-close, and seed/run commands. |
| [backend/apps/wellbeing](../backend/apps/wellbeing/) | [models.py](../backend/apps/wellbeing/models.py), [permissions.py](../backend/apps/wellbeing/permissions.py), [serializers.py](../backend/apps/wellbeing/serializers.py), [services.py](../backend/apps/wellbeing/services.py), [prompts.py](../backend/apps/wellbeing/prompts.py), [views.py](../backend/apps/wellbeing/views.py), [urls.py](../backend/apps/wellbeing/urls.py), [tests](../backend/apps/wellbeing/tests/) | Opt-in wellbeing consent, student check-ins, deterministic triage, escalation notifications, deletion rights, coordinator alerts, and anonymized reporting. |
| [backend/apps/testutils.py](../backend/apps/testutils.py) | Test helper functions. | Shared helpers for backend tests. |

## Backend Data Models At A Glance

| App | Important models |
|---|---|
| [accounts](../backend/apps/accounts/models.py) | `Role`, `User`, `UserCapability`, `AccessLog` |
| [students](../backend/apps/students/models.py) | `StudentProfile`, `AdvisorAssignment`, `FinancialFlag`, `AdvisingNote`, `StudentCorrectionRequest` |
| [academics](../backend/apps/academics/models.py) | `Course`, `CoursePrerequisite`, `CourseSection`, `SectionTimetable`, `Enrollment`, `EnrollmentEvent`, `WaitlistEntry`, `AttendanceSession`, `AttendanceRecord`, `GradingScaleBand`, `AcademicStandingRule`, `GradeRecord`, `GradeChangeLog` |
| [integration](../backend/apps/integration/models.py) | `IntegrationOutboxEvent`, `MoodleUserMap`, `MoodleCourseMap`, `MoodleEngagementIngestionRun`, `MoodleEngagementSnapshot`, `LtiOidcState`, `LtiLaunchSession` |
| [notifications](../backend/apps/notifications/models.py) | `Notification` |
| [audit](../backend/apps/audit/models.py) | `AuditEvent` |
| [calendar](../backend/apps/calendar/models.py) | `AcademicCalendarEvent` |
| [documents](../backend/apps/documents/models.py) | `StudentDocument` |
| [analytics](../backend/apps/analytics/models.py) | `AnalyticsETLRun`, `StudentAnalyticsSnapshot` |
| [knowledge](../backend/apps/knowledge/models.py) | `KnowledgeSource`, `KnowledgeChunk`, `KnowledgeIngestionRun` |
| [copilot](../backend/apps/copilot/models.py) | `CopilotSession`, `CopilotMessage`, `AIAuditLog`, `CopilotFeedback` |
| [summarisation](../backend/apps/summarisation/models.py) | `SummarisationRequest` |
| [atrisk](../backend/apps/atrisk/models.py) | `AtRiskAlert` |
| [wellbeing](../backend/apps/wellbeing/models.py) | `WellbeingConsent`, `WellbeingCheckIn`, `WellbeingAuditLog` |

## Backend URL Map

All normal API routes are mounted in [backend/sis_backend/urls.py](../backend/sis_backend/urls.py) under `/api/v1/`. LTI routes are mounted under `/lti/`.

| URL group | Backend file |
|---|---|
| `/api/v1/auth/...`, `/api/v1/users...` | [backend/apps/accounts/api/urls.py](../backend/apps/accounts/api/urls.py) |
| `/api/v1/students...` | [backend/apps/students/api/urls.py](../backend/apps/students/api/urls.py) |
| `/api/v1/courses`, `/api/v1/sections`, `/api/v1/enrollments`, `/api/v1/grades`, `/api/v1/attendance...` | [backend/apps/academics/api/urls.py](../backend/apps/academics/api/urls.py) |
| `/api/v1/integration/moodle/...` | [backend/apps/integration/api/urls.py](../backend/apps/integration/api/urls.py) |
| `/lti/jwks`, `/lti/login`, `/lti/launch`, `/lti/api/session` | [backend/apps/integration/lti_urls.py](../backend/apps/integration/lti_urls.py) |
| `/api/v1/notifications...` | [backend/apps/notifications/api/urls.py](../backend/apps/notifications/api/urls.py) |
| `/api/v1/admin/activity...` | [backend/apps/audit/api/urls.py](../backend/apps/audit/api/urls.py) |
| `/api/v1/calendar...` | [backend/apps/calendar/api/urls.py](../backend/apps/calendar/api/urls.py) |
| `/api/v1/admin/reports...` | [backend/apps/reporting/api/urls.py](../backend/apps/reporting/api/urls.py) |
| `/api/v1/documents...`, `/api/v1/me/documents`, `/api/v1/students/:id/documents` | [backend/apps/documents/urls.py](../backend/apps/documents/urls.py) |
| `/api/v1/admin/analytics...` | [backend/apps/analytics/urls.py](../backend/apps/analytics/urls.py) |
| `/api/v1/admin/knowledge...` | [backend/apps/knowledge/urls.py](../backend/apps/knowledge/urls.py) |
| `/api/v1/ai/copilot...` | [backend/apps/copilot/urls.py](../backend/apps/copilot/urls.py) |
| `/api/v1/ai/summarise...` | [backend/apps/summarisation/urls.py](../backend/apps/summarisation/urls.py) |
| `/api/v1/advisor/at-risk...` | [backend/apps/atrisk/urls.py](../backend/apps/atrisk/urls.py) |
| `/api/v1/wellbeing...`, `/api/v1/ai/wellbeing/triage` | [backend/apps/wellbeing/urls.py](../backend/apps/wellbeing/urls.py) |

## Frontend Folder Guide

The frontend is organized by responsibility:

| Folder | Files it carries | Purpose |
|---|---|---|
| [frontend/src/api](../frontend/src/api/) | API client files such as [auth.ts](../frontend/src/api/auth.ts), [students.ts](../frontend/src/api/students.ts), [courses.ts](../frontend/src/api/courses.ts), [documents.ts](../frontend/src/api/documents.ts), [copilot.ts](../frontend/src/api/copilot.ts), and [axios.ts](../frontend/src/api/axios.ts). | One file per backend domain. These functions perform HTTP requests and keep endpoint strings out of components. |
| [frontend/src/hooks](../frontend/src/hooks/) | Hooks such as [useAuth.ts](../frontend/src/hooks/useAuth.ts), [useStudents.ts](../frontend/src/hooks/useStudents.ts), [useDocuments.ts](../frontend/src/hooks/useDocuments.ts), and [useCopilot.ts](../frontend/src/hooks/useCopilot.ts). | React/TanStack Query hooks for loading, caching, and mutating API data. |
| [frontend/src/pages](../frontend/src/pages/) | Role and route-level pages under [admin](../frontend/src/pages/admin/), [student](../frontend/src/pages/student/), [advisor](../frontend/src/pages/advisor/), [faculty](../frontend/src/pages/faculty/), [lti](../frontend/src/pages/lti/), plus shared pages such as [Login.tsx](../frontend/src/pages/Login.tsx) and [Notifications.tsx](../frontend/src/pages/Notifications.tsx). | Top-level screens rendered by [frontend/src/router.tsx](../frontend/src/router.tsx). |
| [frontend/src/components](../frontend/src/components/) | Shared UI, layout, auth, student, advisor, faculty, admin, AI, and wellbeing components. | Reusable visual and workflow pieces shared across pages. |
| [frontend/src/features](../frontend/src/features/) | Larger feature component sets for [ai-foundation](../frontend/src/features/ai-foundation/), [copilot](../frontend/src/features/copilot/), [documents](../frontend/src/features/documents/), [summarisation](../frontend/src/features/summarisation/), and [wellbeing](../frontend/src/features/wellbeing/). | Feature-specific components and utilities that are too specialized for `components/`. |
| [frontend/src/stores](../frontend/src/stores/) | [authStore.ts](../frontend/src/stores/authStore.ts). | Zustand stores. Currently this is the persisted JWT/session store. |
| [frontend/src/types](../frontend/src/types/) | Domain TypeScript types such as [documents.ts](../frontend/src/types/documents.ts), [copilot.ts](../frontend/src/types/copilot.ts), [calendar.ts](../frontend/src/types/calendar.ts), and [index.ts](../frontend/src/types/index.ts). | Shared type contracts for API responses and UI data. |
| [frontend/src/utils](../frontend/src/utils/) | [cn.ts](../frontend/src/utils/cn.ts), [formatters.ts](../frontend/src/utils/formatters.ts), [roleGuards.ts](../frontend/src/utils/roleGuards.ts). | Small helper functions for class merging, formatting, and role navigation. |
| [frontend/tests](../frontend/tests/) | [unit](../frontend/tests/unit/) tests, [e2e](../frontend/tests/e2e/) tests, and [setup.ts](../frontend/tests/setup.ts). | Vitest/Testing Library and Playwright coverage. |
| [frontend/public](../frontend/public/) | [sis-logo.svg](../frontend/public/sis-logo.svg), [favicon.svg](../frontend/public/favicon.svg). | Static assets served by Vite/Nginx. |
| [frontend/docs](../frontend/docs/) | [frontend-design-system.md](../frontend/docs/frontend-design-system.md). | Design system reference for frontend work. |

### Frontend Root Files

| Path | Purpose |
|---|---|
| [frontend/package.json](../frontend/package.json) | Frontend scripts and npm dependencies. |
| [frontend/package-lock.json](../frontend/package-lock.json) | Locked npm dependency tree for the frontend. |
| [frontend/vite.config.ts](../frontend/vite.config.ts) | Vite dev server, build, path aliases, and API proxy settings. |
| [frontend/tsconfig.json](../frontend/tsconfig.json), [frontend/tsconfig.app.json](../frontend/tsconfig.app.json), [frontend/tsconfig.node.json](../frontend/tsconfig.node.json) | TypeScript compiler configuration. |
| [frontend/eslint.config.js](../frontend/eslint.config.js) | Frontend lint rules. |
| [frontend/tailwind.config.js](../frontend/tailwind.config.js) | Tailwind theme and design tokens. |
| [frontend/postcss.config.cjs](../frontend/postcss.config.cjs) | PostCSS/Tailwind build config. |
| [frontend/playwright.config.ts](../frontend/playwright.config.ts) | Browser E2E test configuration. |
| [frontend/index.html](../frontend/index.html) | Vite HTML entry file. |
| [frontend/nginx.conf](../frontend/nginx.conf) | Production SPA serving config used in the frontend container. |
| [frontend/Dockerfile](../frontend/Dockerfile) | Frontend container image definition. |

## Frontend Routing Map

The route source of truth is [frontend/src/router.tsx](../frontend/src/router.tsx).

| Role/scope | Routes | Pages |
|---|---|---|
| Public | `/login`, `/forbidden` | [Login.tsx](../frontend/src/pages/Login.tsx), [AccessDenied.tsx](../frontend/src/pages/AccessDenied.tsx) |
| LTI embedded | `/lti/tools/advising-dashboard`, `/lti/tools/registration` | [AdvisingTool.tsx](../frontend/src/pages/lti/AdvisingTool.tsx), [RegistrationTool.tsx](../frontend/src/pages/lti/RegistrationTool.tsx) |
| Shared authenticated | `/account/password`, `/notifications`, `/calendar` | [AccountPassword.tsx](../frontend/src/pages/AccountPassword.tsx), [Notifications.tsx](../frontend/src/pages/Notifications.tsx), [AcademicCalendar.tsx](../frontend/src/pages/AcademicCalendar.tsx) |
| Student | `/student`, `/student/courses`, `/student/grades`, `/student/register`, `/student/copilot`, `/student/corrections`, `/student/wellbeing`, `/documents` | [frontend/src/pages/student](../frontend/src/pages/student/) |
| Advisor | `/advisor`, `/advisor/students/:studentId`, `/advisor/alerts` | [frontend/src/pages/advisor](../frontend/src/pages/advisor/) |
| Faculty | `/faculty`, `/faculty/sections/:sectionId` | [frontend/src/pages/faculty](../frontend/src/pages/faculty/) |
| Admin | `/admin`, `/admin/users`, `/admin/courses`, `/admin/moodle-sync`, `/admin/audit-log`, `/admin/reports`, `/admin/documents`, `/admin/ai-foundation`, `/admin/summarise` | [frontend/src/pages/admin](../frontend/src/pages/admin/) |

## Documentation Folder Guide

| Folder or file | Purpose |
|---|---|
| [docs/README.md](README.md) | Documentation index. |
| [docs/CODEBASE_ONBOARDING.md](CODEBASE_ONBOARDING.md) | This guide. |
| [docs/api/openapi.yaml](api/openapi.yaml) | OpenAPI contract draft/interface definition. |
| [docs/architecture](architecture/) | Stack rationale, ADRs, and architecture diagrams. |
| [docs/architecture/technology-stack.md](architecture/technology-stack.md) | Authoritative stack recommendation. |
| [docs/architecture/ADR-001-technology-baseline.md](architecture/ADR-001-technology-baseline.md) | Accepted architecture decision record. |
| [docs/architecture/architecture-diagrams.md](architecture/architecture-diagrams.md) | Links and descriptions for architecture diagrams. |
| [docs/diagrams](diagrams/) | ERD, source diagram documentation, and rendered diagram assets. |
| [docs/diagrams/rendered](diagrams/rendered/) | Exported SVG/PNG/FigJam diagram artifacts. |
| [docs/phases](phases/) | Phase-by-phase delivery notes, change logs, and test matrices. |
| [docs/project](project/) | SRS, problem statement, vision, and setup guide. |
| [docs/process/version-control.md](process/version-control.md) | Version-control workflow guidance. |
| [docs/specs](specs/) | Project specs that are not tied to a single implementation phase. |
| [docs/archive](archive/) | Historical source documents retained for reference. |
| [docs/superpowers](superpowers/) | Internal planning/spec artifacts used during implementation. |

## Infra Folder Guide

| File or folder | Purpose |
|---|---|
| [infra/README.md](../infra/README.md) | Infrastructure runbook and Compose notes. |
| [infra/.env.example](../infra/.env.example) | Base environment variables for local/development services. |
| [infra/staging.env.example](../infra/staging.env.example) | Staging-oriented environment example. |
| [infra/moodle.env.example](../infra/moodle.env.example) | Moodle service environment example. |
| [infra/docker-compose.yml](../infra/docker-compose.yml) | Base Compose stack. |
| [infra/docker-compose.dev.yml](../infra/docker-compose.dev.yml) | Development overlay. |
| [infra/docker-compose.staging.yml](../infra/docker-compose.staging.yml) | Staging overlay. |
| [infra/docker-compose.moodle.yml](../infra/docker-compose.moodle.yml) | Optional Moodle/Qdrant services for later-phase integration work. |
| [infra/nginx/default.conf](../infra/nginx/default.conf) | Reverse proxy routing for frontend/backend services. |

## Tests And Verification

Backend tests live beside each backend domain under `backend/apps/*/tests`. Important examples:

| Test area | Path |
|---|---|
| Auth/RBAC/users | [backend/apps/accounts/tests](../backend/apps/accounts/tests/) |
| Core student APIs | [backend/apps/students/tests/test_students_api.py](../backend/apps/students/tests/test_students_api.py) |
| Courses and grades | [backend/apps/academics/tests](../backend/apps/academics/tests/) |
| Moodle sync and LTI | [backend/apps/integration/tests](../backend/apps/integration/tests/) |
| Notifications | [backend/apps/notifications/tests/test_notifications_api.py](../backend/apps/notifications/tests/test_notifications_api.py) |
| Audit | [backend/apps/audit/tests/test_audit_activity_api.py](../backend/apps/audit/tests/test_audit_activity_api.py) |
| Calendar | [backend/apps/calendar/tests](../backend/apps/calendar/tests/) |
| Reporting | [backend/apps/reporting/tests/test_admin_reporting_api.py](../backend/apps/reporting/tests/test_admin_reporting_api.py) |
| Documents | [backend/apps/documents/tests](../backend/apps/documents/tests/) |
| Analytics | [backend/apps/analytics/tests](../backend/apps/analytics/tests/) |
| Knowledge | [backend/apps/knowledge/tests](../backend/apps/knowledge/tests/) |
| Copilot | [backend/apps/copilot/tests](../backend/apps/copilot/tests/) |
| Summarisation | [backend/apps/summarisation/tests](../backend/apps/summarisation/tests/) |
| At-risk | [backend/apps/atrisk/tests](../backend/apps/atrisk/tests/) |
| Wellbeing | [backend/apps/wellbeing/tests/test_wellbeing.py](../backend/apps/wellbeing/tests/test_wellbeing.py) |

Frontend tests live in [frontend/tests](../frontend/tests/):

| Test area | Path |
|---|---|
| Unit/component/route tests | [frontend/tests/unit](../frontend/tests/unit/) |
| E2E browser tests | [frontend/tests/e2e](../frontend/tests/e2e/) |
| Test setup | [frontend/tests/setup.ts](../frontend/tests/setup.ts) |

Common verification commands:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q
```

```bash
cd frontend
npm run typecheck
npm test
npm run lint
npm run build
```

## Management Commands

Use these from [backend](../backend/) as `python manage.py <command>`.

| Command | File | Purpose |
|---|---|---|
| `seed_demo_sis` | [backend/apps/accounts/management/commands/seed_demo_sis.py](../backend/apps/accounts/management/commands/seed_demo_sis.py) | Seed repeatable core SIS demo data. |
| `verify_moodle_rest` | [backend/apps/integration/management/commands/verify_moodle_rest.py](../backend/apps/integration/management/commands/verify_moodle_rest.py) | Verify Moodle REST connectivity. |
| `process_moodle_sync` | [backend/apps/integration/management/commands/process_moodle_sync.py](../backend/apps/integration/management/commands/process_moodle_sync.py) | Process/retry Moodle provisioning outbox events. |
| `ingest_moodle_engagement` | [backend/apps/integration/management/commands/ingest_moodle_engagement.py](../backend/apps/integration/management/commands/ingest_moodle_engagement.py) | Pull Moodle engagement data into SIS snapshots. |
| `verify_phase_3_integrations` | [backend/apps/integration/management/commands/verify_phase_3_integrations.py](../backend/apps/integration/management/commands/verify_phase_3_integrations.py) | Print local Moodle/LTI/readiness checks. |
| `seed_audit_activity_demo` | [backend/apps/audit/management/commands/seed_audit_activity_demo.py](../backend/apps/audit/management/commands/seed_audit_activity_demo.py) | Seed safe audit viewer demo records. |
| `seed_academic_calendar_demo` | [backend/apps/calendar/management/commands/seed_academic_calendar_demo.py](../backend/apps/calendar/management/commands/seed_academic_calendar_demo.py) | Seed safe academic calendar demo events. |
| `sync_academic_calendar_from_sections` | [backend/apps/calendar/management/commands/sync_academic_calendar_from_sections.py](../backend/apps/calendar/management/commands/sync_academic_calendar_from_sections.py) | Create/update calendar deadlines from course-section dates. |
| `seed_reporting_demo` | [backend/apps/reporting/management/commands/seed_reporting_demo.py](../backend/apps/reporting/management/commands/seed_reporting_demo.py) | Seed reporting demo data. |
| `seed_document_demo` | [backend/apps/documents/management/commands/seed_document_demo.py](../backend/apps/documents/management/commands/seed_document_demo.py) | Seed student document demo records. |
| `seed_analytics_demo` | [backend/apps/analytics/management/commands/seed_analytics_demo.py](../backend/apps/analytics/management/commands/seed_analytics_demo.py) | Seed analytics demo data. |
| `run_analytics_etl` | [backend/apps/analytics/management/commands/run_analytics_etl.py](../backend/apps/analytics/management/commands/run_analytics_etl.py) | Build student analytics snapshots. |
| `seed_knowledge_demo` | [backend/apps/knowledge/management/commands/seed_knowledge_demo.py](../backend/apps/knowledge/management/commands/seed_knowledge_demo.py) | Seed institutional knowledge sources. |
| `ingest_knowledge_base` | [backend/apps/knowledge/management/commands/ingest_knowledge_base.py](../backend/apps/knowledge/management/commands/ingest_knowledge_base.py) | Chunk/embed/index knowledge sources. |
| `query_knowledge_base` | [backend/apps/knowledge/management/commands/query_knowledge_base.py](../backend/apps/knowledge/management/commands/query_knowledge_base.py) | Test retrieval from the knowledge base. |
| `seed_copilot_demo` | [backend/apps/copilot/management/commands/seed_copilot_demo.py](../backend/apps/copilot/management/commands/seed_copilot_demo.py) | Seed safe co-pilot demo records. |
| `test_copilot_query` | [backend/apps/copilot/management/commands/test_copilot_query.py](../backend/apps/copilot/management/commands/test_copilot_query.py) | Exercise deterministic co-pilot answering. |
| `seed_summarisation_demo` | [backend/apps/summarisation/management/commands/seed_summarisation_demo.py](../backend/apps/summarisation/management/commands/seed_summarisation_demo.py) | Seed staff summarisation demo data. |
| `seed_at_risk_demo` | [backend/apps/atrisk/management/commands/seed_at_risk_demo.py](../backend/apps/atrisk/management/commands/seed_at_risk_demo.py) | Seed at-risk alert demo data. |
| `run_at_risk_engine` | [backend/apps/atrisk/management/commands/run_at_risk_engine.py](../backend/apps/atrisk/management/commands/run_at_risk_engine.py) | Evaluate active students and update alerts. |

## Local Development Path

The fastest complete path is the one-command startup script:

```bash
./scripts/dev-up.sh
```

For a headless machine, use:

```bash
./scripts/dev-up.sh --no-open
```

For the optional Moodle, Qdrant, and richer AI demo stack, use:

```bash
./scripts/dev-up.sh --full
```

The first full run downloads Docker Hub images for the backend/frontend build bases plus Moodle, MariaDB, and Qdrant. [scripts/dev-up.sh](../scripts/dev-up.sh) checks those external images before Compose starts and retries failed pulls; if Docker Hub reports a network or auth-token timeout, rerun the same command once the connection is stable. Use `DOCKER_PULL_RETRIES=5 DOCKER_PULL_RETRY_DELAY=10 ./scripts/dev-up.sh --full` when you want a longer retry window.

The manual Docker Compose path is also documented in [README.md](../README.md) and [infra/README.md](../infra/README.md):

```bash
cd infra
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d db backend frontend proxy
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python manage.py migrate --noinput
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python manage.py seed_demo_sis
```

Then open `http://127.0.0.1:8080`.

For hot-reload local development:

```bash
cd backend
python manage.py runserver 127.0.0.1:8000
```

```bash
cd frontend
npm install
npm run dev
```

Then open `http://127.0.0.1:5173`.

## Conventions To Follow

- Add backend behavior in the domain app that owns the data. For example, document review logic belongs in [backend/apps/documents/services.py](../backend/apps/documents/services.py), not in a frontend component or unrelated app.
- Keep DRF views thin. Validate input with serializers, check object-level permission where required, then call service/selectors.
- Register new backend API routes in the app `urls.py`, include them through [backend/sis_backend/urls.py](../backend/sis_backend/urls.py), and add route policies in [backend/apps/accounts/access.py](../backend/apps/accounts/access.py).
- When adding or changing models, create migrations and update tests.
- Frontend pages should call hooks, not raw Axios. Hooks call files in [frontend/src/api](../frontend/src/api/).
- Shared UI belongs in [frontend/src/components/ui](../frontend/src/components/ui/). Feature-specific UI belongs under [frontend/src/features](../frontend/src/features/) or a role folder in [frontend/src/components](../frontend/src/components/).
- Route-level screens belong in [frontend/src/pages](../frontend/src/pages/) and must be added to [frontend/src/router.tsx](../frontend/src/router.tsx).
- Frontend type contracts belong in [frontend/src/types](../frontend/src/types/) when more than one component or hook needs them.
- Follow the existing design system in [frontend/docs/frontend-design-system.md](../frontend/docs/frontend-design-system.md) and Tailwind tokens in [frontend/tailwind.config.js](../frontend/tailwind.config.js).
- Keep sensitive data out of API responses. The integration, audit, AI, document, and report areas already sanitize secrets and metadata.

## Adding A New Feature

Use this checklist:

1. Identify the domain owner in [backend/apps](../backend/apps/).
2. Add or update models in that app's `models.py`.
3. Generate and review migrations.
4. Put business logic in `services.py`.
5. Add read/query helpers in `selectors.py` if the query is reused or complex.
6. Add serializers and views.
7. Add URL patterns and route access policies.
8. Add backend tests near the app.
9. Add frontend API functions in [frontend/src/api](../frontend/src/api/).
10. Add TypeScript types in [frontend/src/types](../frontend/src/types/).
11. Add TanStack Query hooks in [frontend/src/hooks](../frontend/src/hooks/).
12. Build or extend page/components in [frontend/src/pages](../frontend/src/pages/), [frontend/src/components](../frontend/src/components/), or [frontend/src/features](../frontend/src/features/).
13. Add/update frontend tests.
14. Run backend and frontend verification commands.

## Suggested Reading Order For New Contributors

1. [README.md](../README.md) for project purpose and run commands.
2. [docs/architecture/technology-stack.md](architecture/technology-stack.md) for stack rationale.
3. [backend/sis_backend/urls.py](../backend/sis_backend/urls.py) and [frontend/src/router.tsx](../frontend/src/router.tsx) to understand routes.
4. [backend/apps/accounts/access.py](../backend/apps/accounts/access.py) to understand role-based access.
5. One vertical slice end to end. A good first slice is documents: [backend/apps/documents](../backend/apps/documents/), [frontend/src/api/documents.ts](../frontend/src/api/documents.ts), [frontend/src/hooks/useDocuments.ts](../frontend/src/hooks/useDocuments.ts), [frontend/src/features/documents](../frontend/src/features/documents/), [frontend/src/pages/admin/Documents.tsx](../frontend/src/pages/admin/Documents.tsx), and [frontend/src/pages/student/Documents.tsx](../frontend/src/pages/student/Documents.tsx).
6. [docs/phases](phases/) when you need historical delivery context.

## Starter Agent Instructions

If an AI coding agent is helping in this repo, give it these project-specific instructions:

```md
# Modern SIS Agent Notes

- Backend is Django/DRF under `backend/`; frontend is React/TypeScript/Vite under `frontend/`; infra is Docker Compose under `infra/`.
- Read `docs/CODEBASE_ONBOARDING.md`, `backend/sis_backend/urls.py`, `frontend/src/router.tsx`, and `backend/apps/accounts/access.py` before broad changes.
- Keep backend views thin. Put business rules in app `services.py`, reusable read queries in `selectors.py`, and route authorization in `backend/apps/accounts/access.py`.
- Add migrations for model changes and do not edit old migrations casually.
- Frontend pages call hooks; hooks call API clients; API clients use `frontend/src/api/axios.ts`.
- Keep UI consistent with `frontend/docs/frontend-design-system.md`, `frontend/tailwind.config.js`, and existing shared components.
- Verify with relevant backend pytest targets and frontend typecheck/test/lint/build before claiming completion.
- Do not expose Moodle tokens, LTI keys, JWTs, passwords, private document storage paths, or unsafe metadata in APIs or docs.
```
