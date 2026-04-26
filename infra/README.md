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
- `docker-compose.moodle.yml`
  - dedicated Phase 3 overlay that activates Moodle without changing the default dev stack
- `moodle.env.example`
  - Moodle bootstrap and SIS-side verification variables for the local Moodle slice
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

## Phase 3 Moodle Overlay

Start Moodle only when Phase 3 integration work is needed:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

Moodle is published on `127.0.0.1:${MOODLE_HTTP_PORT:-8090}`.
`moodle_db` remains internal to the Compose network.

Environment values are documented in `infra/moodle.env.example`. For local work, copy that file into your preferred local env workflow or pass it to Compose with `--env-file`. Set `MOODLE_WS_TOKEN` only after you create the token in Moodle admin.

Important bootstrap detail:

- leave `MOODLE_HOST` empty for the local overlay so Moodle uses the incoming `Host` header, including `:8090`
- set `MOODLE_HOST` only if you are serving Moodle behind a stable hostname or external reverse proxy
- the Bitnami image uses `MOODLE_HOST` only on first initialization when it writes Moodle `wwwroot`
- for Step 3.1 verification, the dedicated service user also needs a system role that grants `webservice/rest:use` and the capabilities required by `core_user_get_users`
- if Moodle loads as unstyled HTML or asset links point to `http://127.0.0.1/` without `:8090`, recreate the Moodle volumes:

```bash
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase down
docker volume rm modern-sis_moodle_data modern-sis_moodle_runtime_data modern-sis_moodle_db_data
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase up -d moodle_db moodle
```

If you run ad hoc Moodle PHP CLI commands in the container, prefer `docker exec -u daemon ...` so runtime caches stay writable by the web process.

## Commands

Validate the local containerized stack:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
```

Validate the Moodle overlay:

```bash
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase config
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
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase down
```
