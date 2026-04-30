# Frontend

This directory contains the rebuilt React 18 + TypeScript + Vite frontend for Phase 2 Step 2.4.

## Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS v3 with custom design tokens
- TanStack Query
- React Router
- Axios
- Zustand
- Vitest + Testing Library
- Playwright

## Commands

```bash
npm install
npm run dev
npm run typecheck
npm test
npm run test:e2e
npm run lint
npm run build
```

## Step 2.5 CI And Container Baseline

- the required CI workflow runs `npm run typecheck`, `npm test -- --reporter=dot`, `npm run lint`, and `npm run build`
- Playwright remains a separate workflow so browser verification exists without becoming the blocking merge gate
- `frontend/Dockerfile` builds the Vite application and serves it from Nginx
- `frontend/nginx.conf` provides SPA routing inside the container image
- the Step 2.5 staging smoke path serves the production frontend through the shared reverse proxy on `127.0.0.1:8088`

## Environment

- `VITE_API_BASE_URL`
  - defaults to `/api/v1`
- `VITE_BACKEND_PROXY_TARGET`
  - defaults to `http://127.0.0.1:8000`
  - used only by the Vite dev proxy so local browser requests to `/api` and `/lti/api` do not require Django CORS middleware

## Design System

- design system reference: [docs/frontend-design-system.md](./docs/frontend-design-system.md)
- default product name: `Student Information System`
- default logo asset: `public/sis-logo.svg`

## Local Run Flow

Start the Django backend first, then run the Vite frontend.

Backend terminal from the repository root:

```bash
. .venv/bin/activate
cd backend
export DJANGO_SECRET_KEY='test-secret-key-with-sufficient-length-1234567890'
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
export MYSQL_DATABASE=modern_sis
export MYSQL_USER=modern_sis
export MYSQL_PASSWORD=modern_sis
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3313
python manage.py migrate --noinput
python manage.py seed_demo_sis
python manage.py runserver 127.0.0.1:8000
```

The runbook assumes the local project database is published on `3313` so it does not collide with a workstation that already has MySQL or MariaDB on `3306`. If your machine is clean and you prefer `3306`, update the Docker port mapping and export `MYSQL_PORT=3306`.

Frontend terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

For containerized staging verification, use `http://127.0.0.1:8088` after starting the staging Compose overlay from `infra/`.

## Container Build

Build the frontend image locally:

```bash
docker build -f frontend/Dockerfile -t modern-sis-frontend:test ./frontend
```

## Verification

Run these checks before treating the Step 2.4 UI as healthy:

```bash
cd frontend
npm run typecheck
npm test
npm run lint
npm run build
```

Install Playwright browsers once per machine:

```bash
cd frontend
npx playwright install chromium
```

Then run browser verification:

```bash
cd frontend
npm run test:e2e
```

For full API-backed verification, also run:

```bash
. .venv/bin/activate
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q --cov=apps --cov-report=term-missing
```

For Phase 3 Step 3.3 LTI verification, including the host-run Django/Vite launch setup, optional Moodle launch flow, and expected `/lti/api/session` behavior, use `../docs/phases/phase-03-moodle-integration/STEP_3_3_TESTING.md`.

## Implemented Step 2.4 Surface

- Rebuilt protected login flow with serious, institution-neutral SIS branding
- Shared application shell with role-specific navigation, access-denied rendering, and mobile drawer navigation
- Student area:
  - profile overview
  - official grades
  - section registration and drops
  - correction-request submission and history
  - transcript download
- Advisor area:
  - assigned-student search
  - unified student profile
  - advising note create and draft update
  - financial-flag visibility
  - official grade history visibility
- Faculty area:
  - assigned section list
  - roster view
  - draft grade entry
- Admin area:
  - operational overview
  - user management
  - student operations for standing overrides, financial flags, note approval, correction review, and grade officialisation
- Reusable UI primitives, loading states, empty states, and browser-tested role journeys
- Phase 3 Step 3.3 LTI pages:
  - `/lti/tools/advising-dashboard` renders validated Moodle launch context, mapped SIS course data, and read-only roster data when SIS RBAC allows it
  - `/lti/tools/registration` renders validated Moodle launch context, mapped SIS student data, and current enrollment data without exposing iframe registration mutations in this slice

## Planned But Not Yet Backed By Phase 2 APIs

These screens are presented as roadmap panels instead of fake implementations:

- student AI co-pilot
- advisor at-risk alerts
- advisor and faculty Moodle engagement views
- wellbeing workflows
- AI audit-log review

These remain governed by the SRS and will be implemented in later phases when the backend contract exists.

## Current Verification Snapshot

- `npm run typecheck` passed
- `npm test -- --reporter=dot` passed with `14` unit/component tests
- `npm run lint` passed
- `npm run build` passed
- `npm run test:e2e` passed with `9` Playwright browser tests

Step 3.3 adds LTI frontend routes backed by `GET /lti/api/session`. Run `npm run typecheck`, `npm run lint`, and `npm run build` after changing these pages.

The full Step 3.3 frontend check sequence is `npm run typecheck`, `npm run lint`, `npm test`, and `npm run build`; it is documented with the backend and Moodle setup in `../docs/phases/phase-03-moodle-integration/STEP_3_3_TESTING.md`.

## Demo Accounts

Run `python manage.py seed_demo_sis` after migrations, then sign in with:

- `admin.demo / DemoPass123!`
- `advisor.demo / DemoPass123!`
- `faculty.demo / DemoPass123!`
- `student.demo1 / DemoPass123!`
- `student.demo2 / DemoPass123!`

If you are also testing the local Moodle slice from Phase 3, the bootstrap Moodle admin account is:

- `admin / ChangeMe123!`

The Moodle REST service user `sis.service` is created manually during the Phase 3 runbook. It is not seeded by `seed_demo_sis`, so choose and record its password locally when you create it.

The seeded dataset includes:

- two student profiles assigned to the demo advisor
- two current sections for the demo faculty
- active enrollments for both students
- attendance history for student and advisor profile views
- two official grades for `student.demo1`
- one draft grade for `student.demo2`
- one financial flag, two advising notes, and one correction request

## Exact Test Process

1. Start MySQL 8 locally.
2. From the repo root, activate the Python environment and run Django migrations.
3. Run `python manage.py seed_demo_sis`.
4. Start Django on `127.0.0.1:8000`.
5. In a second terminal, start the frontend with `npm run dev`.
6. Open `http://127.0.0.1:5173`.
7. Test each role:
   - student: sign in as `student.demo1`, review dashboard, grades, registration, corrections, and wellbeing shell
   - advisor: sign in as `advisor.demo`, search `Temba`, open the unified profile, review notes and flags
   - faculty: sign in as `faculty.demo`, open an assigned section, review the roster, and enter a draft grade
   - admin: sign in as `admin.demo`, review the dashboard and create or manage users

## Auth Note

The current backend returns JWTs in JSON responses and does not yet issue refresh tokens in `httpOnly` cookies. For the Step 2.4 local-development baseline, the frontend stores the session in `sessionStorage` and refreshes tokens through the `/auth/refresh` endpoint. This is a Phase 2 implementation constraint, not the long-term preferred security model.
