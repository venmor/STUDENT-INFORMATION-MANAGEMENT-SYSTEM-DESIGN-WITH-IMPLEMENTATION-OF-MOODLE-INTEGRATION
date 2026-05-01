# Phase 4.1: Unified Analytics Schema and Vector Store Foundation Spec

## Status
Accepted for implementation on 2026-05-01.

## Context
Step 3.5G Admissions / Applicant Intake is skipped as optional/future. Phase 4 begins with a foundation step only. The current repository already includes core SIS records, academic calendar deadlines, admin reporting, audit events, notifications, protected student documents, and stored Moodle engagement snapshots from Step 3.4.

Step 4.1 prepares AI-ready data and retrieval infrastructure without implementing the student co-pilot, staff summarisation, at-risk scoring, wellbeing workflows, admissions, or LLM answer generation.

## Goals
- Create read-oriented analytics snapshots from existing SIS and stored Moodle engagement data.
- Provide repeatable management commands for seeding safe analytics demo data and running analytics ETL.
- Add admin-only analytics summary and snapshot APIs.
- Add institutional knowledge source, chunk, and ingestion-run metadata.
- Add deterministic local embeddings for tests/demo and an optional OpenAI-compatible provider that is disabled by default.
- Add a provider-agnostic vector-store service layer with Qdrant HTTP support and an in-memory test fallback.
- Seed, ingest, and retrieve safe institutional knowledge, including a local answer source for "What is the deadline to drop a course?"
- Add a minimal admin verification UI at `/admin/ai-foundation`.

## Non-Goals
- No `/ai/copilot/query` endpoint.
- No student-facing AI co-pilot UI.
- No staff summarisation workflow.
- No at-risk scoring or alerting engine.
- No wellbeing workflows.
- No admissions/applicant intake.
- No AI-generated recommendations or LLM answer generation.
- No default paid provider calls.
- No student documents, private advising notes, raw Moodle tokens, LTI JWTs, private keys, or document contents embedded into vectors.
- No full data warehouse platform.

## Proposed Approach
Use two focused backend apps:

- `apps.analytics` owns ETL runs, student analytics snapshots, selectors, summary APIs, and demo analytics data.
- `apps.knowledge` owns institutional knowledge metadata, chunking, embedding abstraction, vector-store operations, ingestion/retrieval commands, admin-only retrieval APIs, and demo knowledge data.

Qdrant remains a later-phase Docker Compose service, but Step 4.1 wires its environment variables and local dev port. Tests use deterministic embeddings and either mocked vector-store operations or an in-memory fallback so they require no internet and no paid AI provider.

The frontend adds a compact admin-only "AI Foundation" page for verification. It shows analytics readiness, knowledge source state, latest ingestion status, vector health, and retrieval-test results. It is not branded as a co-pilot and does not generate answers.

## Data Rules
- Analytics snapshots store counts and derived signals only.
- Attendance is calculated from existing attendance records as present or excused over total attendance records.
- Financial status is represented as active financial flag count only.
- GPA comes from `StudentProfile.cumulative_gpa`; no grade recalculation is introduced.
- Moodle engagement uses stored `MoodleEngagementSnapshot` rows only; no live Moodle dependency.
- Knowledge ingestion uses institutional/public policy-like sources only.
- Student document files and private student records are not knowledge sources.

## API Scope
Admin-only analytics endpoints:
- `GET /api/v1/admin/analytics/summary/`
- `GET /api/v1/admin/analytics/snapshots/`
- `GET /api/v1/admin/analytics/etl-runs/`
- `GET /api/v1/admin/analytics/snapshots/<id>/`

Admin-only knowledge endpoints:
- `GET /api/v1/admin/knowledge/summary/`
- `GET /api/v1/admin/knowledge/sources/`
- `GET /api/v1/admin/knowledge/ingestion-runs/`
- `POST /api/v1/admin/knowledge/test-query/`

Students, advisors, faculty, and unauthenticated users do not receive broad analytics or knowledge admin access in Step 4.1.

## Commands
- `python manage.py seed_analytics_demo`
- `python manage.py run_analytics_etl [--dry-run] [--student-id <uuid>] [--academic-year <value>] [--semester <value>] [--limit <n>]`
- `python manage.py seed_knowledge_demo`
- `python manage.py ingest_knowledge_base [--source-id <uuid>] [--source-type <type>] [--rebuild] [--dry-run] [--limit <n>]`
- `python manage.py query_knowledge_base "What is the deadline to drop a course?" [--limit 5] [--source-type <type>]`

## SRS Requirement Mapping
### Functional Requirements Addressed
- Supports the Phase 4.1 setup-guide requirement for a unified analytics schema fed by SIS and stored Moodle engagement data.
- Partially prepares AI-COP-002 and AI-COP-004 by enabling embedding, chunk retrieval, and source/chunk references without implementing co-pilot prompting or answer generation.
- Supports the AI knowledge-source list in SRS 6.1.2 through safe institutional knowledge sources: academic calendar, course catalog overview, academic regulations, registration procedures, fee schedule, and system policy/demo sources.

### Non-Functional Requirements Addressed
- Modularity: separate analytics and knowledge apps with model, selector, service, serializer, view, command, and test boundaries.
- Maintainability: provider abstractions isolate deterministic, OpenAI-compatible, in-memory, and Qdrant behavior.
- Testability: deterministic embeddings and in-memory vector search keep tests offline and repeatable.
- Reliability: ETL and ingestion runs record status, counts, failures, and last error.
- Usability: admin verification UI exposes readiness and retrieval test state without presenting unfinished AI features.

### Privacy and Security Requirements Addressed
- Analytics snapshots use derived counts and safe references, not raw private payloads.
- Knowledge ingestion excludes student documents, private notes, raw Moodle payloads, tokens, JWTs, and private keys.
- APIs are admin-only through the existing RBAC registry.
- Environment variables keep provider and Qdrant configuration outside source code.

### Auditability Requirements Addressed
- ETL completion/failure, knowledge ingestion completion/failure, and retrieval tests create safe audit events.
- Audit metadata stores counts and IDs only, not retrieved content, secrets, API keys, or raw student data.
- Failure notifications go to admins through the existing in-app notification service.

### AI Governance Requirements Addressed
- No LLM is called in Step 4.1.
- Retrieval is source-grounded and returns chunk/source references for future citations.
- Deterministic embeddings allow local validation before paid provider configuration.
- Step 4.1 creates the governed foundation needed before Step 4.2 introduces student-facing AI.

### Deferred Requirements and Why
- Student co-pilot, summarisation, at-risk scoring, and wellbeing are deferred because Step 4.1 is infrastructure only.
- AI audit log for prompts/responses is deferred because no LLM prompts or responses exist in this step.
- Rate limiting for AI endpoints is deferred because no student-facing AI endpoint is added.
- Live Moodle deep analytics for quizzes, forums, and assignments are deferred; only stored nullable Step 3.4 fields are consumed.

## Risks and Mitigations
- Qdrant may be unavailable locally. Management commands report clear errors, and tests use in-memory/mocked storage.
- Demo knowledge can be mistaken for official policy. Seeded sources are explicitly marked demo/local.
- Analytics can overreach into sensitive records. Snapshot services only aggregate counts and safe existing fields.
- Retrieval scores from deterministic embeddings are not production-quality. They are for local verification only; provider configuration can change later without touching feature code.
