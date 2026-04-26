# Phase 3 Step 3.1 Moodle Instance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a local Moodle development instance through a dedicated Compose overlay and prove SIS-to-Moodle REST connectivity with a narrow verification command.

**Architecture:** Keep the existing Phase 2 Compose base intact and activate Moodle only through a dedicated Phase 3 overlay plus the existing `later-phase` profile. Use a small Django management command under the integration app for `core_user_get_users` verification instead of prematurely building the full provisioning layer.

**Tech Stack:** Docker Compose, Bitnami Moodle 4.3 container, MariaDB 11, Django 5, Python requests-style HTTP via stdlib or `requests`, pytest, repository runbooks and changelogs

---

## Status

Plan written on 2026-04-26 from the approved spec in `docs/superpowers/specs/2026-04-26-phase-03-step-3-1-moodle-instance-design.md`.

## File Map

- Create: `infra/docker-compose.moodle.yml`
- Create: `infra/moodle.env.example`
- Create: `backend/apps/integration/management/__init__.py`
- Create: `backend/apps/integration/management/commands/__init__.py`
- Create: `backend/apps/integration/management/commands/verify_moodle_rest.py`
- Create: `backend/apps/integration/tests/test_verify_moodle_rest_command.py`
- Create: `docs/phases/phase-03-moodle-integration/README.md`
- Create: `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- Modify: `infra/README.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/README.md`
- Modify: `docs/phases/README.md`
- Modify: `backend/README.md`

### Task 1: Create Phase 3 Tracking And Docs Baseline

**Files:**
- Create: `docs/phases/phase-03-moodle-integration/README.md`
- Create: `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- Modify: `docs/README.md`
- Modify: `docs/phases/README.md`

- [ ] **Step 1: Write the Phase 3 README**

Create `docs/phases/phase-03-moodle-integration/README.md` with:

```markdown
# Phase 3 Moodle Integration

## Objective

Phase 3 introduces Moodle integration in controlled slices so Lane A REST provisioning and Lane B LTI work can build on the stable Phase 2 SIS baseline.

## Scope

- stand up a local Moodle development environment
- prove SIS-to-Moodle REST connectivity
- implement Lane A provisioning after connectivity is proven
- implement Lane B LTI only after Lane A is stable

## Status

- Status: In progress
- Source guide: `docs/project/modern-sis-setup-guide.md` Phase 3
- Current step: Step 3.1 Moodle development instance and REST connectivity proof

## Current Step

- Step 3.1 is active on this implementation slice: Moodle is started through a dedicated overlay and verified manually plus through a narrow SIS-side verification command.
- Step 3.2 remains next: provisioning sync engine for Lane A.

## Expected Deliverables

- dedicated Moodle Compose overlay
- Moodle-specific env template
- manual admin runbook for web services and REST
- SIS-side `core_user_get_users` verification command

## Exit Criteria

- local Moodle starts without changing default Phase 2 startup
- manual Moodle web-services setup is documented clearly
- the verification command proves REST connectivity with a real token

## Tracking

- [Phase 3 Changelog](CHANGELOG.md)
- [Setup Guide](../../project/modern-sis-setup-guide.md)
- [SRS](../../project/SRS_Modern_SIS.md)
```

- [ ] **Step 2: Create the Phase 3 changelog**

Create `docs/phases/phase-03-moodle-integration/CHANGELOG.md` with:

```markdown
# Phase 3 Changelog

## [Unreleased]

### Added
- Phase 3 README to track Moodle integration separately from the Phase 2 core build.

### Changed
- None.

### Notes
- None.
```

- [ ] **Step 3: Update the docs index**

Update `docs/README.md` so the status line no longer says `main` only preserves the Phase 2 auth baseline. Replace the stale opening paragraph with:

```markdown
This directory contains the maintained documentation for the Modern SIS project.

`main` now carries the completed Phase 2 core build and the active Phase 3 Moodle integration baseline.
```

Add Phase 3 to the `Start Here` list immediately after Phase 2:

```markdown
5. [Phase 3 Moodle Integration](phases/phase-03-moodle-integration/README.md)
6. [Architecture Diagrams](architecture/architecture-diagrams.md)
7. [Version Control](process/version-control.md)
```

- [ ] **Step 4: Update the phases index**

Update `docs/phases/README.md` so the table reflects the transition:

```markdown
| Phase 2 - Core Build | Complete | `phase-02-core-build/` | Core SIS implementation in isolation: backend/frontend scaffolding, auth, RBAC, and core modules |
| Phase 3 - Moodle Integration | In Progress | `phase-03-moodle-integration/` | Lane A provisioning baseline, REST connectivity, and later Lane B LTI delivery |
```

- [ ] **Step 5: Verify docs changes render cleanly**

Run:

```bash
sed -n '1,220p' docs/README.md
sed -n '1,220p' docs/phases/README.md
sed -n '1,220p' docs/phases/phase-03-moodle-integration/README.md
sed -n '1,120p' docs/phases/phase-03-moodle-integration/CHANGELOG.md
```

Expected: all four files show Phase 3 as active with no placeholder content left behind.

### Task 2: Add The Dedicated Moodle Overlay And Env Template

**Files:**
- Create: `infra/docker-compose.moodle.yml`
- Create: `infra/moodle.env.example`
- Modify: `infra/README.md`

- [ ] **Step 1: Write the failing Compose-shape check**

Confirm the file does not exist yet:

```bash
test ! -f infra/docker-compose.moodle.yml && echo overlay-missing
test ! -f infra/moodle.env.example && echo moodle-env-missing
```

Expected:

```text
overlay-missing
moodle-env-missing
```

- [ ] **Step 2: Create the Moodle env example**

Create `infra/moodle.env.example` with:

```dotenv
MOODLE_HTTP_PORT=8090
MOODLE_HOST=127.0.0.1
MOODLE_SITE_NAME=Student Information System Moodle
MOODLE_USERNAME=admin
MOODLE_PASSWORD=ChangeMe123!
MOODLE_EMAIL=admin@example.com

MOODLE_DB_NAME=moodle
MOODLE_DB_USER=moodle
MOODLE_DB_PASSWORD=moodle
MOODLE_DB_ROOT_PASSWORD=root

MOODLE_BASE_URL=http://127.0.0.1:8090
MOODLE_WS_TOKEN=
```

- [ ] **Step 3: Create the dedicated Moodle overlay**

Create `infra/docker-compose.moodle.yml` with:

```yaml
services:
  moodle_db:
    env_file:
      - ./moodle.env.example

  moodle:
    env_file:
      - ./moodle.env.example
    ports:
      - "127.0.0.1:${MOODLE_HTTP_PORT:-8090}:8080"
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8080/ >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 120s
```

Do not publish `moodle_db`.

- [ ] **Step 4: Document the overlay in infra README**

Add a dedicated section to `infra/README.md`:

```markdown
## Phase 3 Moodle Overlay

Start Moodle only when Phase 3 integration work is needed:

```bash
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

Moodle is published on `127.0.0.1:${MOODLE_HTTP_PORT:-8090}`.
`moodle_db` remains internal to the Compose network.

Environment values live in `infra/moodle.env.example`. Copy them into your local env workflow and set `MOODLE_WS_TOKEN` only after you create the token in Moodle admin.
```

- [ ] **Step 5: Verify Compose resolution**

Run:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase config > /tmp/modern-sis-moodle-compose.yaml
```

Expected: exit `0`.

- [ ] **Step 6: Verify Moodle starts through the overlay**

Run:

```bash
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle

docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  ps
```

Expected: `moodle_db` is running and `moodle` reaches running or healthy state on `127.0.0.1:8090`.

- [ ] **Step 7: Tear down after the check**

Run:

```bash
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down
```

Expected: clean teardown with no impact on the default Phase 2 stack.

### Task 3: Add The Narrow Moodle REST Verification Command And Tests

**Files:**
- Create: `backend/apps/integration/management/__init__.py`
- Create: `backend/apps/integration/management/commands/__init__.py`
- Create: `backend/apps/integration/management/commands/verify_moodle_rest.py`
- Create: `backend/apps/integration/tests/test_verify_moodle_rest_command.py`
- Modify: `backend/README.md`

- [ ] **Step 1: Write the failing tests**

Create `backend/apps/integration/tests/test_verify_moodle_rest_command.py` with:

```python
from io import StringIO
from unittest.mock import patch

import requests
from django.core.management import call_command, CommandError
from django.test import SimpleTestCase, override_settings


class VerifyMoodleRestCommandTests(SimpleTestCase):
    @override_settings(MOODLE_BASE_URL="", MOODLE_WS_TOKEN="")
    def test_requires_base_url(self):
        with self.assertRaisesMessage(CommandError, "MOODLE_BASE_URL is not configured"):
            call_command("verify_moodle_rest")

    @override_settings(MOODLE_BASE_URL="http://127.0.0.1:8090", MOODLE_WS_TOKEN="")
    def test_requires_token(self):
        with self.assertRaisesMessage(CommandError, "MOODLE_WS_TOKEN is not configured"):
            call_command("verify_moodle_rest")

    @override_settings(MOODLE_BASE_URL="http://127.0.0.1:8090", MOODLE_WS_TOKEN="token")
    @patch("apps.integration.management.commands.verify_moodle_rest.requests.get")
    def test_reports_connection_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("boom")
        with self.assertRaisesMessage(CommandError, "Unable to reach Moodle REST endpoint"):
            call_command("verify_moodle_rest")

    @override_settings(MOODLE_BASE_URL="http://127.0.0.1:8090", MOODLE_WS_TOKEN="token")
    @patch("apps.integration.management.commands.verify_moodle_rest.requests.get")
    def test_reports_invalid_json(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.side_effect = ValueError("bad json")
        with self.assertRaisesMessage(CommandError, "Moodle did not return valid JSON"):
            call_command("verify_moodle_rest")

    @override_settings(MOODLE_BASE_URL="http://127.0.0.1:8090", MOODLE_WS_TOKEN="token")
    @patch("apps.integration.management.commands.verify_moodle_rest.requests.get")
    def test_reports_moodle_exception_payload(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {
            "exception": "moodle_exception",
            "message": "Access control exception",
        }
        with self.assertRaisesMessage(CommandError, "Moodle returned an error: Access control exception"):
            call_command("verify_moodle_rest")

    @override_settings(MOODLE_BASE_URL="http://127.0.0.1:8090", MOODLE_WS_TOKEN="token")
    @patch("apps.integration.management.commands.verify_moodle_rest.requests.get")
    def test_reports_success_for_core_user_get_users(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {"users": []}
        stdout = StringIO()

        call_command("verify_moodle_rest", stdout=stdout)

        self.assertIn("Moodle REST connectivity verified", stdout.getvalue())
        mock_get.assert_called_once()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
export VIRTUAL_ENV='/home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/.venv'
export PATH="$VIRTUAL_ENV/bin:$PATH"
pytest -q backend/apps/integration/tests/test_verify_moodle_rest_command.py
```

Expected: fail because the command module does not exist yet.

- [ ] **Step 3: Create the management package markers**

Create:

`backend/apps/integration/management/__init__.py`

```python
```

`backend/apps/integration/management/commands/__init__.py`

```python
```

- [ ] **Step 4: Implement the command**

Create `backend/apps/integration/management/commands/verify_moodle_rest.py` with:

```python
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Verify Moodle REST connectivity with core_user_get_users."

    def handle(self, *args, **options):
        base_url = getattr(settings, "MOODLE_BASE_URL", "").strip()
        token = getattr(settings, "MOODLE_WS_TOKEN", "").strip()

        if not base_url:
            raise CommandError("MOODLE_BASE_URL is not configured")
        if not token:
            raise CommandError("MOODLE_WS_TOKEN is not configured")

        endpoint = urljoin(base_url.rstrip("/") + "/", "webservice/rest/server.php")
        params = {
            "wstoken": token,
            "wsfunction": "core_user_get_users",
            "moodlewsrestformat": "json",
            "criteria[0][key]": "email",
            "criteria[0][value]": "admin@example.com",
        }

        try:
            response = requests.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CommandError("Unable to reach Moodle REST endpoint") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CommandError("Moodle did not return valid JSON") from exc

        if isinstance(payload, dict) and payload.get("exception"):
            raise CommandError(f"Moodle returned an error: {payload.get('message', payload['exception'])}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Moodle REST connectivity verified via core_user_get_users at {endpoint}"
            )
        )
```

- [ ] **Step 5: Add settings support if needed**

If `settings.py` does not already expose these values, add:

```python
MOODLE_BASE_URL = env("MOODLE_BASE_URL", default="")
MOODLE_WS_TOKEN = env("MOODLE_WS_TOKEN", default="")
```

Place them with the other environment-derived integration settings only if they do not already exist elsewhere.

- [ ] **Step 6: Re-run the tests**

Run:

```bash
export VIRTUAL_ENV='/home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/.venv'
export PATH="$VIRTUAL_ENV/bin:$PATH"
pytest -q backend/apps/integration/tests/test_verify_moodle_rest_command.py
```

Expected: PASS.

- [ ] **Step 7: Document the command in backend README**

Add a section to `backend/README.md`:

```markdown
## Moodle REST Verification

Phase 3 Step 3.1 adds a narrow connectivity check:

```bash
python manage.py verify_moodle_rest
```

Required environment:

- `MOODLE_BASE_URL`
- `MOODLE_WS_TOKEN`

This command only proves local REST connectivity through `core_user_get_users`. It is not the provisioning sync engine.
```

### Task 4: Write The Moodle Admin Runbook, Repo Updates, And Final Verification

**Files:**
- Modify: `infra/README.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/phases/phase-03-moodle-integration/README.md`
- Modify: `docs/phases/phase-03-moodle-integration/CHANGELOG.md`

- [ ] **Step 1: Add the manual Moodle admin runbook to infra README**

Add a dedicated ordered section:

```markdown
## Manual Moodle Web Services Setup

After the Moodle overlay is running:

1. Open `http://127.0.0.1:8090`.
2. Complete the Moodle web installer with the local development values.
3. Go to `Site administration > Plugins > Web services > Overview` and enable web services.
4. Go to `Site administration > Plugins > Web services > Manage protocols` and enable REST.
5. Create a dedicated service user for SIS integration.
6. Go to `Site administration > Server > Web services > External services` and create a service for the SIS.
7. Add the required function `core_user_get_users` to that service.
8. Generate a token for the service user and external service.
9. Store the token in `MOODLE_WS_TOKEN`.
10. Run `python manage.py verify_moodle_rest`.
```

- [ ] **Step 2: Update the root README current status and runbook**

Add:

```markdown
Phase 3 has started with Step 3.1: a local Moodle development instance and REST connectivity proof for later Lane A work.
```

Add a Moodle section under the current test/runbook:

```markdown
### Phase 3 Moodle Connectivity Check

```bash
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle

cd backend
export MOODLE_BASE_URL=http://127.0.0.1:8090
export MOODLE_WS_TOKEN=your-manually-created-token
python manage.py verify_moodle_rest
```
```

- [ ] **Step 3: Update the root changelog**

Append to `CHANGELOG.md`:

```markdown
### Added
- Phase 3 Step 3.1 Moodle overlay, env example, and REST verification command baseline.

### Changed
- Documentation now marks Phase 3 as active and records the manual Moodle web-services runbook.

### Notes
- Step 3.1 intentionally stops at local REST connectivity proof and does not yet implement provisioning sync or LTI.
```

- [ ] **Step 4: Update the Phase 3 README with verification notes**

Add to `docs/phases/phase-03-moodle-integration/README.md`:

```markdown
## Verification Snapshot

- Moodle starts through `infra/docker-compose.moodle.yml`
- `moodle_db` remains internal to the Compose network
- `python manage.py verify_moodle_rest` fails clearly when token or base URL is missing
- `python manage.py verify_moodle_rest` succeeds after manual admin setup and token creation
```

- [ ] **Step 5: Update the Phase 3 changelog**

Append to `docs/phases/phase-03-moodle-integration/CHANGELOG.md`:

```markdown
### Added
- Dedicated Moodle Compose overlay and Moodle env example for Phase 3 Step 3.1.
- Manual admin runbook for web services, REST, service user, external service, token creation, and `core_user_get_users` verification.
- Narrow Django management command for Moodle REST connectivity proof.
```

- [ ] **Step 6: Run the final Step 3.1 verification set**

Run:

```bash
export VIRTUAL_ENV='/home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/.venv'
export PATH="$VIRTUAL_ENV/bin:$PATH"

python - <<'PY'
from pathlib import Path
for path in [
    Path("docs/phases/phase-03-moodle-integration/README.md"),
    Path("docs/phases/phase-03-moodle-integration/CHANGELOG.md"),
    Path("infra/moodle.env.example"),
    Path("infra/docker-compose.moodle.yml"),
]:
    assert path.exists(), path
print("phase3-step31-files-ok")
PY

docker compose -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase config >/tmp/modern-sis-phase3-moodle.yaml

pytest -q backend/apps/integration/tests/test_verify_moodle_rest_command.py
```

Expected:

- `phase3-step31-files-ok`
- Compose config exits `0`
- test file passes

- [ ] **Step 7: Run the live Moodle connectivity proof after manual admin setup**

Run:

```bash
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle

export DJANGO_SECRET_KEY='test-secret-key-with-sufficient-length-1234567890'
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
export MYSQL_DATABASE=modern_sis
export MYSQL_USER=modern_sis
export MYSQL_PASSWORD=modern_sis
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3313
export MOODLE_BASE_URL='http://127.0.0.1:8090'
export MOODLE_WS_TOKEN='paste-manually-created-token-here'

cd backend
python manage.py verify_moodle_rest
```

Expected: success output containing `Moodle REST connectivity verified`.

- [ ] **Step 8: Tear down the Moodle stack**

Run:

```bash
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down
```

Expected: clean shutdown with no effect on default Phase 2 services.

## Self-Review

- Spec coverage: plan covers overlay, env example, manual runbook, narrow verification command, Phase 3 docs, and changelog updates.
- Placeholder scan: no `TBD`, `TODO`, or unresolved task references remain.
- Type consistency: plan consistently uses `verify_moodle_rest`, `MOODLE_BASE_URL`, `MOODLE_WS_TOKEN`, and `infra/docker-compose.moodle.yml`.

