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

- Step 4.3 `apps.summarisation` backend app with `SummarisationRequest` model, deterministic and OpenAI-compatible providers, structured extraction prompt, service layer with AI audit logging and advising note creation on approval, serializers, views, URL routing, and access policy enforcement for advisor and admin roles.
- `POST /api/v1/ai/summarise/` endpoint accepting raw text (up to 5000 chars) and returning structured JSON summary with `key_issues`, `recommended_actions`, and `urgency_level`.
- `POST /api/v1/ai/summarise/{id}/approve/` endpoint saving human-edited summary as official advising note (when student context is provided) with full audit trail.
- Live `AISummarisationPanel` replacing the disabled Step 2.4 placeholder in the advisor student profile page, with governance notice, character counter, editable structured result form, approve/discard flow, and success/error states.
- Standalone `/admin/summarise` page for admin staff to summarise text without student context, accessible from the admin sidebar under Insights.
- Demo seed command `python manage.py seed_summarisation_demo` with 5 real-world advising scenarios (academic probation, course withdrawal, graduate preparation, personal circumstances, internship credit).
- Backend tests for service layer (deterministic provider, urgent detection, approval with/without student, validation) and API permissions (advisor/admin allowed, student/faculty denied, input validation).
- Frontend tests for `SummarisationForm` (governance notice, char counter, submit, truncation warning) and `SummarisationResult` (editable issues, urgency selector, approve/discard callbacks).

### Changed
- Activated OpenAI-compatible provider for the student co-pilot in local development configuration (`AI_PROVIDER=openai_compatible`, model `gpt-4o-mini`). Tests and CI continue to use the deterministic provider. The `.env.local` file holds the API key and is git-ignored.
- Updated `infra/moodle.env.example` with improved documentation comments and default model value for OpenAI-compatible provider setup.
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
