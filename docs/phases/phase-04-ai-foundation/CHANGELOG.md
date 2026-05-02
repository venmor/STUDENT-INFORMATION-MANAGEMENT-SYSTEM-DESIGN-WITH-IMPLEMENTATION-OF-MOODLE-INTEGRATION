# Phase 4 Changelog

## [Unreleased]

### Added
- Step 4.1 `apps.analytics` backend app with `AnalyticsETLRun`, `StudentAnalyticsSnapshot`, selectors, services, serializers, admin-only APIs, and ETL/demo commands.
- Step 4.1 `apps.knowledge` backend app with institutional knowledge source metadata, chunk records, ingestion runs, chunking, deterministic embeddings, Qdrant/in-memory vector-store wrappers, retrieval-only test command, demo seed command, and admin-only APIs.
- Optional Qdrant later-phase Compose service wiring with persisted storage and local dev port exposure.
- Environment template values for Qdrant, embedding provider selection, deterministic local embeddings, and knowledge chunk sizing.
- Admin `/admin/ai-foundation` UI for analytics readiness, knowledge source status, vector-store health, ingestion runs, and retrieval-only testing.
- Backend and frontend tests for analytics ETL, permissions, knowledge ingestion, deterministic retrieval, Qdrant failure handling, admin API access, route registration, labelled retrieval input, empty/error/loading states, scope note, and no-emoji page text.
- Step 4.2 `apps.copilot` backend app with `CopilotSession`, `CopilotMessage`, `AIAuditLog`, optional `CopilotFeedback`, serializers, permissions, selectors, services, prompts, safety helpers, provider abstraction, student APIs, and demo/test commands.
- Deterministic local co-pilot provider for offline tests and demos, plus optional OpenAI-compatible provider configuration through environment variables.
- Student `/student/copilot` UI with reusable co-pilot components, source panel, recent sessions, example prompts, thinking indicator, error retry, confidence badges, suggested action links, and accessible labelled composer.
- Backend and frontend tests for co-pilot service behavior, permissions, source references, no-source fallback, audit redaction, provider failure, top-k retrieval, commands, route protection, sidebar navigation, chat submission, thinking/error states, and no-emoji page text.

### Changed
- Phase sequencing now records Step 3.5G Admissions / Applicant Intake as skipped optional/future scope.
- Phase 4 starts with data and RAG foundations before any co-pilot, summarisation, at-risk, or wellbeing features.
- Step 4.2 narrows the first generated-answer feature to student-facing institutional Q&A only, using Step 4.1 retrieval and safe student context without record mutation.

### Notes
- Step 4.1 uses existing SIS and stored Moodle engagement records only. If attendance, financial flags, GPA, or detailed Moodle assignment/quiz/forum metrics are unavailable, snapshots store null or zero rather than invented values.
- Step 4.1 does not call OpenAI or any paid provider by default.
- Step 4.1 does not embed private student documents or student-private notes into Qdrant.
- Step 4.1 does not implement `/ai/copilot/query`, student co-pilot UI, staff summarisation, at-risk scoring, wellbeing workflows, or admissions.
- Step 4.2 defaults to the deterministic provider and does not require internet or paid AI providers for tests or demos.
- Step 4.2 does not implement Step 4.3 staff summarisation, at-risk scoring, wellbeing workflows, admissions/applicant intake, grade prediction, document OCR/AI analysis, automated enrollment/drop actions, official-record creation, or SIS mutation.
- Step 4.2 does not embed private student documents into the vector store or expose private document contents/review notes to prompts or responses.
