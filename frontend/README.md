# Frontend Source for Objective 1

The frontend implements the Objective 1 user interface using React, Vite, TypeScript, Tailwind CSS, TanStack Query, and the shared SIS API client.

## Implemented Areas

- Login and authenticated application shell.
- Administrator workflows for users, academic structure, Moodle synchronization, audit activity, reports, calendar, and documents.
- Advisor workflows for student search and unified student profile review.
- Faculty workflows for class rosters and grade entry.
- Student workflows for dashboard, registration, grades, calendar, notifications, and documents.
- Moodle/LTI-facing tool routes for embedded advising and registration workflows.

## Verification Commands

```bash
npm ci
npm run typecheck
npm run lint
npm test -- --reporter=dot
npm run build
```
