# Phase 4.2 Student Service Co-pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a source-grounded, auditable, student-facing co-pilot over Step 4.1 institutional knowledge and safe student context.

**Execution status:** Completed and verified on 2026-05-02 in branch `feature/phase-04-2-student-service-copilot`.

**Architecture:** Add a focused `apps.copilot` backend app that orchestrates retrieval, provider calls, safety, persistence, and audit logging while reusing `apps.knowledge` and `apps.analytics`. Add a componentized student frontend feature at `/student/copilot` with session history, accessible chat states, citations, suggested actions, and deterministic local demo behavior.

**Tech Stack:** Django 5, Django REST Framework, MySQL, existing RBAC/audit/document/calendar/analytics/knowledge services, Qdrant through Step 4.1, deterministic local provider, optional OpenAI-compatible provider, React 18, TypeScript, Vite, TanStack Query, Tailwind, Heroicons.

---

## Component Responsibility Map

### Backend `apps/copilot`
- `models.py`: `CopilotSession`, `CopilotMessage`, `AIAuditLog`, `CopilotFeedback`, choices and indexes.
- `serializers.py`: query/session/message/feedback validation and API response shaping.
- `permissions.py`: role and ownership helpers.
- `selectors.py`: safe student context, session queryset, message queryset, source reference shaping.
- `safety.py`: question validation constants, secret redaction, prompt-injection flagging, confidence selection, fallback text.
- `prompts.py`: system prompt and provider prompt assembly.
- `providers.py`: deterministic provider, OpenAI-compatible provider, provider selection.
- `services.py`: create/archive sessions, run query flow, persist messages, suggested actions, audit events.
- `views.py`: thin DRF views.
- `urls.py`: student co-pilot routes.
- `management/commands/seed_copilot_demo.py`: repeatable demo seeding.
- `management/commands/test_copilot_query.py`: deterministic command-line query verification.
- `tests/`: model, service, provider, permission, API, command, and safety tests.

### Frontend
- `frontend/src/types/copilot.ts`: API/domain types.
- `frontend/src/api/copilot.ts`: co-pilot API client.
- `frontend/src/hooks/useCopilot.ts`: query/session state and mutation hooks.
- `frontend/src/pages/student/Copilot.tsx`: thin route page.
- `frontend/src/features/copilot/components/*`: chat shell, transcript, bubbles, composer, thinking indicator, source panel, session list, safety notice, empty/error states, example prompts, suggested actions.
- `frontend/src/router.tsx`, `Sidebar.tsx`, `AppShell.tsx`, `StudentDashboard.tsx`: student route/navigation/links/headings.
- `frontend/tests/unit/student-copilot*.test.tsx`: route, sidebar, page workflow, accessibility, and rendered response tests.

### Config And Docs
- `backend/sis_backend/settings.py`: install app and AI provider settings.
- `backend/sis_backend/urls.py`: include copilot URLs.
- `backend/apps/accounts/access.py`: register route policies.
- `docs/phases/phase-04-ai-foundation/README.md`, `CHANGELOG.md`, `docs/phases/README.md`, SRS, setup guide, backend/frontend/root READMEs, root changelog.

## Task 1: Backend Tests First
- [ ] Add `backend/apps/copilot/tests/test_services.py` for deterministic source-grounded answer, no-source fallback, audit creation, safe student context, provider failure, top-k retrieval limit, and secret redaction.
- [ ] Add `backend/apps/copilot/tests/test_api_permissions.py` for student query/session lifecycle, unauthenticated 401, advisor/faculty denial, other-student session denial, validation errors, source/action/disclaimer payloads, and feedback ownership.
- [ ] Add `backend/apps/copilot/tests/test_commands.py` for `seed_copilot_demo` and `test_copilot_query`.
- [ ] Run `pytest -q apps/copilot/tests/` from `backend`; expected result before implementation: failure because `apps.copilot` does not exist.

## Task 2: Backend Implementation
- [ ] Create `apps/copilot` files from the responsibility map.
- [ ] Add model migration.
- [ ] Wire app in settings, URLs, and access policy.
- [ ] Reuse `apps.knowledge.services.test_knowledge_retrieval` for retrieval and do not duplicate vector-store logic.
- [ ] Keep prompt/context assembly bounded and free of private document contents.
- [ ] Run copilot tests until green.

## Task 3: Frontend Tests First
- [ ] Add route/sidebar test for `/student/copilot` and student-only access.
- [ ] Add page workflow test covering examples, composer label, submit, thinking state, answer, citations, confidence, suggested actions, low-confidence disclaimer, error retry, and send-disabled state.
- [ ] Run targeted Vitest tests; expected result before implementation: failure because route/components are missing.

## Task 4: Frontend Implementation
- [ ] Add `types`, `api`, `hook`, thin page, and focused components.
- [ ] Add student sidebar item and AppShell heading.
- [ ] Link student dashboard co-pilot entry to `/student/copilot`.
- [ ] Preserve existing design system, Heroicons, accessible labels, `aria-live` thinking/error states, and responsive source panel.
- [ ] Replace the old deferred co-pilot drawer behavior or remove it from the dashboard if it conflicts with the real route.
- [ ] Run targeted frontend tests until green.

## Task 5: Documentation And Verification
- [ ] Update Phase 4 docs, SRS/setup guide, READMEs, changelogs, and command instructions.
- [ ] Run backend verification: `python manage.py check`, migration dry-run, copilot/knowledge/analytics/audit/notifications/integration tests, and `ruff check .`.
- [ ] Run frontend verification: typecheck, lint, tests, and build.
- [ ] Run `git diff --check`.
- [ ] Commit as `feat: add phase 4.2 student service co-pilot`.
- [ ] Push feature branch, merge to local `main`, push `main`, and update local `main`.

## Self-Review
- The plan implements Step 4.2 only and explicitly excludes staff summarisation, at-risk scoring, wellbeing, admissions, and SIS mutation actions.
- Backend layers are separate and testable.
- Frontend route is split by responsibility and keeps the page thin.
- Tests are written before implementation where practical.
- Local demo and tests do not require internet, live Qdrant, or a paid provider.
