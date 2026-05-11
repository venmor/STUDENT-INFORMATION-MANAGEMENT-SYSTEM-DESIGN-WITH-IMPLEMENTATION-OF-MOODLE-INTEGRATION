# Phase 3 Step 3.1 Moodle Development Instance Design

## Status

Approved for spec drafting on 2026-04-26 in the active Codex session. Awaiting user review before implementation planning.

## Context

Phase 2 is complete through Step 2.5. The repository now has:

- a working Django backend
- a working React frontend
- repeatable local and staging Compose workflows
- CI, coverage, and container validation

The next setup-guide item is `Phase 3 Step 3.1 — Stand up a Moodle instance` in [docs/project/modern-sis-setup-guide.md](/home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/docs/project/modern-sis-setup-guide.md). The SRS establishes Moodle REST web services as the foundation for Lane A provisioning and reconciliation, while LTI v1.3 is a separate later Step 3.3 concern.

The repository already contains `moodle` and `moodle_db` as later-phase placeholders in the shared base Compose file. Step 3.1 therefore does not need a new platform design. It needs:

- a controlled way to activate the existing Moodle placeholders
- documented environment variables for Moodle bootstrap and SIS-side REST access
- a manual administrator runbook for Moodle web-service setup
- a small verification path proving `core_user_get_users` works locally

## Goal

Provide a local Dockerized Moodle development environment and a documented manual setup flow that proves the SIS can reach Moodle's REST API with a manually created token.

## Scope

### In Scope

- add a dedicated Phase 3 Compose overlay for Moodle activation
- keep Moodle isolated from normal Phase 2 backend/frontend development
- document Moodle bootstrap environment variables
- document manual Moodle admin steps for web services and REST setup
- add SIS-side environment variable support for Moodle base URL and token storage
- add a small verification command proving `core_user_get_users` connectivity
- update phase, infra, and repository documentation and changelogs

### Out Of Scope

- Moodle provisioning sync engine
- Moodle user or course mapping models
- Celery-backed retry workflows for Moodle calls
- LTI v1.3 implementation
- automated Moodle admin bootstrap through browser/UI scripting
- adding Moodle to required CI
- making Moodle a dependency of the default Phase 2 dev workflow

## Requirements Mapping

### Setup Guide Alignment

This step must satisfy the `Step 3.1 — Stand up a Moodle instance` requirements:

1. install a local Moodle 4.3+ development instance using Docker
2. enable web services
3. create a dedicated web-service user
4. enable the REST protocol
5. generate an API token
6. verify connectivity with `core_user_get_users`

### SRS Alignment

This step supports the prerequisites for Moodle integration defined in [docs/project/SRS_Modern_SIS.md](/home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/docs/project/SRS_Modern_SIS.md):

- Section `5.1 Lane A — Provisioning & Synchronisation`
- `MI-A-005` and related REST-based integration calls
- assumption that an institutional or development Moodle instance exists with web services enabled
- constraint that Moodle integration must use standard Moodle web services and must not modify Moodle core

## Design Decisions

### 1. Use A Dedicated Moodle Overlay

The base Compose file will continue to define `moodle` and `moodle_db` as later-phase placeholder services. Step 3.1 will activate them through a dedicated overlay:

- `infra/docker-compose.moodle.yml`

Startup will require explicit intent, for example:

```bash
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

This preserves the stability of the normal Phase 2 developer workflow. A developer working only on the SIS backend or frontend should not pay the cost or complexity of a Moodle runtime unless they are actively doing Phase 3 integration work.

### 2. Keep Moodle Off Default Dev Startup

The existing Phase 2 dev and staging runbooks must continue to work without Moodle. Step 3.1 must not:

- change `infra/docker-compose.dev.yml` to start Moodle by default
- make backend or frontend depend on `moodle`
- require Moodle variables for normal local backend/frontend startup

This isolation is intentional. Step 3.1 proves REST connectivity only. The rest of the system should remain operational without Moodle running.

### 3. Publish Moodle On A Safe Local Port

The Moodle overlay will publish Moodle on a dedicated host port, defaulting to:

- `127.0.0.1:8090`

This avoids collisions with:

- the Phase 2 frontend dev server on `5173`
- the shared reverse-proxy dev path on `8080`
- the staging proxy path on `8088`

`moodle_db` will remain internal to the Compose network unless a documented future need requires exposure.

### 4. Add Dedicated Moodle Environment Examples

Step 3.1 will add:

- `infra/moodle.env.example`

This file will document two distinct classes of variables.

#### Moodle container bootstrap variables

These exist to make local Moodle startup repeatable:

- `MOODLE_HOST`
- `MOODLE_SITE_NAME`
- `MOODLE_USERNAME`
- `MOODLE_PASSWORD`
- `MOODLE_EMAIL`
- `MOODLE_DB_NAME`
- `MOODLE_DB_USER`
- `MOODLE_DB_PASSWORD`
- `MOODLE_DB_ROOT_PASSWORD`
- `MOODLE_HTTP_PORT`

The exact variable names will match the current Bitnami Moodle container contract.

#### SIS-side verification variables

These exist for the local REST connectivity check:

- `MOODLE_BASE_URL`
- `MOODLE_WS_TOKEN`

`MOODLE_WS_TOKEN` will be explicitly documented as a value created manually inside Moodle admin during Step 3.1. No token-generation automation will be added in this step.

### 5. Manual Moodle Admin Setup Is The Intended Workflow

Step 3.1 deliberately stops short of UI automation. The runbook will document the exact manual setup flow:

1. start `moodle` and `moodle_db`
2. complete initial Moodle web installation
3. enable web services
4. enable REST protocol
5. create a dedicated service user
6. create an external service
7. assign the necessary capability or functions for the verification call
8. generate a token for the service user
9. place the token into `MOODLE_WS_TOKEN`
10. run the verification command

This is acceptable for Step 3.1 because the purpose is proving local REST connectivity, not building a production-grade Moodle administration automation layer.

### 6. Verification Will Be A Small Django Management Command

The verification tool should live in the backend integration area rather than as a standalone shell script. The preferred design is a Django management command under `backend/apps/integration/management/commands/`.

Responsibilities:

- read `MOODLE_BASE_URL` and `MOODLE_WS_TOKEN`
- call Moodle's REST endpoint using `core_user_get_users`
- print a clear success message with high-signal response details
- fail clearly for:
  - missing token
  - missing base URL
  - HTTP connection failure
  - REST disabled or wrong endpoint behavior
  - invalid JSON
  - Moodle exception payloads

Non-responsibilities:

- no retry queues
- no sync engine abstraction
- no user provisioning
- no persistence of Moodle IDs

This keeps the command aligned to Step 3.1's narrow purpose.

### 7. Documentation And Versioning Will Follow The Existing System

Step 3.1 will add active Phase 3 tracking artifacts:

- `docs/phases/phase-03-moodle-integration/README.md`
- `docs/phases/phase-03-moodle-integration/CHANGELOG.md`

It will update:

- `docs/README.md`
- `docs/phases/README.md`
- `infra/README.md`
- `README.md`
- `CHANGELOG.md`

The documentation updates will:

- mark Phase 3 as active
- explain how Step 3.1 starts Moodle without affecting Phase 2
- document the manual Moodle admin runbook
- document the verification command
- capture the verification evidence in the same phase/versioning style used in earlier steps

## File Plan

### Create

- `infra/docker-compose.moodle.yml`
- `infra/moodle.env.example`
- `backend/apps/integration/management/__init__.py`
- `backend/apps/integration/management/commands/__init__.py`
- `backend/apps/integration/management/commands/verify_moodle_rest.py`
- `backend/apps/integration/tests/test_verify_moodle_rest_command.py`
- `docs/phases/phase-03-moodle-integration/README.md`
- `docs/phases/phase-03-moodle-integration/CHANGELOG.md`

### Modify

- `infra/README.md`
- `README.md`
- `CHANGELOG.md`
- `docs/README.md`
- `docs/phases/README.md`

### Possible Minor Modify

- `backend/README.md`

Only if needed to document the new management command and Moodle env variables from the backend side.

## Verification Strategy

Step 3.1 completion will require fresh evidence for:

- Compose config validation with the Moodle overlay
- successful startup of `moodle_db` and `moodle`
- local Moodle HTTP reachability on the dedicated host port
- management-command failure behavior when required env vars are absent
- management-command success path after manual Moodle admin setup and token creation

Expected manual verification path:

```bash
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle

python manage.py verify_moodle_rest
```

The exact command name may change slightly during implementation, but its behavior must remain limited to `core_user_get_users` connectivity proof.

## Risks And Mitigations

### Risk: Moodle container variable drift

Mitigation:

- verify against the current Bitnami Moodle README during implementation
- keep the env example tightly scoped to variables actually used in this repo

### Risk: Runbook ambiguity in Moodle admin steps

Mitigation:

- write the manual steps explicitly and in order
- document where token creation happens and where the token is stored afterward

### Risk: Step 3.1 quietly expands into Step 3.2

Mitigation:

- keep the verification command deliberately narrow
- avoid sync abstractions, queue logic, or persistence models in this step

### Risk: Moodle destabilizes ordinary developer workflows

Mitigation:

- require the dedicated overlay and explicit profile activation
- avoid adding Moodle to default dev or CI paths

## Exit Criteria

Step 3.1 is complete when all of the following are true:

- Moodle can be started locally through a dedicated Phase 3 overlay
- Moodle is not required for the default Phase 2 development workflow
- `infra/moodle.env.example` exists and documents both bootstrap and token variables
- the manual admin runbook clearly covers web services, REST, service user, external service, token creation, and token storage
- a small SIS-side verification command exists for `core_user_get_users`
- the verification command fails clearly on missing token, unreachable Moodle, disabled REST/web services, and invalid JSON
- the verification command succeeds after manual Moodle admin setup
- Phase 3 README and changelog exist
- repo and phase documentation are updated in the established versioning system

