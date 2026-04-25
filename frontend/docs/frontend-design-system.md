# Frontend Design System

## Purpose

This document records the Phase 2 Step 2.4 frontend rebuild for the Student Information System. It translates the approved UI direction into a maintainable implementation baseline that any school can later brand for its own identity.

The frontend is intentionally institution-neutral:

- product name: `Student Information System`
- visual language: serious, operational, academic
- target users: students, advisors, faculty, and administrators
- target device range: responsive browser UI from `375px` upward

## Step 2.4 Scope Boundary

Step 2.4 covers the frontend baseline only:

- React 18 + TypeScript + Vite application scaffold
- Tailwind-based design system and reusable UI primitives
- role-protected routing
- authenticated app shell
- live student, advisor, faculty, and admin flows backed by the verified Step 2.3 APIs

The following surfaces are intentionally designed now but not connected to live backend workflows yet:

- student AI co-pilot orchestration
- advisor at-risk alert engine and acknowledgement persistence
- Moodle engagement analytics
- wellbeing data collection and escalation workflows
- admin AI audit-log search
- LTI-served launch experiences

Those remain visible as clearly labelled deferred panels or shell pages so the final information architecture is present without fabricating backend behaviour.

## Technical Baseline

- framework: React 18
- language: TypeScript strict mode
- build tool: Vite
- styling: Tailwind CSS v3 with custom tokens
- server state: TanStack Query v5
- routing: React Router v6
- HTTP client: Axios with JWT interceptor
- local auth state: Zustand persisted in `sessionStorage`
- unit tests: Vitest + React Testing Library
- browser tests: Playwright

## Brand Tokens

### Color

- `primary`: `#1E4E8C`
- `primary.dark`: `#163A6B`
- `primary.light`: `#E8F0FE`
- `secondary`: `#0D9488`
- `secondary.dark`: `#0F766E`
- `secondary.light`: `#CCFBF1`
- `danger`: `#B91C1C`
- `warning`: `#B45309`
- `success`: `#15803D`
- `info`: `#0369A1`
- `neutral.50`: `#F8FAFC`
- `neutral.100`: `#F1F5F9`
- `neutral.200`: `#E2E8F0`
- `neutral.300`: `#CBD5E1`
- `neutral.400`: `#94A3B8`
- `neutral.500`: `#64748B`
- `neutral.700`: `#334155`
- `neutral.900`: `#0F172A`
- `wellbeing.accent`: `#7C3AED`
- `wellbeing.soft`: `#F5F3FF`
- `wellbeing.muted`: `#EDE9FE`

### Typography

- primary UI font: `DM Sans`
- monospace font: `JetBrains Mono`
- display accent font: `Sora`

### Layout

- max content width: `1280px`
- sidebar width: `256px`
- mobile topbar height: `64px`
- card radius: `12px`
- modal radius: `16px`
- card padding: `p-6` desktop, `p-4` mobile

## Component Rules

### Buttons

- minimum touch target: `44x44`
- all interactive controls use visible focus rings
- primary buttons use `primary`
- destructive actions use `danger`
- loading buttons preserve width and replace text with a spinner

### Inputs

- visible labels are mandatory
- invalid state uses `danger` border and message text
- labels and errors are connected with `htmlFor`, `id`, and `aria-describedby`

### Cards

- white background
- subtle border
- restrained shadow
- semantic left-border accent only when conveying operational meaning

### Tables

- neutral header row
- zebra support
- hover state on body rows
- monospace for codes, IDs, and numeric values
- always pair with loading and empty-state handling

## Role Layouts

### Student

- primary concerns: GPA, standing, courses, grades, registration
- co-pilot remains student-only
- wellbeing route exists as a safeguarded shell, not a fake live service

### Advisor

- primary concerns: advisee search, unified student profile, notes, risk context
- unified profile uses tabbed structure for academic record, attendance, Moodle engagement, notes, and flags
- at-risk alert queue remains visually reserved but explicitly deferred pending later AI phases

### Faculty

- primary concerns: assigned sections, roster visibility, draft grade entry
- section switching is tab-based
- grade entry is draft-only in the faculty UI

### Admin

- primary concerns: user administration, operational oversight, controlled academic interventions
- user directory is live
- system health and AI audit screens are reserved as later-phase operational panels

## Accessibility Requirements

- WCAG 2.2 AA target for core flows
- visible focus states on every interactive control
- color never carries meaning alone
- keyboard navigation works across forms, tabs, dialogs, and navigation
- modals trap focus and close on `Escape`
- tables include labels or captions
- wellbeing quick exit remains a native `<a>` element

## Testing Strategy

### Unit Coverage

Unit coverage focuses on the reusable surfaces most likely to regress:

- button loading and disable states
- form accessibility wiring
- protected route behaviour
- advisor alert row semantics
- co-pilot disclaimer and deferred shell rendering
- wellbeing check-in gating
- login form failure and submission states

### Browser Coverage

Playwright covers Step 2.4 browser journeys with mocked API responses:

- role-based login redirects
- student registration interaction
- advisor student-profile navigation
- faculty draft-grade submission
- admin user creation
- wellbeing shell visibility

## Local Verification Commands

```bash
cd frontend
npm install
npm test -- --reporter=dot
npm run lint
npm run build
npm run test:e2e
```

If another local MySQL or MariaDB service already owns port `3306`, run the backend container on `3313` and set `MYSQL_PORT=3313` before starting Django.

## Deferred Features Record

The following UI surfaces remain intentionally non-operational until their corresponding backend phases:

- AI co-pilot response generation
- advisor at-risk engine and persistence
- AI summarisation persistence workflow
- wellbeing consent, submission, and escalation storage
- admin AI audit log
- Moodle analytics and LTI launch flows

These are documented here so later phases extend the same information architecture rather than rebuilding the frontend again.
