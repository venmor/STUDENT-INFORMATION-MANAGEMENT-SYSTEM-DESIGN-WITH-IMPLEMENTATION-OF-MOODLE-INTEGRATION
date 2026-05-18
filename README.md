# Objective 1 Supervisor Submission

Student Information Management System Design and Implementation With Integration of Moodle.

Prepared by Chitundu Milimbo and Charles Hangoma for Prof. J Phiri, Department of Computer Science, School of Natural Sciences, The University of Zambia.

## Objective 1

To design and develop a modular Student Information System with core administrative modules for student records, course management, enrollment, and grade management, and to implement bidirectional integration with Moodle using Moodle web services API for provisioning and LTI v1.3 for embedding SIS-hosted tools.

## Contents of This Branch

This branch contains the source code and submission documents required to inspect, run, and test the implemented Objective 1 work:

- `backend/`: Django REST backend for accounts, student records, academic structure, enrollments, grades, Moodle integration, LTI launch handling, notifications, audit activity, calendar, reports, and documents.
- `frontend/`: React/Vite frontend for administrator, advisor, faculty, and student workflows.
- `infra/`: Docker Compose configuration and environment templates for the SIS stack and optional Moodle-connected testing.
- `docs/objective-1/`: source map and implementation notes for Objective 1.
- `submission/`: supervisor report in Markdown and DOCX format plus submission readme.

## Quick Start

1. Copy environment templates:

```bash
cp infra/.env.example infra/.env
cp infra/moodle.env.example infra/moodle.env
```

2. Start the application stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build
```

3. Prepare backend data:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml exec backend python manage.py migrate
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml exec backend python manage.py seed_demo_sis
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml exec backend python manage.py seed_moodle_demo
```

4. Open the frontend:

```text
http://127.0.0.1:8080
```

Demo users are created by `seed_demo_sis`. The seeded administrator, advisor, faculty, and student accounts allow the supervisor to verify role-based access, student records, enrollment workflows, grade workflows, Moodle synchronization screens, and LTI tool launch readiness.

## Verification Commands

Backend:

```bash
cd backend
DJANGO_SECRET_KEY=test-secret DJANGO_SETTINGS_MODULE=sis_backend.test_settings MYSQL_DATABASE=test MYSQL_USER=test MYSQL_PASSWORD=test MYSQL_HOST=localhost MYSQL_PORT=3306 pytest apps/accounts apps/students apps/structure apps/academics apps/integration apps/notifications apps/audit apps/calendar apps/reporting apps/documents
```

Frontend:

```bash
cd frontend
npm ci
npm run typecheck
npm run lint
npm test -- --reporter=dot
npm run build
```

Docker configuration:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
docker compose -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml config
```
