# Infrastructure for Objective 1

The infrastructure directory provides Docker Compose configuration for local and supervisor review of the Objective 1 SIS implementation.

## Files

- `docker-compose.yml`: backend, frontend, database, Moodle-compatible environment configuration, and supporting services.
- `docker-compose.dev.yml`: development overrides for local review.
- `docker-compose.moodle.yml`: Moodle-connected configuration overlay.
- `.env.example`: SIS environment template.
- `moodle.env.example`: Moodle environment template.

## Configuration Check

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
docker compose -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml config
```
