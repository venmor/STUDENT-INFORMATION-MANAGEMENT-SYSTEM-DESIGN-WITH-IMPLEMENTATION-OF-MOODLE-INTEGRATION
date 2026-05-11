# Phase 2 Step 2.4 Frontend Implementation Plan

## Status

- Date: 2026-04-24
- Phase: 2
- Step: 2.4
- Branch: `feat/phase-02-step-2-4-frontend`
- Source requirements:
  - `docs/project/modern-sis-setup-guide.md`
  - `docs/project/SRS_Modern_SIS.md`

## Goal

Implement the first real React frontend for Modern SIS using React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router, and Axios. The frontend must provide protected, role-aware navigation and wire the available Step 2.3 REST endpoints into usable student, advisor, faculty, and admin workflows.

## Required Step 2.4 Outcomes

1. Scaffold the frontend in `frontend/` with Vite React TypeScript.
2. Install and configure Tailwind CSS, TanStack Query, React Router, and Axios.
3. Implement role-specific dashboards:
   - Student: profile, grades, enrollment actions, transcript download, correction requests
   - Advisor: student search, unified profile view, advising notes
   - Faculty: section list, roster, grade entry
   - Admin: user management, student management, academic operations
4. Enforce protected routes and role-based route access.
5. Connect frontend forms to the verified REST API endpoints.
6. Add frontend tests and verification.
7. Update Phase 2 documentation to reflect the implemented UI surface and the remaining gap to Step 2.5.

## Backend Reality Check

The Step 2.3 backend exposes these frontend-usable domains today:

- Auth: login, refresh, role probes
- Users: list, create, update, deactivate, reset password, access logs, change password
- Students: list, detail, advisor assignment, financial flags, advising notes, correction requests, transcript
- Academics: courses, sections, roster, enrollments, attendance sessions, grades

The SRS also references:

- student AI co-pilot
- at-risk alerts
- Moodle engagement views
- wellbeing workflows
- AI audit-log review
- admin system status tooling

Those are not part of the current Step 2.3 backend contract and belong to later phases or later Phase 2 steps. Step 2.4 will therefore expose those areas as clearly marked roadmap panels rather than inventing unsupported API calls.

## Implementation Approach

### 1. Frontend architecture

- Use route-based code splitting with React Router.
- Use a shared authenticated app shell with role-aware navigation.
- Use TanStack Query for server data and Axios for transport.
- Store access and refresh tokens in session storage for this Phase 2 local-development baseline.
  - This differs from the long-term SRS preference for `httpOnly` refresh cookies.
  - Rationale: the current backend exposes token JSON responses only and does not issue refresh cookies yet.
  - This deviation must be documented as a Phase 2 constraint, not hidden.

### 2. Role-aware surfaces

- Student:
  - login
  - dashboard summary
  - student profile
  - official grades list
  - active enrollments and section self-enrollment
  - transcript download
  - correction-request submission and history
  - placeholder AI co-pilot panel
- Advisor:
  - assigned student list
  - unified student profile with attendance percentages, financial flags, grade history, advising notes
  - draft advising note create/update
  - placeholder at-risk and Moodle engagement panels
- Faculty:
  - assigned sections
  - section roster
  - grade entry for enrolled students
  - grade visibility scoped to faculty-owned sections
- Admin:
  - user management
  - student management
  - financial-flag update flow
  - grade officialisation and update
  - placeholder system-status panel derived only from currently available APIs

### 3. Testing strategy

- Unit/integration tests with Vitest and Testing Library for:
  - protected routing
  - login/session bootstrapping
  - role-based navigation
  - representative dashboard flows
  - form submissions and error states
- Production build verification with `npm run build`
- Lint verification with `npm run lint`

## Risks

### Missing backend endpoints

- AI co-pilot, at-risk alerts, wellbeing, Moodle engagement, and full admin system status are not available yet.
- Mitigation: ship explicit placeholder panels with requirement references so the UI is honest and Phase 3 work is visually anticipated.

### Token storage trade-off

- The SRS long-term security posture prefers `httpOnly` refresh cookies.
- Current Step 2 backend does not expose cookie-based refresh, so the frontend must temporarily store tokens client-side.
- Mitigation: document the deviation, keep the auth module isolated, and make future cookie migration straightforward.

### No CORS middleware in backend

- The frontend dev server must not depend on cross-origin browser calls.
- Mitigation: use the Vite dev proxy for `/api`.

## Verification Plan

1. Run frontend tests.
2. Run frontend lint.
3. Run production build.
4. Start the Vite dev server.
5. Smoke-test the login screen and protected navigation in a browser session.
6. Update phase docs with the verified Step 2.4 result and whether Step 2.5 is unblocked.

## Implementation Result

- Frontend scaffolded in `frontend/` with Vite, React 18, TypeScript, Tailwind CSS v4, TanStack Query, React Router, Axios, and Vitest.
- Role-aware protected routing implemented for student, advisor, faculty, admin, and shared account-security routes.
- Student workflows implemented for profile overview, official grades, transcript download, section registration and drops, and correction requests.
- Advisor workflows implemented for assigned-student search, unified student profile, advising note create/update, financial-flag visibility, and official grade visibility.
- Faculty workflows implemented for assigned sections, section rosters, and draft grade entry.
- Admin workflows implemented for operational overview, user management, standing overrides, financial-flag management, advising-note approval, correction review, and grade officialisation.
- Explicit roadmap panels were added for AI co-pilot, at-risk alerts, Moodle engagement, wellbeing, and AI audit surfaces that do not yet have a backend contract.
- Minimal backend support additions were delivered for Step 2.4:
  - login `student_profile_id`
  - student-visible programme section catalog reads
  - enrollment list reads

## Verification Result

- Frontend verification passed:
  - `npm test`
  - `npm run lint`
  - `npm run build`
- Backend verification passed on a disposable `mysql:8` database:
  - `python manage.py check`
  - `python manage.py makemigrations --check --dry-run`
  - `python manage.py migrate --noinput`
  - `pytest -q --cov=apps --cov-report=term-missing`
- Latest backend verification result: `45` passing tests and `93%` total backend coverage.
- Step 2.5 is the next implementation step after this slice.
