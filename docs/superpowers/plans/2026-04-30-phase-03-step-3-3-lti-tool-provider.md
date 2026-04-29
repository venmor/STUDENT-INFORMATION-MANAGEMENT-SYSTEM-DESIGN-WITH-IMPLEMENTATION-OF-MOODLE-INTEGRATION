# Phase 3 Step 3.3 LTI Tool Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver Moodle Lane B LTI v1.3 tool-provider support with secure launch validation, launch sessions, and usable embedded SIS advising/registration tool pages.

**Architecture:** Extend the existing integration app with focused LTI settings, state/session models, service logic, public launch endpoints, and a protected LTI context API. Frontend LTI routes render backend-validated context instead of trusting Moodle-supplied data directly.

**Tech Stack:** Django 5, PyLTI1p3 dependency footprint, PyJWT/cryptography, React/Vite, pytest, Vitest, Docker Compose runbooks.

---

## File Map

- Modify: `backend/sis_backend/settings.py`
- Modify: `backend/sis_backend/urls.py`
- Modify: `backend/apps/integration/models.py`
- Create: `backend/apps/integration/lti.py`
- Create: `backend/apps/integration/lti_views.py`
- Create: `backend/apps/integration/lti_urls.py`
- Create: `backend/apps/integration/tests/test_lti_tool_provider.py`
- Create: integration migration for `LtiOidcState` and `LtiLaunchSession`
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/src/pages/lti/AdvisingTool.tsx`
- Modify: `frontend/src/pages/lti/RegistrationTool.tsx`
- Create: `frontend/src/api/lti.ts`
- Create: `frontend/src/types/lti.ts`
- Create or modify focused frontend tests if practical
- Modify: `infra/nginx/default.conf`
- Modify: `infra/docker-compose.yml`
- Modify: `infra/moodle.env.example`
- Modify: `infra/README.md`
- Modify: `backend/README.md`
- Modify: `frontend/README.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/project/modern-sis-setup-guide.md`
- Modify: `docs/project/SRS_Modern_SIS.md` only for implemented-detail clarification
- Modify: `docs/phases/phase-03-moodle-integration/README.md`
- Modify: `docs/phases/phase-03-moodle-integration/CHANGELOG.md`

## Task 1: Add Failing Backend LTI Tests

- [ ] Add tests for JWKS public-key exposure and private-key exclusion.
- [ ] Add OIDC login tests for missing parameters, redirect construction, and stored state/nonce.
- [ ] Add launch tests for valid JWT, invalid issuer, invalid audience, expired JWT, missing deployment, missing state, replayed state/nonce, and missing mappings.
- [ ] Add LTI context API tests for denied access without a valid launch cookie and allowed access with a valid launch session.
- [ ] Run targeted tests and confirm they fail because the LTI code does not exist yet:

```bash
cd backend
pytest -q apps/integration/tests/test_lti_tool_provider.py
```

## Task 2: Add LTI Settings And Models

- [ ] Add environment-driven settings for tool key material, platform issuer/client/deployment, platform auth/JWKS endpoints, redirect base, session cookie, and TTLs.
- [ ] Add `LtiOidcState` for state/nonce replay protection.
- [ ] Add `LtiLaunchSession` for hashed opaque launch sessions.
- [ ] Generate and review the migration.
- [ ] Re-run the targeted tests and keep failures focused on missing service/view behavior.

## Task 3: Implement LTI Service Logic

- [ ] Implement public-key-to-JWKS conversion without exposing private material.
- [ ] Implement OIDC login-initiation validation and redirect parameter creation.
- [ ] Implement platform JWKS/public-key resolution.
- [ ] Implement JWT validation for signature, `iss`, `aud`, `exp`, deployment id, message type, target link URI, and state/nonce.
- [ ] Implement Moodle user/course mapping extraction using `MoodleUserMap` and `MoodleCourseMap`.
- [ ] Implement launch-session creation and lookup using hashed opaque tokens.
- [ ] Re-run targeted backend tests until service-level behavior passes.

## Task 4: Implement LTI Views And Routing

- [ ] Add `GET /lti/jwks`.
- [ ] Add `GET /lti/login`.
- [ ] Add CSRF-exempt `POST /lti/launch`.
- [ ] Add protected `GET /lti/api/session` for embedded tool context.
- [ ] Mount `apps.integration.lti_urls` at `/lti/`.
- [ ] Add proxy routing so `/lti/jwks`, `/lti/login`, `/lti/launch`, and `/lti/api/*` reach Django while `/lti/tools/*` stays on the frontend.
- [ ] Re-run targeted LTI tests.

## Task 5: Implement Frontend LTI Pages

- [ ] Add a typed LTI context client with credentialed fetch to `/lti/api/session`.
- [ ] Replace deferred panels with usable launch pages that render loading, denied, unmapped, and mapped states.
- [ ] Advising page shows verified launch metadata, mapped section details, and roster data for mapped advisor/faculty/admin sessions.
- [ ] Registration page shows verified launch metadata, mapped student details, and current enrollment data for mapped student sessions.
- [ ] Ensure no registration mutation is exposed in this slice.
- [ ] Run frontend typecheck/lint/build if practical.

## Task 6: Update Documentation

- [ ] Update setup guide Step 3.3 with implemented env variables, key generation, endpoints, and Moodle registration instructions.
- [ ] Update SRS only to clarify the Step 3.3 DB-backed state/nonce implementation and read-oriented registration slice.
- [ ] Update Phase 3 README and changelog so Step 3.3 is complete, Step 3.4 is next, and Phase 3.5 remains future scope.
- [ ] Update backend, frontend, infra, root README, and root changelog.
- [ ] Ensure docs state no private keys or real secrets are committed.

## Task 7: Verify

- [ ] Run:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/integration/tests/test_lti_tool_provider.py apps/integration/tests/test_moodle_sync_service.py apps/integration/tests/test_process_moodle_sync_command.py apps/integration/tests/test_verify_moodle_rest_command.py
ruff check .
```

- [ ] Run frontend checks if frontend files changed:

```bash
cd frontend
npm run typecheck
npm run lint
npm test -- --run
npm run build
```

- [ ] Run Compose config checks for changed infra:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
docker compose --env-file infra/moodle.env.example -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml --profile later-phase config
```

## Task 8: Finish Branch

- [ ] Review `git diff --check`.
- [ ] Commit with `feat: implement phase 3 step 3.3 LTI tool provider`.
- [ ] Push `feature/phase-03-step-3-3-lti-tool-provider`.
- [ ] Merge to `main`.
- [ ] Push `main`.
- [ ] Ensure local `main` is updated.
- [ ] Confirm no Phase 3.5 implementation was started.
