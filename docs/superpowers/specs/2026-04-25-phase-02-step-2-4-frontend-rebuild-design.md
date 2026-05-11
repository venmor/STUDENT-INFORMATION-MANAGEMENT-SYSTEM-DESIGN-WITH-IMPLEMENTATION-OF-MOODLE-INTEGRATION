# Phase 2 Step 2.4 Frontend Rebuild Design

## Status

Accepted for implementation on 2026-04-25 based on the user's rebuild brief, `docs/project/modern-sis-setup-guide.md`, and `docs/project/SRS_Modern_SIS.md`.

## Goal

Replace the current generic Step 2.4 frontend with a role-specific, institution-ready Student Information System frontend that looks deliberate, serious, and adoptable by any school, while staying inside the actual Step 2.4 scope and the current Django backend contract.

## Product Naming

- Product name in the UI: `Student Information System`
- Branding posture: school-agnostic and adoptable
- No hardcoded references to a specific institution in navigation, titles, or copy
- Logo handling: neutral default mark and configurable asset slot for a future institution-specific logo

## Design Direction

The frontend should feel administrative, academic, and trustworthy rather than startup-like or promotional. It should prioritise clear information hierarchy, robust table and form patterns, and role-specific workflows over decorative dashboards.

Visual principles:

- cool neutral canvas with strong blue institutional primary
- dense but readable information layout
- strong semantic color usage only where meaning exists
- no generic bright gradients, no playful AI persona, no celebratory wellbeing language
- typography built around `DM Sans`, `Sora`, and `JetBrains Mono`

## Locked Technical Decisions

- React 18 + TypeScript + Vite
- Tailwind CSS with project-specific design tokens
- TanStack Query for server state
- React Router for client routing
- Axios with a configured API client and JWT refresh retry
- Zustand for auth/session state
- Vitest + React Testing Library for component and route tests
- Playwright for end-to-end role journeys

## Step 2.4 Scope Boundary

### In Scope For This Rebuild

- rebuild the frontend file structure and component library
- rebuild login, authenticated shell, sidebar, topbar, mobile navigation, and protected routing
- implement role-specific dashboards for student, advisor, faculty, and admin
- connect all supported Step 2.4 flows to the existing backend endpoints
- improve tests, docs, and verification for the rebuilt frontend

### Not Live-Implemented In Step 2.4

These are allowed as explicit UI placeholders or shells only, because the setup guide places them later or the backend surface does not yet exist:

- live AI co-pilot query execution
- live advisor summarisation execution
- live at-risk alert queue and acknowledgement
- live admin AI audit-log search
- live wellbeing consent, check-in, triage, and coordinator workflows
- LTI-served tool launch flows
- live admin system-health and sync-status telemetry

### Required Treatment For Deferred Items

- keep them visibly present where the design needs them
- label them as planned or unavailable in the current phase
- never fabricate fake data that implies backend support exists
- document the phase dependency in code comments only where necessary and in the Phase 2 docs

## Backend Contract Reality

The current backend supports:

- JWT login and refresh
- role-aware user management
- student profile detail and list
- correction requests
- financial flags
- advising notes and approvals
- course list and detail
- section list/detail/roster
- enrollments, drops, transfers, and bulk preview/commit
- attendance session creation
- grade create/detail/officialise
- transcript download

The current backend does not support the full prompt endpoint map for AI, wellbeing, LTI, sync telemetry, or audit-log browsing. The frontend must be designed to accommodate those features later without blocking Step 2.4.

## Information Architecture

### Shared Shell

- desktop sidebar with role-aware navigation
- topbar with page context, current user, and quick account actions
- mobile drawer navigation
- access-denied screen for wrong-role navigation

### Student Area

- overview dashboard
- my courses
- my grades
- course registration
- correction requests
- transcript action
- optional deferred co-pilot panel shell
- optional deferred wellbeing entry point shell

### Advisor Area

- overview dashboard
- assigned student search
- unified student profile view composed from existing student, grades, advising note, and flag APIs
- deferred at-risk queue shell
- deferred AI summarisation shell

### Faculty Area

- assigned sections overview
- section detail
- roster display
- attendance marking flow based on existing attendance session creation support
- draft grade entry

### Admin Area

- overview dashboard
- user administration
- student operations view
- grade officialisation and related record workflows
- deferred system health, sync status, and AI audit-log shells

## Component Strategy

Build a reusable primitive layer first:

- Button
- Input
- Select
- Textarea
- Card
- Badge
- Table
- Modal
- Skeleton
- EmptyState
- Alert
- Spinner

Then build:

- shell layout components
- role-specific workflow components
- deferred AI/wellbeing/LTI panels that are visibly distinct from live features

## Routing Strategy

- `/login` is outside the app shell
- authenticated routes mount the shell
- role routes render an access-denied page when mismatched
- role home redirects are deterministic
- deferred LTI routes may exist as non-live shells only if they do not imply operational Moodle integration

## State And Data Strategy

- Zustand stores auth tokens and current user summary
- Axios interceptor attaches the access token and retries once on refresh
- TanStack Query handles server reads, invalidation, and optimistic updates where safe
- no duplication of server state into Zustand except auth/session metadata

## Testing Strategy

Frontend rebuild verification must include:

- unit tests for design-system primitives and protected routing
- component tests for critical role widgets
- Playwright role journeys limited to flows supported by the current backend
- explicit documentation of deferred E2E scenarios for later phases

## Documentation Requirements

The rebuild must update:

- `frontend/README.md`
- `docs/phases/phase-02-core-build/README.md`
- `docs/phases/phase-02-core-build/CHANGELOG.md`
- `docs/api/openapi.yaml` only if the frontend-support contract changes

The rebuild must also add:

- `frontend/docs/frontend-design-system.md` capturing the implemented design system and phase deferments

## Risks

- The prompt asks for later-phase AI/wellbeing/LTI features that do not belong to Step 2.4 as live integrations.
- The current frontend already shipped on `main`, so this rebuild should be isolated and reviewed carefully before replacing it.
- Tailwind v4 is currently installed; the rebuild will need to decide whether to align package versions to the new design brief or implement the same token system under the current toolchain with minimal risk.

## Decision

Proceed with a Step 2.4 frontend rebuild that adopts the user's design brief as the visual and structural source of truth, while enforcing strict separation between:

1. live Step 2.4 workflows supported by the existing backend
2. clearly marked later-phase UI shells for AI, wellbeing, LTI, and telemetry
