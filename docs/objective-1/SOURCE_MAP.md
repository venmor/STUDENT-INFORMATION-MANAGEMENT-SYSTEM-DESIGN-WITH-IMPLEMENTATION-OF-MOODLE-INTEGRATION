# Objective 1 Source Map

## Project

Student Information Management System Design and Implementation With Integration of Moodle.

## Students

Chitundu Milimbo and Charles Hangoma.

## Supervisor

Prof. J Phiri.

## Objective 1

To design and develop a modular Student Information System with core administrative modules for student records, course management, enrollment, and grade management, and to implement bidirectional integration with Moodle using Moodle web services API for provisioning and LTI v1.3 for embedding SIS-hosted tools.

## Backend Source Map

| Area | Main paths | Evidence |
| --- | --- | --- |
| Accounts and access control | `backend/apps/accounts/` | Authenticated users, roles, access policies, demo users, login/audit events |
| Student records | `backend/apps/students/` | Student profiles, advisor assignment, student APIs |
| Academic structure | `backend/apps/structure/` | Schools, departments, programmes, academic organisation |
| Course management and enrollment | `backend/apps/academics/` | Courses, terms, sections, enrollment records, waitlists, enrollment events |
| Grade management | `backend/apps/academics/` | Grade records, officialisation, release workflow, correction requests |
| Moodle integration | `backend/apps/integration/` | Moodle web service client, outbox events, Moodle mappings, engagement ingestion, LTI v1.3 provider |
| Supporting SIS workflows | `backend/apps/notifications/`, `backend/apps/audit/`, `backend/apps/calendar/`, `backend/apps/reporting/`, `backend/apps/documents/` | Operational review, notifications, audit trail, calendar, reports, and document evidence |
| Backend configuration | `backend/sis_backend/` | Installed apps, API routing, settings, test settings |

## Frontend Source Map

| Area | Main paths | Evidence |
| --- | --- | --- |
| API clients | `frontend/src/api/` | Typed clients for students, courses, enrollments, grades, Moodle sync, LTI tools, reports, calendar, notifications, documents |
| Application routing | `frontend/src/router.tsx` | Role-based routes and LTI tool routes |
| Shared shell | `frontend/src/components/layout/` | Sidebar, topbar, authenticated app shell |
| Administrator workflows | `frontend/src/pages/admin/` | Users, academic structure, Moodle sync, audit activity, reports, documents |
| Advisor workflows | `frontend/src/pages/advisor/` and `frontend/src/components/advisor/` | Student search and unified student profile |
| Faculty workflows | `frontend/src/pages/faculty/` | Course rosters and grade entry |
| Student workflows | `frontend/src/pages/student/`, `frontend/src/pages/Registration.tsx`, `frontend/src/pages/Grades.tsx` | Dashboard, registration, grades, calendar, notifications, documents |
| LTI tool UI | `frontend/src/pages/lti/` | Embedded advising and registration tool entry points |

## Infrastructure Source Map

| Area | Main paths | Evidence |
| --- | --- | --- |
| SIS Docker stack | `infra/docker-compose.yml` and `infra/docker-compose.dev.yml` | Local backend, frontend, database, and supporting services |
| Moodle-connected configuration | `infra/docker-compose.moodle.yml` and `infra/moodle.env.example` | Moodle review configuration and integration variables |
| Environment template | `infra/.env.example` | Required SIS configuration variables |

## Submission Documents

| File | Purpose |
| --- | --- |
| `submission/OBJECTIVE_1_IMPLEMENTATION_REPORT.md` | Main supervisor report in Markdown |
| `submission/OBJECTIVE_1_IMPLEMENTATION_REPORT.docx` | Main supervisor report in Word format |
| `submission/SUBMISSION_README.md` | Branch, tag, archive, and testing instructions |
