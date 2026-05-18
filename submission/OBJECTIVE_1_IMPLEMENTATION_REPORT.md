# Objective 1 Implementation Report

## Project Details

**Institution:** The University of Zambia, School of Natural Sciences, Department of Computer Science  
**Project Title:** Student Information Management System Design and Implementation With Integration of Moodle  
**Students:** Chitundu Milimbo and Charles Hangoma  
**Supervisor:** Prof. J Phiri  
**Submission Date:** 18 May 2026  
**Submission Branch:** `supervisor/objective-1-submission`  
**Submission Tag:** `objective-1-supervisor-submission-v1`

## Project Objective 1

To design and develop a modular Student Information System with core administrative modules for student records, course management, enrollment, and grade management, and to implement bidirectional integration with Moodle using Moodle web services API for provisioning and LTI v1.3 for embedding SIS-hosted tools.

## Implementation Summary

Objective 1 has been implemented as a full-stack Student Information System composed of a Django REST backend, a React/Vite frontend, and Docker-based infrastructure for local and Moodle-connected testing. The implementation keeps the SIS as the authoritative administrative and academic record while providing integration points for Moodle provisioning and embedded SIS tools.

The system includes the required core administrative modules: student records, academic structure and course management, enrollment management, and grade management. It also includes supporting workflows needed to operate and verify those modules, including user access control, notifications, audit activity, academic calendar, reporting, and student document handling.

The Moodle integration work is implemented through two lanes. The provisioning lane uses Moodle web service configuration, mapping tables, integration outbox events, synchronization commands, and monitoring screens. The embedded-tool lane implements LTI v1.3 launch handling, JWKS publication, launch session storage, context validation, and frontend routes for SIS-hosted tools launched from Moodle.

## Objective 1 Implementation Evidence

| Requirement from Objective 1 | Implementation Evidence |
| --- | --- |
| Modular Student Information System | Backend applications under `backend/apps/` and frontend routes under `frontend/src/pages/` are separated by responsibility and role. |
| Student records | `backend/apps/students/`, `frontend/src/api/students.ts`, advisor and student profile screens. |
| Course management | `backend/apps/structure/`, `backend/apps/academics/`, administrator academic-structure UI, course and section APIs. |
| Enrollment management | Enrollment records, enrollment events, waitlist/approval workflow, student registration UI, advisor/faculty visibility. |
| Grade management | `backend/apps/academics/`, faculty grade-entry workflow, official grade release, student grades view, correction workflow. |
| Moodle web service provisioning | `backend/apps/integration/` outbox events, Moodle client, mapping records, sync processing command, Moodle sync monitoring UI. |
| LTI v1.3 embedded tools | LTI launch service, JWKS endpoint, launch-session model, context mapping, and embedded frontend tool routes. |
| Full-stack reviewability | Docker Compose stack, backend tests, frontend typecheck/lint/tests/build, and supervisor submission documents. |

## Backend Progress

The backend implementation provides role-based access for administrator, advisor, faculty, and student users. It exposes REST APIs for student profiles, academic structure, course sections, enrollment actions, grade workflows, Moodle synchronization, LTI launches, notifications, audit activity, academic dates, reports, and documents.

The Moodle provisioning lane records synchronization work in integration outbox events and supports user, course, enrollment, and grade synchronization workflows. The integration module includes processing commands and monitoring APIs so the supervisor can inspect both successful and failed sync activity.

The LTI lane implements the security and launch structure required for Moodle to launch SIS-hosted tools. The backend publishes keys, validates launch context, maps Moodle users and courses to SIS records, and stores launch sessions for auditability.

## Frontend Progress

The frontend provides role-specific screens that demonstrate Objective 1 end to end. Administrators can manage users, academic structure, Moodle synchronization, audit activity, reports, calendar records, and documents. Advisors can search for students and open unified student profiles. Faculty users can review rosters and enter grades. Students can access their dashboard, registration, grades, calendar, notifications, and documents.

The Moodle and LTI review paths are represented in the frontend by the Moodle synchronization monitoring page and SIS-hosted LTI tool routes for advising and registration workflows.

## Source Code Submitted

The source code submitted on the branch includes:

- `backend/`
- `frontend/`
- `infra/`
- `docs/objective-1/`
- `submission/`
- `.github/workflows/`
- project configuration files required to install, test, build, and run the system

The branch intentionally contains only Objective 1 implementation source and the supporting modules required for Objective 1 operation and verification.

## Testing and Verification

The implementation can be verified through backend tests, frontend static checks and tests, frontend production build, and Docker Compose configuration checks.

Verification performed on 18 May 2026:

| Check | Result |
| --- | --- |
| Python source compilation | Passed |
| Docker Compose configuration for development stack | Passed |
| Docker Compose configuration for Moodle-connected stack | Passed |
| Frontend dependency installation | Passed with 0 reported vulnerabilities |
| Frontend TypeScript typecheck | Passed |
| Frontend lint | Passed |
| Frontend unit tests | 18 test files passed, 65 tests passed |
| Frontend production build | Passed |
| Backend focused Objective 1 test suite | 177 tests passed |

Backend verification command:

```bash
cd backend
DJANGO_SECRET_KEY=test-secret DJANGO_SETTINGS_MODULE=sis_backend.test_settings MYSQL_DATABASE=test MYSQL_USER=test MYSQL_PASSWORD=test MYSQL_HOST=localhost MYSQL_PORT=3306 pytest apps/accounts apps/students apps/structure apps/academics apps/integration apps/notifications apps/audit apps/calendar apps/reporting apps/documents
```

Frontend verification commands:

```bash
cd frontend
npm ci
npm run typecheck
npm run lint
npm test -- --reporter=dot
npm run build
```

Docker configuration verification:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
docker compose -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml config
```

## Supervisor Review Guide

To review the submitted implementation, clone the repository, check out branch `supervisor/objective-1-submission`, copy the environment templates, start the Docker Compose stack, run migrations, seed demo data, and open the frontend at `http://127.0.0.1:8080`.

Recommended review flow:

1. Sign in as an administrator and review users, academic structure, Moodle synchronization, audit activity, reports, and documents.
2. Sign in as an advisor and open the student search and unified student profile screens.
3. Sign in as a faculty user and review class roster and grade-entry workflows.
4. Sign in as a student and review dashboard, registration, grades, calendar, notifications, and documents.
5. Review the Moodle sync monitoring page and LTI tool routes to inspect Moodle integration readiness.

## Conclusion

Objective 1 is implemented as a working full-stack SIS with the required administrative modules and Moodle integration lanes. The submitted branch provides the source code, documentation, and test commands needed for the supervisor to run, inspect, and verify the implementation.
