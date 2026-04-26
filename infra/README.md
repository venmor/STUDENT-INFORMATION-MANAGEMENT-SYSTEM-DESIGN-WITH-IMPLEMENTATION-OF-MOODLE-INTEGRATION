# Infrastructure

This directory contains the Docker and environment assets used for the Phase 2 CI and staging baseline.

## Step 2.5 Assets

- `docker-compose.yml`
  - shared service definitions for the Phase 2 core stack
- `docker-compose.dev.yml`
  - local containerized stack overlay
- `docker-compose.staging.yml`
  - staging-oriented overlay with a separate entrypoint and env template
- `.env.example`
  - local dev variable template
- `staging.env.example`
  - staging variable template
- `nginx/default.conf`
  - reverse-proxy config routing `/api`, `/admin`, and `/static` to Django and `/` to the frontend container

## Current Service Model

### Active Phase 2 Services

- `db`
- `backend`
- `frontend`
- `proxy`

### Later-Phase Placeholder Services

These are included to match the setup guide and SRS topology, but they are profile-gated and not required for the current Phase 2 runtime:

- `redis`
- `celery_worker`
- `celery_beat`
- `qdrant`
- `moodle`
- `moodle_db`

Activate them only when the later Moodle and AI phases are implemented.

## Commands

Validate the local containerized stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
```

Start the local containerized stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build -d db backend frontend proxy
```

The dev overlay publishes:

- MySQL on `127.0.0.1:${DEV_DB_PORT:-3313}`
- the reverse proxy on `127.0.0.1:${DEV_HTTP_PORT:-8080}`

Validate the staging stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml config
```

Start the staging-oriented stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml up --build -d db backend frontend proxy
```

The staging overlay publishes the reverse proxy on `127.0.0.1:${STAGING_HTTP_PORT:-8088}` and keeps the database internal to the Compose network.

Smoke-check the staging entrypoint:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml ps
curl -I http://127.0.0.1:8088
curl http://127.0.0.1:8088/api/v1/auth/login
```

Tear down either stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml down
docker compose -f infra/docker-compose.yml -f infra/docker-compose.staging.yml down
```
