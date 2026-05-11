# Phase 2 Step 2.4 Frontend Rebuild Implementation Plan

## Outcome

Implemented on `2026-04-25` in the rebuild worktree. The frontend now matches the approved institution-neutral SIS direction, remains aligned with the Step 2.4 backend contract, and explicitly defers later-phase AI, wellbeing, LTI, and telemetry integrations.

Verification snapshot:

- `npm run typecheck` passed
- `npm test -- --reporter=dot` passed with `14` tests
- `npm run lint` passed
- `npm run build` passed
- `npm run test:e2e` passed with `9` browser journeys

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Step 2.4 frontend so it matches the new institutional design brief, stays aligned to the setup guide and SRS, and wires only the workflows that the current backend actually supports.

**Architecture:** Replace the current lightweight Step 2.4 frontend with a component-first frontend organized by primitives, layout, role areas, hooks, and API modules. Keep auth/session state in Zustand, server data in TanStack Query, and use explicit deferred UI shells for later-phase AI, wellbeing, LTI, and telemetry features instead of fake integrations.

**Tech Stack:** React 18, TypeScript, Vite, Tailwind CSS, Zustand, TanStack Query, React Router, Axios, Vitest, React Testing Library, Playwright.

---

## File Structure

### Core frontend files to create or replace

- Replace: `frontend/src/**`
- Create: `frontend/docs/frontend-design-system.md`
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.ts`
- Modify or create: `frontend/tailwind.config.js`
- Modify: `frontend/src/index.css`

### New frontend responsibilities

- `src/api/*`: HTTP client plus per-domain API modules
- `src/components/ui/*`: reusable design-system primitives
- `src/components/layout/*`: shell, sidebar, topbar, mobile nav
- `src/components/student/*`, `advisor/*`, `faculty/*`, `admin/*`: role widgets
- `src/components/ai/*`, `wellbeing/*`: deferred but intentionally designed feature shells
- `src/pages/*`: route-level pages
- `src/hooks/*`: query/mutation wrappers and auth helpers
- `src/stores/authStore.ts`: auth state and token lifecycle
- `src/router.tsx`: route tree and role guards
- `tests/unit/*`: focused unit and component tests
- `tests/e2e/*`: Playwright journeys

## Task 1: Lock package and build configuration

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.ts`
- Create or modify: `frontend/tailwind.config.js`
- Modify: `frontend/src/index.css`

- [ ] Remove or replace dependencies that conflict with the rebuild architecture.
- [ ] Add `zustand`, `@heroicons/react`, `@radix-ui/react-dialog`, `@radix-ui/react-popover`, `@radix-ui/react-select`, `@radix-ui/react-tabs`, `@radix-ui/react-tooltip`, `clsx`, `tailwind-merge`, `@tailwindcss/forms`, `playwright`, and any missing test dependencies.
- [ ] Align Tailwind configuration to the rebuild token system.
- [ ] Load `DM Sans`, `Sora`, and `JetBrains Mono` in the app entry or `index.html`.
- [ ] Add a clean alias strategy for `@/`.
- [ ] Run: `npm install`
- [ ] Run: `npm run build`

## Task 2: Replace auth/session foundation

**Files:**
- Create: `frontend/src/stores/authStore.ts`
- Create: `frontend/src/api/axios.ts`
- Create: `frontend/src/hooks/useAuth.ts`
- Replace: `frontend/src/router.tsx`
- Replace: `frontend/src/App.tsx`
- Replace: `frontend/src/main.tsx`

- [ ] Write failing tests for unauthenticated redirects and wrong-role access behavior.
- [ ] Verify the current tests fail for the new route structure.
- [ ] Implement Zustand auth store with access token, refresh token, user payload, and logout handling.
- [ ] Implement Axios request and refresh retry interceptors against the existing auth endpoints.
- [ ] Implement `ProtectedRoute` and role-aware routing with explicit access-denied rendering.
- [ ] Run: `npm test -- tests/unit/router.test.tsx`

## Task 3: Build design-system primitives first

**Files:**
- Create: `frontend/src/components/ui/Button.tsx`
- Create: `frontend/src/components/ui/Input.tsx`
- Create: `frontend/src/components/ui/Select.tsx`
- Create: `frontend/src/components/ui/Textarea.tsx`
- Create: `frontend/src/components/ui/Card.tsx`
- Create: `frontend/src/components/ui/Badge.tsx`
- Create: `frontend/src/components/ui/Table.tsx`
- Create: `frontend/src/components/ui/Modal.tsx`
- Create: `frontend/src/components/ui/Skeleton.tsx`
- Create: `frontend/src/components/ui/EmptyState.tsx`
- Create: `frontend/src/components/ui/Alert.tsx`
- Create: `frontend/src/components/ui/Spinner.tsx`
- Create: `frontend/src/utils/cn.ts`

- [ ] Write failing unit tests for Button loading state, Input error wiring, and semantic badge rendering.
- [ ] Implement the primitives to satisfy the token system and accessibility requirements.
- [ ] Add responsive table fallback behavior for smaller screens.
- [ ] Run: `npm test -- tests/unit/components-ui.test.tsx`

## Task 4: Build the shared application shell

**Files:**
- Create: `frontend/src/components/layout/AppShell.tsx`
- Create: `frontend/src/components/layout/Sidebar.tsx`
- Create: `frontend/src/components/layout/Topbar.tsx`
- Create: `frontend/src/components/layout/MobileNav.tsx`
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/utils/roleGuards.ts`

- [ ] Build role-aware navigation driven by a single route/navigation map.
- [ ] Use neutral SIS branding and a configurable logo slot.
- [ ] Implement the responsive shell states for mobile, tablet, and desktop.
- [ ] Ensure wrong-role users see an access denied page instead of a silent redirect loop.
- [ ] Run: `npm run build`

## Task 5: Rebuild live student workflows

**Files:**
- Create: `frontend/src/api/students.ts`
- Create: `frontend/src/api/courses.ts`
- Create: `frontend/src/api/enrollments.ts`
- Create: `frontend/src/api/grades.ts`
- Create: `frontend/src/hooks/useStudents.ts`
- Create: `frontend/src/hooks/useCourses.ts`
- Create: `frontend/src/hooks/useEnrollments.ts`
- Create: `frontend/src/hooks/useGrades.ts`
- Create: `frontend/src/components/student/CourseCard.tsx`
- Create: `frontend/src/components/student/GradeHistoryTable.tsx`
- Create: `frontend/src/components/student/QuickStatsPanel.tsx`
- Create: `frontend/src/components/student/EnrollmentWizard.tsx`
- Create: `frontend/src/components/ai/CopilotDrawer.tsx`
- Create: `frontend/src/components/ai/CopilotDisclaimer.tsx`
- Create: `frontend/src/pages/student/Dashboard.tsx`
- Create: `frontend/src/pages/student/MyCourses.tsx`
- Create: `frontend/src/pages/student/MyGrades.tsx`
- Create: `frontend/src/pages/student/CourseRegistration.tsx`

- [ ] Write failing tests for student enrollment interaction and deferred co-pilot rendering.
- [ ] Implement live grades, courses, registration, corrections, and transcript actions against the existing backend.
- [ ] Implement co-pilot as a visually complete deferred shell because live AI endpoints are not in Step 2.4.
- [ ] Run targeted tests and smoke build.

## Task 6: Rebuild live advisor and faculty workflows

**Files:**
- Create: `frontend/src/api/advising.ts` or keep advising operations in `students.ts` if simpler
- Create: `frontend/src/components/advisor/StudentSearchBar.tsx`
- Create: `frontend/src/components/advisor/UnifiedStudentProfile.tsx`
- Create: `frontend/src/components/advisor/AdvisingNoteEditor.tsx`
- Create: `frontend/src/components/advisor/AtRiskAlertQueue.tsx`
- Create: `frontend/src/components/advisor/AISummarisationPanel.tsx`
- Create: `frontend/src/components/faculty/SectionTabs.tsx`
- Create: `frontend/src/components/faculty/RosterTable.tsx`
- Create: `frontend/src/components/faculty/InlineGradeEntry.tsx`
- Create: `frontend/src/components/faculty/AttendanceMarker.tsx`
- Create: `frontend/src/pages/advisor/Dashboard.tsx`
- Create: `frontend/src/pages/advisor/StudentProfile.tsx`
- Create: `frontend/src/pages/faculty/Dashboard.tsx`
- Create: `frontend/src/pages/faculty/SectionDetail.tsx`

- [ ] Write failing tests for at-risk row rendering and faculty draft grade entry behavior.
- [ ] Implement advisor unified profile using the existing student, grades, note, and flag endpoints.
- [ ] Implement at-risk and summarisation panels as explicit deferred shells with no fake data persistence.
- [ ] Implement faculty roster, attendance session creation, and draft grade entry using live endpoints.
- [ ] Run targeted tests and smoke build.

## Task 7: Rebuild live admin workflows and deferred operational views

**Files:**
- Create: `frontend/src/components/admin/SystemHealthCard.tsx`
- Create: `frontend/src/components/admin/ActivityFeed.tsx`
- Create: `frontend/src/components/admin/UserTable.tsx`
- Create: `frontend/src/components/admin/AuditLogSearch.tsx`
- Create: `frontend/src/components/admin/SyncStatusBadge.tsx`
- Create: `frontend/src/pages/admin/Dashboard.tsx`
- Create: `frontend/src/pages/admin/Users.tsx`
- Create: `frontend/src/pages/admin/Courses.tsx`
- Create: `frontend/src/pages/admin/AuditLog.tsx`

- [ ] Implement live admin user and student operations using existing endpoints.
- [ ] Render system health, sync monitor, and AI audit log as deferred operational shells tied to later phases.
- [ ] Ensure admin copy never implies those backend services exist today.
- [ ] Run targeted tests and smoke build.

## Task 8: Wellbeing and LTI page treatment

**Files:**
- Create: `frontend/src/components/wellbeing/WellbeingConsentPage.tsx`
- Create: `frontend/src/components/wellbeing/WellbeingCheckInForm.tsx`
- Create: `frontend/src/components/wellbeing/MoodSelector.tsx`
- Create: `frontend/src/components/wellbeing/WellbeingEscalationScreen.tsx`
- Create: `frontend/src/components/wellbeing/QuickExitButton.tsx`
- Create: `frontend/src/pages/student/Wellbeing.tsx`
- Create: `frontend/src/pages/lti/AdvisingTool.tsx`
- Create: `frontend/src/pages/lti/RegistrationTool.tsx`

- [ ] Implement non-live shells only, with copy that explicitly states the features depend on later backend phases and governance approvals.
- [ ] Preserve the intended visual system and safety language for later activation.
- [ ] Do not claim these are operational Step 2.4 features.

## Task 9: Documentation and verification

**Files:**
- Create: `frontend/docs/frontend-design-system.md`
- Modify: `frontend/README.md`
- Modify: `docs/phases/phase-02-core-build/README.md`
- Modify: `docs/phases/phase-02-core-build/CHANGELOG.md`
- Modify: `CHANGELOG.md`

- [ ] Document the design system, route structure, and which requested prompt items were deferred beyond Step 2.4.
- [ ] Add updated local run and test instructions.
- [ ] Run: `npm test`
- [ ] Run: `npm run lint`
- [ ] Run: `npm run build`
- [ ] Run: `npx playwright test` for the journeys that are truly supported in this phase
- [ ] Record any still-deferred tests tied to unavailable backend endpoints

## Spec Coverage Check

- Design system, serious academic visual tone, and neutral SIS branding: covered by Tasks 1, 3, and 4
- Role-specific dashboards and routing: covered by Tasks 2, 4, 5, 6, and 7
- Live Step 2.4 backend wiring: covered by Tasks 5, 6, and 7
- Deferred AI/wellbeing/LTI handling: covered by Tasks 5, 6, 7, and 8
- Testing and documentation: covered by Task 9

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-25-phase-02-step-2-4-frontend-rebuild.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration
2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints
