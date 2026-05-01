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

## Run And Test Step 4.1

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
```

Open:

- `http://127.0.0.1:8080/admin/ai-foundation`
- optional Vite hot reload: `http://127.0.0.1:5173/admin/ai-foundation`

Verification commands:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/analytics/tests/
pytest -q apps/knowledge/tests/
pytest -q apps/reporting/tests/
pytest -q apps/calendar/tests/
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
