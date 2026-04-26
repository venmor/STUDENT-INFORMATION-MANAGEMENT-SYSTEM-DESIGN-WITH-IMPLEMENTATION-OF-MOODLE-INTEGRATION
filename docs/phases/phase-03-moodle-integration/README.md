# Phase 3 Moodle Integration

## Objective

Phase 3 introduces Moodle integration in controlled slices so Lane A REST provisioning and Lane B LTI work can build on the stable Phase 2 SIS baseline.

## Scope

- stand up a local Moodle development environment
- prove SIS-to-Moodle REST connectivity
- implement Lane A provisioning after connectivity is proven
- implement Lane B LTI only after Lane A is stable

## Status

- Status: In Progress
- Source guide: `docs/project/modern-sis-setup-guide.md` Phase 3
- Completed step: Step 3.1 Moodle development instance and REST connectivity proof
- Next step: Step 3.2 provisioning sync engine for Lane A

## Current Step

- Step 3.1 is complete on this implementation slice: Moodle starts through a dedicated overlay and REST connectivity is proven through the SIS verification command.
- Step 3.2 is now next: provisioning sync engine for Lane A.

## Expected Deliverables

- dedicated Moodle Compose overlay
- Moodle-specific env template
- manual admin runbook for web services and REST
- SIS-side `core_user_get_users` verification command

## Implementation Progress

- dedicated Moodle overlay added at `infra/docker-compose.moodle.yml`
- isolated Moodle env template added at `infra/moodle.env.example`
- base placeholder services tightened to include Moodle bootstrap variables, MariaDB health checks, and persisted `/bitnami/moodledata`
- SIS-side verification command added at `python manage.py verify_moodle_rest`
- backend regression tests added for missing config, network failure, invalid JSON, Moodle exception payloads, and success output

## Manual Runbook

### 1. Start The Local Moodle Slice

From the repository root:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

Check status:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  ps
```

Moodle is published on `http://127.0.0.1:8090`.

### 2. Wait For The First-Run Moodle Bootstrap

- The Bitnami container performs the initial Moodle installation from the bootstrap values in `infra/moodle.env.example`
- leave `MOODLE_HOST` empty for this local slice so Moodle follows the incoming host and port from the browser request
- Wait until the container stops running `admin/cli/install.php` and the site responds on `http://127.0.0.1:8090`
- Then sign in with the bootstrap admin account
- The default bootstrap values for this slice are:
  - username: `admin`
  - password: `ChangeMe123!`
  - email: `admin@example.com`
  - site name: `Student Information System Moodle`

If the page loads as unstyled HTML or asset links point to `http://127.0.0.1/` without `:8090`, the site was initialized with the wrong `MOODLE_HOST`. Reset the Moodle volumes, keep `MOODLE_HOST` empty for local use, and start again:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down

docker volume rm \
  modern-sis_moodle_data \
  modern-sis_moodle_runtime_data \
  modern-sis_moodle_db_data

docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

### 3. Enable Web Services

In Moodle admin:

- go to `Site administration > Advanced features`
- enable `Enable web services`
- save changes

### 4. Enable The REST Protocol

- go to `Site administration > Server > Web services > Manage protocols`
- enable `REST`

### 5. Create A Dedicated Service User

- go to `Site administration > Users > Accounts > Add a new user`
- create a dedicated non-human account such as `sis.service`
- use a strong password and a non-personal email address

### 6. Create And Assign A Minimal System Role

`core_user_get_users` is not usable with a bare user account. For this Step 3.1 proof, create a minimal system role and assign it to the dedicated service user:

- go to `Site administration > Users > Permissions > Define roles`
- add a new role with no archetype, for example:
  - name: `SIS Web Service Integration`
  - short name: `siswebservice`
- allow these capabilities:
  - `webservice/rest:use`
  - `moodle/user:viewdetails`
  - `moodle/user:viewhiddendetails`
  - `moodle/course:useremail`
- assign that role to `sis.service` at `Site administration > Users > Permissions > Assign system roles`

Step 3.1 is a read-only connectivity proof. Do not add broader user or course modification capabilities at this stage. Introduce any required write permissions later in Step 3.2 when provisioning sync is implemented and the exact least-privilege write scope is known.

### 7. Create A Custom External Service

- go to `Site administration > Server > Web services`
- choose `Add a new custom service`
- recommended name: `Modern SIS REST`
- enable `Authorised users only`
- save the service

### 8. Add The Verification Function

- open the new service
- add the function `core_user_get_users`

This Step 3.1 slice verifies only that single function. Do not broaden the service yet.

### 9. Authorise The Service User

- open the service's `Authorised users` screen
- add the dedicated `sis.service` user you created

### 10. Generate A Token

- go to `Site administration > Server > Web services > Manage tokens`
- add a token for the dedicated service user and the `Modern SIS REST` service
- copy the generated token immediately

### 11. Store The Token For The SIS Backend

In the backend terminal:

```bash
export MOODLE_BASE_URL='http://127.0.0.1:8090'
export MOODLE_WS_TOKEN='paste-the-generated-token-here'
```

If you maintain a local untracked env file for backend commands, store the same values there instead.

### 12. Verify REST Connectivity

With the backend virtualenv active:

```bash
cd backend
python manage.py verify_moodle_rest
```

Expected success output:

- `Moodle REST connectivity verified.`
- matched user count
- first matched username and Moodle user id

Optional explicit lookup:

```bash
python manage.py verify_moodle_rest --username sis.service
```

### 13. Tear Down The Moodle Slice

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down
```

## Verification Snapshot

- overlay config resolves cleanly through `docker compose ... config`
- targeted backend command tests pass in `backend/apps/integration/tests/test_verify_moodle_rest_command.py`
- default Phase 2 dev and staging overlays remain unchanged
- Step 3.1 stops at local REST connectivity proof; provisioning sync and LTI remain later steps
- live REST proof succeeded against the documented Compose overlay on `http://127.0.0.1:8090`
- live REST proof succeeded against a real Moodle token with `python manage.py verify_moodle_rest --username sis.service`

## Troubleshooting

- if Moodle serves a blank or unstyled page after local bootstrap, reset the Moodle-specific volumes and keep `MOODLE_HOST` empty for local use
- if you run PHP CLI commands inside the Moodle container for debugging, run them as the web user to avoid cache permission regressions:

```bash
docker exec -u daemon <moodle-container> php -r 'define("CLI_SCRIPT", true); require "/opt/bitnami/moodle/config.php";'
```

## Exit Criteria

- local Moodle starts without changing default Phase 2 startup
- manual Moodle web-services setup is documented clearly
- the verification command proves REST connectivity with a real token

## Tracking

- [Phase 3 Changelog](CHANGELOG.md)
- [Setup Guide](../../project/modern-sis-setup-guide.md)
- [SRS](../../project/SRS_Modern_SIS.md)
