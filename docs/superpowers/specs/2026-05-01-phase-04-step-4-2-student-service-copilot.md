# Phase 4.2: Student Service Co-pilot Spec

## Status
Accepted for implementation on 2026-05-01 by direct user instruction.

## Context
Step 4.1 implemented the analytics snapshot and institutional knowledge/vector-store foundation. The current system also has role-based dashboards, academic calendar/deadline rules, secure student documents, notifications, and audit/admin activity records.

Step 4.2 adds a student-facing co-pilot for question answering only. It must answer from institutional knowledge chunks, source citations, safe authenticated-student context, and workflow links. It must not mutate SIS records or implement Step 4.3 staff summarisation, at-risk scoring, wellbeing workflows, admissions, OCR, grade prediction, or official-record generation.

## Goals
- Provide authenticated students with `/student/copilot`.
- Add source-grounded co-pilot APIs under `/api/v1/ai/copilot/`.
- Store co-pilot sessions, messages, and AI audit logs.
- Retrieve top institutional knowledge chunks through the Step 4.1 knowledge service.
- Include safe student context: profile summary, active enrollments, student-visible document counts/statuses, current academic deadlines, official-grade summary, and the student's own analytics snapshot summary.
- Return confidence, source references, suggested next actions, and registrar fallback guidance.
- Use a deterministic local provider by default for offline tests/demo.
- Support an optional OpenAI-compatible provider through environment variables.

## Non-Goals
- No staff summarisation or advisor/admin note drafting.
- No at-risk labels, scoring, or predictions.
- No wellbeing diagnosis, triage, or check-in workflow.
- No admissions/applicant intake.
- No document OCR or AI document analysis.
- No automated enrollment, drop, grade, approval, document-review, or official-record mutation actions.
- No embedding of student-private documents or other private student content into Qdrant.
- No paid provider requirement for local tests or demo commands.

## Backend Design
Create `backend/apps/copilot/` as an orchestration app. `apps.analytics` and `apps.knowledge` stay focused on their foundation responsibilities.

- `models.py`: `CopilotSession`, `CopilotMessage`, and `AIAuditLog`.
- `permissions.py`: student/admin checks and session ownership helpers.
- `selectors.py`: safe student context, current user's sessions, message lookup, and retrieval result shaping.
- `safety.py`: question length checks, prompt-injection flagging, metadata/text redaction, source/reference validation, and low-confidence fallback rules.
- `prompts.py`: central system prompt and context assembly helpers.
- `providers.py`: deterministic local provider and optional OpenAI-compatible provider.
- `services.py`: query orchestration, retrieval, provider call/fallback, message persistence, suggested actions, and AI audit records.
- `serializers.py`: request validation and response shaping.
- `views.py` and `urls.py`: thin DRF endpoints.
- `management/commands/seed_copilot_demo.py`: repeatable local demo seed.
- `management/commands/test_copilot_query.py`: offline deterministic query test.

## API Design
Student-facing endpoints:
- `POST /api/v1/ai/copilot/query`
- `GET /api/v1/ai/copilot/sessions`
- `POST /api/v1/ai/copilot/sessions`
- `GET /api/v1/ai/copilot/sessions/<id>`
- `POST /api/v1/ai/copilot/sessions/<id>/archive`
- `POST /api/v1/ai/copilot/messages/<id>/feedback`

Feedback is included because it is small, safe, and useful for governance. It stores only ownership-checked assistant-message ratings and optional bounded comments. It has no official-record effect.

## Provider Behavior
The deterministic provider is the default. It requires no API key and builds answers from retrieved chunks plus safe student context. It refuses unsupported questions instead of returning canned one-answer output.

The OpenAI-compatible provider is selected only when `AI_PROVIDER=openai_compatible` and required provider settings exist. Missing configuration or provider failure returns a safe fallback and creates an audit event. Tests must not use the live provider.

## Safety And Privacy
- Questions are length-limited.
- Prompt-injection-like requests are flagged and answered with a safety refusal/fallback.
- Provider prompts include retrieved institutional chunks and safe context only.
- Private student documents, raw document contents, admin notes, broad analytics, raw audit logs, Moodle tokens, LTI keys, JWTs, passwords, provider headers, and API keys are excluded from context and audit metadata.
- Students can only access their own sessions and assistant messages.
- Advisors/faculty are denied Step 4.2 student co-pilot APIs.
- Admins may use the command-line/demo path and can create non-student-safe provider checks later, but this API remains student scoped.

## Frontend Design
Add a student route `/student/copilot` and sidebar entry labelled `AI Co-pilot`.

Feature files:
- `frontend/src/api/copilot.ts`
- `frontend/src/hooks/useCopilot.ts`
- `frontend/src/types/copilot.ts`
- `frontend/src/pages/student/Copilot.tsx`
- `frontend/src/features/copilot/components/*`

The page uses a three-region layout: recent sessions, chat transcript/composer, and source panel. On mobile, sources collapse below the transcript. The route page stays thin and components own focused responsibilities.

Required UX states:
- Empty state with example prompts.
- User message appears immediately on submit.
- Thinking indicator announces `Searching institutional sources...` then `Preparing answer...`.
- Send is disabled while pending.
- Errors show a retry action.
- Assistant messages include confidence, citations, suggested actions, disclaimer, and timestamp.

## SRS Requirement Mapping

### Functional AI Co-pilot Requirements
- `AI-COP-001`: implemented with authenticated student chat UI at `/student/copilot`.
- `AI-COP-002`: implemented through Step 4.1 embeddings/vector retrieval with default top-k 5.
- `AI-COP-003`: implemented by prompt rules and unsupported fallback when sources are insufficient.
- `AI-COP-004`: implemented by returning source references for every grounded response.
- `AI-COP-005`: implemented by `AIAuditLog` records for queries, responses, low-confidence answers, provider errors, and retrieval-only/demo flows.
- `AI-COP-006`: implemented by persistent frontend safety notice and response disclaimer.
- `AI-COP-007`: implemented by provider error fallback and audit logging.
- `AI-COP-008` through `AI-COP-010`: partially supported with deterministic command/test coverage; full 30-question formal accuracy evaluation is deferred to deployment readiness.

### Student Service Requirements
- Supports registration, deadlines, course, grades, documents, notifications, and Registrar guidance questions.
- Returns workflow links only; no returned action mutates records.
- Uses safe student context from existing student-visible routes and summaries.

### RBAC Requirements
- Students can query and manage only their own co-pilot sessions.
- Advisors and faculty are denied the student co-pilot endpoints in Step 4.2.
- Unauthenticated requests receive 401 through existing access-control middleware.
- Admin broad AI audit review UI remains deferred; admin commands are available for local verification.

### Audit Requirements
- Each submitted query and generated/fallback response is recorded.
- Audit metadata stores IDs, counts, provider, model, confidence, and source references.
- Audit metadata is redacted and excludes secrets, private payloads, provider headers, and document contents.
- AI output is not marked as an official institutional record.

### Privacy/Security Requirements
- Context is scoped to the authenticated student's own data.
- Private student document contents, admin notes, broad analytics, raw audit logs, Moodle tokens, LTI keys, JWTs, passwords, prompts containing secrets, and provider credentials are excluded.
- Prompt-injection attempts are flagged and do not override source-grounding rules.

### Performance Requirements
- Default retrieval top-k is 5 and configurable.
- Question length, chat history, source preview, and response payloads are bounded.
- Provider timeout is configurable via `AI_REQUEST_TIMEOUT_SECONDS`.
- Session/message lookups are indexed by user/session/time.

### Accessibility/Usability Requirements
- Chat transcript has a labelled region.
- Composer has an accessible label, visible send button text, keyboard submit, and disabled state.
- Thinking and error states are announced with `aria-live`.
- Confidence and source information use text, not color alone.
- Suggested actions are real links/buttons with visible labels.
- Layout is responsive and avoids hover-only controls.

### Maintainability Requirements
- Backend follows model/serializer/permission/selector/service/provider/view boundaries.
- Frontend route is split into API/types/hooks/page/components.
- Deterministic provider keeps tests offline and repeatable.
- Optional provider configuration is centralized.

### Deferred Requirements And Why
- Step 4.3 staff summarisation is deferred because it creates staff workflow and official-record review concerns outside this student Q&A slice.
- At-risk scoring is deferred to Phase 5 because it requires agreed signal thresholds, advisor workflow, and risk-governance review.
- Wellbeing is deferred to Phase 6 because it requires consent, safeguarding policy, restricted storage, and staffed escalation.
- Admissions remains optional/future per Step 3.5G.
- AI audit admin search UI is deferred; Step 4.2 writes auditable records and existing admin audit viewer records AI-category activity.

## Risks And Mitigations
- Vector store unavailable: return unsupported/provider-unavailable fallback and audit the failure.
- Low retrieval relevance: mark confidence `LOW` or `UNSUPPORTED`, cite no unsupported facts, and direct the student to Registrar/advisor.
- Provider failure: deterministic remains default; OpenAI-compatible provider errors degrade safely.
- Privacy overreach: selectors explicitly build summaries and never pass document contents, notes, or other students' data to prompts.
