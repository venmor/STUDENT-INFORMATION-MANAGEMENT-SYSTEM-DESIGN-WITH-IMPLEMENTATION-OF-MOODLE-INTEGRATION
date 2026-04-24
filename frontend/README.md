# Frontend

This directory contains the React 18 + TypeScript + Vite frontend delivered in Phase 2 Step 2.4.

## Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS v4 via `@tailwindcss/vite`
- TanStack Query
- React Router
- Axios
- Vitest + Testing Library

## Commands

```bash
npm install
npm run dev
npm test
npm run lint
npm run build
```

## Environment

- `VITE_API_BASE_URL`
  - defaults to `/api/v1`
- `VITE_BACKEND_PROXY_TARGET`
  - defaults to `http://127.0.0.1:8000`
  - used only by the Vite dev proxy so local browser requests do not require Django CORS middleware

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
export MYSQL_PORT=3306
python manage.py migrate --noinput
python manage.py runserver 127.0.0.1:8000
```

Frontend terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Verification

Run these checks before treating the Step 2.4 UI as healthy:

```bash
cd frontend
npm test
npm run lint
npm run build
```

For full API-backed verification, also run:

```bash
. .venv/bin/activate
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q --cov=apps --cov-report=term-missing
```

## Implemented Step 2.4 Surface

- Protected login flow with role-aware route access
- Shared application shell with role-specific navigation
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

## Planned But Not Yet Backed By Phase 2 APIs

These screens are presented as roadmap panels instead of fake implementations:

- student AI co-pilot
- advisor at-risk alerts
- advisor and faculty Moodle engagement views
- wellbeing workflows
- AI audit-log review

These remain governed by the SRS and will be implemented in later phases when the backend contract exists.

## Auth Note

The current backend returns JWTs in JSON responses and does not yet issue refresh tokens in `httpOnly` cookies. For the Step 2.4 local-development baseline, the frontend stores the session in `sessionStorage` and refreshes tokens through the `/auth/refresh` endpoint. This is a Phase 2 implementation constraint, not the long-term preferred security model.
