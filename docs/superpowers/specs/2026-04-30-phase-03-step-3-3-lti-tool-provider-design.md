# Phase 3 Step 3.3 LTI Tool Provider Design

## Status

Approved for implementation by the 2026-04-30 Codex request. The user explicitly requested an end-to-end implementation without repeated approval checkpoints, so this spec records the design used for the implementation slice.

## Context

Phase 3 Step 3.1 established the local Moodle development instance and REST connectivity proof. Phase 3 Step 3.2 added Moodle Lane A provisioning through `MoodleSyncService`, retryable `IntegrationOutboxEvent` records, and `MoodleUserMap` / `MoodleCourseMap` mapping tables.

The remaining Phase 3.3 gap is Lane B: Moodle launching selected SIS tools through LTI v1.3. The SIS stays the authoritative academic/admin system, Moodle stays the learning environment, and no Moodle core code is modified.

Phase 3.5 remains documented future scope only after Step 3.4. This design does not start Phase 3.5.

## Goal

Implement a secure, testable LTI v1.3 tool-provider baseline so Moodle can launch SIS embedded tools for advising and registration.

## Scope

### In Scope

- environment-driven LTI configuration
- public JWKS endpoint at `GET /lti/jwks`
- OIDC login initiation endpoint at `GET /lti/login`
- LTI launch endpoint at `POST /lti/launch`
- JWT signature and claim validation for Moodle launch tokens
- replay-resistant state and nonce storage
- minimal launch-session storage for embedded SIS tools
- mapping launched Moodle users/courses to `MoodleUserMap` and `MoodleCourseMap`
- protected LTI context API for frontend tool pages
- usable minimal pages:
  - `/lti/tools/advising-dashboard`
  - `/lti/tools/registration`
- mocked automated tests without requiring a live Moodle instance
- Moodle registration runbook and documentation updates

### Out Of Scope

- Phase 3.5 dashboards, notifications, reporting, audit viewer, calendar, document management, or admissions intake
- Moodle engagement analytics ETL from Step 3.4
- modifying Moodle core or Moodle database tables
- full LTI administration UI for multiple platforms
- write actions inside the embedded registration tool before the Step 3.4 verification slice hardens the full launch-to-enrollment flow

## Requirements Mapping

- `MI-B-001`: RSA keys configured from environment or untracked files; private keys are never committed.
- `MI-B-002`: `GET /lti/jwks` returns public JWK material only.
- `MI-B-003`: `GET /lti/login` validates Moodle OIDC login-initiation parameters and redirects to Moodle authorization.
- `MI-B-004`: `POST /lti/launch` validates JWT signature, issuer, audience, expiry, nonce/state, deployment, message type, and target URI; then creates a launch session.
- `MI-B-005`: Step 3.3 uses a database-backed nonce/state model with 10-minute expiry because Redis is still a later-phase optional service in the current stack. The model enforces replay protection and can be replaced by Redis without changing the external flow.
- `MI-B-006` through `MI-B-008`: advising tool is launchable, read-only, context-aware, and exposes mapped roster data only when SIS RBAC allows it.
- `MI-B-009` through `MI-B-011`: registration tool is launchable for mapped SIS students and shows a safe read-only registration context; mutating registration actions remain routed through the standard SIS enrollment engine in a later hardened slice.

## Design Decisions

### 1. Keep LTI In The Existing Integration App

`apps.integration` already owns Moodle Lane A and the Moodle mapping models. Lane B will add focused LTI modules in the same app:

- `lti.py` for key, OIDC, JWT, launch-session, and context logic
- `lti_views.py` for HTTP endpoints
- `lti_urls.py` for `/lti/*` URL registration
- focused tests under `apps/integration/tests/`

This keeps all Moodle integration code in one bounded area.

### 2. Use Existing LTI Dependency Footprint

`PyLTI1p3` is already an approved backend dependency. The implementation will use the existing dependency pattern and standard JWT/cryptography primitives available through the installed backend stack. It will not add a new LTI framework or a new dependency unless verification proves the current stack cannot validate Moodle tokens correctly.

### 3. Store Only Minimal State

Add two minimal models:

- `LtiOidcState`: stores `state`, `nonce`, issuer, client id, target URI, optional Moodle hints, expiry, and first-use timestamp.
- `LtiLaunchSession`: stores a hashed opaque session token, launch identifiers, raw safe claim summary, mapped SIS user/course references where available, expiry, and access timestamps.

The raw ID token is not stored. Private key material is not stored in the database.

### 4. Use A Cookie-Backed Launch Session

After a valid launch, the backend creates an opaque session token, stores only its hash, sets an HTTP-only `sis_lti_session` cookie, and redirects to the selected frontend route.

The frontend does not receive or store the raw LTI JWT. Tool pages call `GET /lti/api/session` with browser credentials and render only the context returned by the backend.

### 5. Fail Safely On Missing Mapping

The launch itself may succeed even if Moodle user/course mapping is absent. The tool context API returns a limited unmapped context so operators can see what was launched. It exposes SIS roster, student profile, and enrollment data only when:

- the Moodle launch is valid,
- the session is unexpired,
- the Moodle user maps to an active SIS user,
- the Moodle course maps to a SIS section when the tool needs course data,
- the mapped SIS role is allowed for that tool.

This avoids trusting Moodle roles as the sole authority.

### 6. Keep Embedded Tools Read-Oriented In This Slice

The advising dashboard displays launch context, mapped section details, and a roster when the mapped SIS role is advisor, faculty, or admin. The registration page displays launch context, mapped student details, and current enrollment data when the mapped SIS role is student.

Registration mutations are intentionally not implemented in Step 3.3. They require a tighter end-to-end verification path in Step 3.4 to avoid bypassing SIS enrollment rules through iframe entry points.

## Security Boundaries

- Public unauthenticated endpoints are limited to `GET /lti/jwks`, `GET /lti/login`, and `POST /lti/launch`.
- `/lti/api/session` requires a valid LTI launch cookie.
- Existing JWT/RBAC middleware remains unchanged for `/api/v1/*`.
- Private keys, ID tokens, access tokens, and Moodle REST tokens are not logged.
- Launch validation checks issuer, client id/audience, deployment id, expiry, state, nonce replay, message type, and target link URI.
- Moodle-provided roles are advisory only; SIS data access depends on SIS user mapping and SIS role.

## Testing Strategy

Automated tests use generated in-memory RSA keys and mocked JWT payloads. They do not require a live Moodle instance.

Tests cover:

- JWKS shape and private-material exclusion
- unauthenticated JWKS access
- OIDC missing-parameter failure
- OIDC redirect construction and state/nonce creation
- valid launch session creation
- invalid issuer
- invalid audience/client id
- expired token
- missing deployment id
- missing or replayed nonce/state
- missing Moodle user/course mapping
- mapped user/course launch context
- embedded tool context denied without session
- embedded tool context allowed with valid session
- token/private-key leakage prevention in responses and logs

Manual Moodle verification is documented separately in the Phase 3 runbook.

## Rollback

This slice is additive. Rollback is a normal code/database rollback:

- remove `/lti/*` routes from `sis_backend.urls`
- roll back the integration migration that adds LTI models
- remove LTI environment variables from deployment configuration
- remove Moodle external-tool registration from Moodle admin

No Moodle core changes are required to roll back.
