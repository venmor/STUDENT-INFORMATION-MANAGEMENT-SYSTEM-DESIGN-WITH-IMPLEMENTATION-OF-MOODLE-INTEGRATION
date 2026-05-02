# Phase 4 - AI Foundation

Phase 4 begins after Step 3.5F Student Document Management. Optional Step 3.5G Admissions / Applicant Intake is skipped for now and remains future scope.

## Step 4.1 - Unified Analytics Schema And Vector Store Foundation

Status: Implemented.

Step 4.1 prepares the data and retrieval layer required by later governed AI features. It does not implement the student co-pilot, staff summarisation, at-risk scoring, wellbeing workflows, or admissions.

### Backend Scope

- `apps.analytics` stores derived student analytics snapshots in a read-oriented schema.
- `python manage.py seed_analytics_demo` creates safe repeatable demo SIS, grade, attendance, financial-flag, and stored Moodle engagement data.
- `python manage.py run_analytics_etl` copies existing SIS and stored Moodle engagement data into `StudentAnalyticsSnapshot` records.
- Admin-only APIs expose analytics summary, snapshots, and ETL runs under `/api/v1/admin/analytics/`.
- `apps.knowledge` stores institutional knowledge sources, chunks, and ingestion runs.
- `python manage.py seed_knowledge_demo` creates safe local demo institutional sources.
- `python manage.py ingest_knowledge_base` chunks, embeds, and upserts institutional chunks into the configured vector store.
- `python manage.py query_knowledge_base "What is the deadline to drop a course?"` tests retrieval only and does not call an LLM.
- Admin-only APIs expose knowledge summary, sources, ingestion runs, and retrieval-only test query under `/api/v1/admin/knowledge/`.

### Vector Store And Embeddings

- Qdrant is available as an optional `later-phase` Docker Compose service.
- `QDRANT_URL`, `QDRANT_COLLECTION`, `KNOWLEDGE_VECTOR_STORE_PROVIDER`, and embedding settings are environment-driven.
- The default local/demo embedding provider is deterministic and does not require internet access or a paid API.
- An OpenAI-compatible embedding provider is configurable for later phases but is not used by default.

### Admin Verification UI

Admins can open `/admin/ai-foundation` to inspect:

- latest analytics ETL status
- student analytics snapshots
- knowledge source and chunk readiness
- vector-store health
- recent knowledge ingestion runs
- retrieval-only test results for institutional chunks

The page is intentionally labelled AI Foundation. It does not implement the student AI co-pilot or generated answers.

### Governance Boundaries

- Analytics snapshots store derived counts and nullable signals only.
- Moodle tokens, raw LTI JWTs, private student document contents, and private notes are not stored in analytics snapshots.
- Knowledge ingestion is limited to institutional policy/demo text and safe source references.
- Step 3.5F student documents are not embedded into Qdrant.
- Retrieval tests audit source/chunk identifiers and query length, not long retrieved content or secrets.
- Admin notifications are created only for ETL or ingestion failures where the notification service is available.

## Step 4.2 - Student Service Co-pilot

Status: Implemented.

Step 4.2 adds the student-facing AI Co-pilot at `/student/copilot`. It answers routine academic service questions using Step 4.1 institutional knowledge retrieval, safe authenticated-student context, academic calendar deadlines, current enrollments, official grade summaries where already student-visible, and bounded document-status counts. It is a source-grounded question-answering feature only.

### Backend Scope

- `apps.copilot` stores `CopilotSession`, `CopilotMessage`, `AIAuditLog`, and optional `CopilotFeedback` records.
- Student APIs are exposed under `/api/v1/ai/copilot/` for query, session list/create/detail/archive, and assistant-message feedback.
- The service layer orchestrates question validation, Step 4.1 retrieval, safe context assembly, provider calls, source/confidence validation, fallback responses, and audit logging.
- The deterministic provider is the default for local tests and demos. It requires no API key, internet, or paid AI account, and builds predictable answers from retrieved chunks plus safe student context.
- An OpenAI-compatible provider is optional through `AI_PROVIDER=openai_compatible`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, and timeout/top-k settings.
- `python manage.py seed_copilot_demo` seeds safe demo student/context/knowledge/analytics data and a starter co-pilot session.
- `python manage.py test_copilot_query "What is the deadline to drop a course?"` runs retrieval and deterministic answering against the demo student.

### Frontend Scope

- Students can open `/student/copilot` from the student sidebar and dashboard.
- The route page is thin and delegates to reusable co-pilot feature components under `frontend/src/features/copilot/`.
- The chat UI includes example prompts, recent session panel, accessible transcript, source panel, source references, confidence badges, suggested workflow links, low-confidence disclaimer, retryable error state, and a labelled multiline composer.
- The thinking state appears immediately with `Searching institutional sources...` and transitions to `Preparing answer...` while the request is pending.

### Governance Boundaries

- Co-pilot answers do not create official records and do not mutate enrollments, grades, documents, calendar events, notifications, Moodle records, or SIS records.
- The co-pilot does not implement Step 4.3 staff summarisation.
- The co-pilot does not implement at-risk scoring, wellbeing workflows, admissions/applicant intake, grade prediction, OCR, image/file analysis, or automated enrollment/drop actions.
- Source retrieval is limited to institutional knowledge chunks. Private student documents are not embedded into Qdrant and private document contents/review notes are not passed into prompts.
- Safe student context is limited to the authenticated student's profile summary, current enrollment summary, role-visible academic deadlines, student-visible document status counts, official grade summary, and safe analytics counts.
- Every query/response/fallback/provider error writes sanitized AI audit records and safe `AuditEvent` activity metadata without provider credentials, raw JWTs, Moodle tokens, LTI keys, passwords, API keys, private prompts, raw provider headers, or private retrieved content.
- Unsupported or low-confidence answers are labelled and direct the student to verify with the Registrar office.

## Run And Test Step 4.2

Start from latest `main`:

```bash
git checkout main
git pull origin main
```

Start the full local stack including Qdrant:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d --build db backend frontend proxy moodle_db moodle qdrant
```

Run migrations and seed/demo commands:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py migrate
```

Create or reset an admin account if needed:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py createsuperuser

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py changepassword admin
```

Seed analytics, knowledge, and co-pilot demo data:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py seed_analytics_demo

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py run_analytics_etl

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py seed_knowledge_demo

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py ingest_knowledge_base

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py query_knowledge_base "What is the deadline to drop a course?"

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py seed_copilot_demo

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  exec backend python manage.py test_copilot_query "What is the deadline to drop a course?"
```

Open:

- `http://127.0.0.1:8080/student/copilot`
- optional Vite hot reload: `http://127.0.0.1:5173/student/copilot`

Demo login:

```text
student.demo1 / DemoPass123!
```

Verification commands:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/copilot/tests/
pytest -q apps/analytics/tests/
pytest -q apps/knowledge/tests/
pytest -q apps/audit/tests/
pytest -q apps/notifications/tests/
pytest -q apps/integration/tests/
ruff check .
```

```bash
cd frontend
npm run typecheck
npm run lint
npm run test
npm run build
```

Tear down:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.dev.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down
```

The Step 4.1 admin foundation remains available at `http://127.0.0.1:8080/admin/ai-foundation` for analytics, knowledge, vector-store health, and retrieval-only verification.
