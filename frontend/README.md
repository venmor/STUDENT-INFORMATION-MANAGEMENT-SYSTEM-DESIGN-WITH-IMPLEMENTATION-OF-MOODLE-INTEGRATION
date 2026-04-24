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
