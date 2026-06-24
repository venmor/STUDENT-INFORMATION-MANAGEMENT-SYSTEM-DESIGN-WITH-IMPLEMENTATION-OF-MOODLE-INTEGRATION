#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cat >"$TMP_DIR/docker" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail

COUNT_FILE="${DOCKER_STUB_COUNT_FILE:?}"

if [[ "${1:-}" == "compose" && "${2:-}" == "version" ]]; then
  exit 0
fi

if [[ "${1:-}" == "image" && "${2:-}" == "inspect" ]]; then
  exit 1
fi

if [[ "${1:-}" == "pull" ]]; then
  count="$(cat "$COUNT_FILE" 2>/dev/null || printf '0')"
  count=$((count + 1))
  printf '%s' "$count" >"$COUNT_FILE"
  if [[ "$count" -lt 2 ]]; then
    exit 1
  fi
  exit 0
fi

echo "Unexpected docker invocation: $*" >&2
exit 90
STUB

chmod +x "$TMP_DIR/docker"
printf '0' >"$TMP_DIR/pull-count"

export PATH="$TMP_DIR:$PATH"
export DOCKER_STUB_COUNT_FILE="$TMP_DIR/pull-count"
export DOCKER_PULL_RETRIES=2
export DOCKER_PULL_RETRY_DELAY=0
export DEV_UP_LIB_ONLY=1
source "$ROOT_DIR/scripts/dev-up.sh"

has_required_image() {
  local expected="$1"
  local image
  for image in "${REQUIRED_IMAGES[@]}"; do
    if [[ "$image" == "$expected" ]]; then
      return 0
    fi
  done
  return 1
}

FULL_STACK=0
configure_stack
for image in python:3.11-slim node:20-alpine mysql:8 nginx:1.27-alpine; do
  if ! has_required_image "$image"; then
    echo "Expected core stack to pre-pull $image" >&2
    exit 1
  fi
done
if has_required_image mariadb:11; then
  echo "Core stack should not pre-pull optional Moodle images" >&2
  exit 1
fi

FULL_STACK=1
configure_stack
for image in python:3.11-slim node:20-alpine mysql:8 nginx:1.27-alpine mariadb:11 bitnamilegacy/moodle:4.5.4 qdrant/qdrant:v1.13.6; do
  if ! has_required_image "$image"; then
    echo "Expected full stack to pre-pull $image" >&2
    exit 1
  fi
done

retry_docker_pull "mariadb:11" >"$TMP_DIR/dev-up-retry-test.log"

attempts="$(cat "$TMP_DIR/pull-count")"
if [[ "$attempts" != "2" ]]; then
  echo "Expected retry_docker_pull to use 2 attempts, got $attempts" >&2
  exit 1
fi

grep -q "Pulling Docker image mariadb:11 (attempt 2/2)" "$TMP_DIR/dev-up-retry-test.log"
