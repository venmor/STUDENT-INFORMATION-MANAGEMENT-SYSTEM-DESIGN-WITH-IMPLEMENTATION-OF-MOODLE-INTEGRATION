# Phase 4.1 Analytics and Vector Store Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 4.1 data and retrieval foundation without implementing co-pilot, summarisation, at-risk, wellbeing, or admissions features.

**Architecture:** Add `apps.analytics` for read-oriented SIS/Moodle analytics snapshots and `apps.knowledge` for institutional knowledge metadata, chunking, embeddings, vector-store interaction, ingestion, and retrieval testing. Add a small admin-only `/admin/ai-foundation` verification page that calls admin-only APIs and never invokes an LLM.

**Tech Stack:** Django 5, Django REST Framework, MySQL, existing audit/notification/RBAC services, Qdrant HTTP API via `requests`, deterministic local embeddings, React 18, TypeScript, TanStack Query, Tailwind, Heroicons.

---

## Component Responsibility Map

### Backend Analytics
- `backend/apps/analytics/models.py`: `AnalyticsETLRun`, `StudentAnalyticsSnapshot`, status choices.
- `backend/apps/analytics/selectors.py`: snapshot filters, latest run, summary queries.
- `backend/apps/analytics/services.py`: ETL orchestration, per-student snapshot calculation, audit/notification hooks, summary data.
- `backend/apps/analytics/serializers.py`: admin API response shaping.
- `backend/apps/analytics/views.py`: thin admin API controllers.
- `backend/apps/analytics/urls.py`: route declarations.
- `backend/apps/analytics/management/commands/run_analytics_etl.py`: ETL command.
- `backend/apps/analytics/management/commands/seed_analytics_demo.py`: safe repeatable demo data.
- `backend/apps/analytics/tests/`: model/service/API/command tests.

### Backend Knowledge
- `backend/apps/knowledge/models.py`: `KnowledgeSource`, `KnowledgeChunk`, `KnowledgeIngestionRun`, status/type/visibility choices.
- `backend/apps/knowledge/chunking.py`: approximate token chunking with overlap.
- `backend/apps/knowledge/embeddings.py`: deterministic provider and optional OpenAI-compatible provider abstraction.
- `backend/apps/knowledge/vector_store.py`: Qdrant HTTP wrapper and in-memory test fallback.
- `backend/apps/knowledge/services.py`: seed/source preparation, ingestion, retrieval, audit/notification hooks, summary.
- `backend/apps/knowledge/serializers.py`: admin API response shaping.
- `backend/apps/knowledge/views.py`: thin admin API controllers.
- `backend/apps/knowledge/urls.py`: route declarations.
- `backend/apps/knowledge/management/commands/seed_knowledge_demo.py`: safe demo institutional sources.
- `backend/apps/knowledge/management/commands/ingest_knowledge_base.py`: chunk/embed/upsert command.
- `backend/apps/knowledge/management/commands/query_knowledge_base.py`: retrieval-only command.
- `backend/apps/knowledge/tests/`: chunking, embedding, vector-store, service, API, command tests.

### Frontend
- `frontend/src/types/aiFoundation.ts`: analytics/knowledge response types.
- `frontend/src/api/aiFoundation.ts`: admin API functions only.
- `frontend/src/hooks/useAIFoundation.ts`: TanStack Query hooks/mutations.
- `frontend/src/features/ai-foundation/components/*`: reusable summary, analytics readiness, knowledge tables, retrieval test, scope note.
- `frontend/src/pages/admin/AIFoundation.tsx`: thin route page composing feature components.
- `frontend/src/router.tsx`, `Sidebar.tsx`, `AppShell.tsx`: admin route/navigation/heading.
- `frontend/tests/unit/ai-foundation*.test.tsx`: route, sidebar, page states, retrieval results.

### Config and Docs
- `backend/sis_backend/settings.py`: install apps, Qdrant/embedding/chunk settings.
- `backend/sis_backend/urls.py`: include analytics and knowledge URLs.
- `backend/apps/accounts/access.py`: register admin-only routes.
- `infra/docker-compose.yml`, `infra/docker-compose.dev.yml`, env examples: Qdrant env/port/provider defaults.
- Docs/changelogs: phase 4 README/changelog, docs index, SRS, setup guide, backend/frontend/root docs.

## Task 1: Analytics Tests First
- [ ] Create `backend/apps/analytics/tests/test_services.py` with tests for ETL creating snapshots, dry-run behavior, stored Moodle snapshot use, and missing optional data.
- [ ] Create `backend/apps/analytics/tests/test_api_and_commands.py` with tests for admin-only APIs and `seed_analytics_demo`/`run_analytics_etl` command output.
- [ ] Run `pytest -q apps/analytics/tests/` and confirm failure from missing `apps.analytics`.

## Task 2: Knowledge Tests First
- [ ] Create `backend/apps/knowledge/tests/test_chunking_embeddings_vector.py` for chunk overlap, deterministic vector stability, in-memory retrieval, and Qdrant failure messages.
- [ ] Create `backend/apps/knowledge/tests/test_services_api_commands.py` for demo seeding, ingestion with mocked/in-memory vector store, retrieval-only query, admin-only APIs, audit events, and no LLM behavior.
- [ ] Run `pytest -q apps/knowledge/tests/` and confirm failure from missing `apps.knowledge`.

## Task 3: Frontend Tests First
- [ ] Create route/sidebar/page tests for `/admin/ai-foundation`.
- [ ] Mock `useAIFoundation` hooks and assert summary cards, analytics panel, source table, labelled retrieval input, scope note, empty/error/loading states, and no emoji text.
- [ ] Run targeted Vitest tests and confirm failure from missing route/page.

## Task 4: Implement Backend Analytics
- [ ] Add `apps.analytics` files per responsibility map.
- [ ] Compute attendance average from existing `AttendanceRecord` values.
- [ ] Count active financial flags, active enrollments, draft/official grades, stored Moodle snapshots, latest Moodle access, and existing GPA.
- [ ] Implement dry-run without snapshot writes.
- [ ] Add admin-only API routes and RBAC registry entries.
- [ ] Run analytics tests until green.

## Task 5: Implement Backend Knowledge and Vector Store
- [ ] Add `apps.knowledge` files per responsibility map.
- [ ] Implement deterministic embeddings with fixed dimensionality and no network.
- [ ] Implement optional OpenAI-compatible provider behind env config, disabled by default.
- [ ] Implement Qdrant HTTP wrapper plus in-memory fallback for tests/local command option.
- [ ] Seed demo institutional sources and ingest chunks with 512-token/64-overlap defaults.
- [ ] Add admin-only API routes and RBAC registry entries.
- [ ] Run knowledge tests until green.

## Task 6: Compose, Settings, and Frontend UI
- [ ] Add analytics/knowledge apps and env settings.
- [ ] Wire Qdrant env vars and dev port mapping.
- [ ] Add admin-only `/admin/ai-foundation` route, sidebar item, AppShell heading, API/types/hooks, and componentized page.
- [ ] Run targeted frontend tests until green.

## Task 7: Documentation and Verification
- [ ] Update phase 4 docs, phase index, SRS, setup guide, READMEs, OpenAPI, and changelog.
- [ ] Run backend verification: `check`, migration dry-run, analytics/knowledge/reporting/calendar/audit/notifications/integration tests, and `ruff check .`.
- [ ] Run frontend verification: `typecheck`, `lint`, `test`, `build`.
- [ ] Run `git diff --check`.
- [ ] Commit as `feat: add phase 4.1 analytics and vector store foundation`, push feature branch, merge to main, push main.

## Self-Review
- The plan maps every requested backend layer to a file responsibility.
- It keeps Step 4.1 retrieval-only and excludes co-pilot, summarisation, at-risk, wellbeing, admissions, and student-private document embeddings.
- It uses TDD for new backend and frontend behavior.
- It includes Qdrant wiring while preserving later-phase profile isolation.
