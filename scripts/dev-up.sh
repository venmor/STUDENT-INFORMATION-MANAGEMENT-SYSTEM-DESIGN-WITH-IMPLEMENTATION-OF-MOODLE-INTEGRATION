#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FULL_STACK=0
OPEN_BROWSER=1
DOCKER_PULL_RETRIES="${DOCKER_PULL_RETRIES:-3}"
DOCKER_PULL_RETRY_DELAY="${DOCKER_PULL_RETRY_DELAY:-5}"

usage() {
  cat <<'EOF'
Usage: scripts/dev-up.sh [--full] [--no-open] [--help]

Start Modern SIS for local demonstration.

Options:
  --full      Start the optional Moodle/Qdrant services and seed AI demo data.
  --no-open   Do not try to open the browser after startup.
  --help      Show this help message.

Default behavior starts the core SIS:
  MySQL + Django backend + React frontend + Nginx proxy

After startup, open:
  http://127.0.0.1:8080

Demo password for seeded accounts:
  DemoPass123!
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --full)
        FULL_STACK=1
        shift
        ;;
      --no-open)
        OPEN_BROWSER=0
        shift
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        echo "Unknown option: $1" >&2
        usage >&2
        exit 2
        ;;
    esac
  done
}

check_docker_compose() {
  if ! docker compose version >/dev/null 2>&1; then
    echo "Docker Compose is required. Install Docker Desktop or the Docker Compose plugin, then rerun this script." >&2
    exit 1
  fi
}

configure_stack() {
  if [[ "$FULL_STACK" -eq 1 ]]; then
    COMPOSE_ARGS=(
      --env-file "$ROOT_DIR/infra/moodle.env.example"
      -f "$ROOT_DIR/infra/docker-compose.yml"
      -f "$ROOT_DIR/infra/docker-compose.dev.yml"
      -f "$ROOT_DIR/infra/docker-compose.moodle.yml"
      --profile later-phase
    )
    SERVICES=(db backend frontend proxy moodle_db moodle qdrant)
    REQUIRED_IMAGES=(
      python:3.11-slim
      node:20-alpine
      mysql:8
      nginx:1.27-alpine
      mariadb:11
      bitnamilegacy/moodle:4.5.4
      qdrant/qdrant:v1.13.6
    )
  else
    COMPOSE_ARGS=(
      -f "$ROOT_DIR/infra/docker-compose.yml"
      -f "$ROOT_DIR/infra/docker-compose.dev.yml"
    )
    SERVICES=(db backend frontend proxy)
    REQUIRED_IMAGES=(
      python:3.11-slim
      node:20-alpine
      mysql:8
      nginx:1.27-alpine
    )
  fi
}

compose() {
  docker compose "${COMPOSE_ARGS[@]}" "$@"
}

retry_docker_pull() {
  local image="$1"
  local attempt=1

  while (( attempt <= DOCKER_PULL_RETRIES )); do
    if docker image inspect "$image" >/dev/null 2>&1; then
      echo "Docker image $image is already available."
      return 0
    fi

    echo "Pulling Docker image $image (attempt $attempt/$DOCKER_PULL_RETRIES)..."
    if docker pull "$image"; then
      return 0
    fi

    if (( attempt == DOCKER_PULL_RETRIES )); then
      cat >&2 <<EOF
Docker could not pull $image after $DOCKER_PULL_RETRIES attempts.

This is usually a Docker Hub or network issue, not a Modern SIS code issue.
Check internet access to https://auth.docker.io and https://registry-1.docker.io,
then rerun this command. You can also pre-pull the image manually:
  docker pull $image
EOF
      return 1
    fi

    echo "Pull failed for $image. Retrying in ${DOCKER_PULL_RETRY_DELAY}s..."
    sleep "$DOCKER_PULL_RETRY_DELAY"
    attempt=$((attempt + 1))
  done
}

ensure_required_images() {
  local image
  for image in "${REQUIRED_IMAGES[@]}"; do
    retry_docker_pull "$image"
  done
}

wait_for_backend() {
  echo "Waiting for the Django backend to accept commands..."
  for _ in $(seq 1 60); do
    if compose exec -T backend python manage.py check >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  echo "Backend did not become ready in time. Check container logs with:" >&2
  echo "  docker compose ${COMPOSE_ARGS[*]} logs backend" >&2
  exit 1
}

run_backend_command() {
  compose exec -T backend python manage.py "$@"
}

open_browser() {
  local url="$1"
  if [[ "$OPEN_BROWSER" -ne 1 ]]; then
    return 0
  fi
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "$url" >/dev/null 2>&1 || true
  elif command -v wslview >/dev/null 2>&1; then
    wslview "$url" >/dev/null 2>&1 || true
  fi
}

main() {
  parse_args "$@"
  check_docker_compose
  configure_stack

  cd "$ROOT_DIR/infra"

  echo "Checking required Docker images..."
  ensure_required_images

  echo "Starting Modern SIS containers..."
  compose up --build -d "${SERVICES[@]}"

  wait_for_backend

  echo "Applying database migrations..."
  run_backend_command migrate --noinput

  echo "Seeding core SIS demo data..."
  run_backend_command seed_demo_sis

  if [[ "$FULL_STACK" -eq 1 ]]; then
    echo "Seeding optional demo data for calendar, documents, analytics, knowledge, co-pilot, summarisation, and at-risk workflows..."
    run_backend_command seed_academic_calendar_demo
    run_backend_command seed_document_demo
    run_backend_command seed_analytics_demo
    run_backend_command run_analytics_etl
    run_backend_command seed_knowledge_demo
    run_backend_command ingest_knowledge_base
    run_backend_command seed_copilot_demo
    run_backend_command seed_summarisation_demo
    run_backend_command seed_at_risk_demo
  fi

  APP_URL="http://127.0.0.1:${DEV_HTTP_PORT:-8080}"
  open_browser "$APP_URL"

  cat <<EOF

Modern SIS is running.

Open: $APP_URL

Demo accounts:
  admin.demo    / DemoPass123!
  advisor.demo  / DemoPass123!
  faculty.demo  / DemoPass123!
  student.demo1 / DemoPass123!
  student.demo2 / DemoPass123!

Stop services:
  cd infra
  docker compose ${COMPOSE_ARGS[*]} down
EOF
}

if [[ "${DEV_UP_LIB_ONLY:-0}" != "1" ]]; then
  main "$@"
fi
