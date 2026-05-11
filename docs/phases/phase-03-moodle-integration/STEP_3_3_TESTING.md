# Phase 3 Step 3.3 LTI Testing Guide

This guide explains how to verify the Phase 3 Step 3.3 Moodle LTI v1.3 implementation from a fresh local setup.

Step 3.2 was Lane A: SIS data moves into Moodle through REST provisioning and sync.

Step 3.3 is Lane B: Moodle launches back into the SIS through a secure LTI v1.3 flow.

Phase 3.5 is future scope only. Do not implement Phase 3.5 features while following this guide.

## What Step 3.3 Added

Step 3.3 added the Moodle LTI v1.3 tool-provider baseline:

- `GET /lti/jwks`
  - exposes the SIS tool public key as JWKS
  - must never expose private key material
- `GET /lti/login`
  - handles Moodle OIDC login initiation
  - validates issuer, client ID, target link URI, and deployment ID when present
  - stores state and nonce records for replay protection
- `POST /lti/launch`
  - validates Moodle's signed LTI launch JWT
  - checks signature, issuer, audience, expiry, nonce/state, deployment ID, message type, and target link URI
  - creates an opaque SIS-side LTI launch session
- `GET /lti/api/session`
  - returns protected launch context to embedded frontend pages after a valid launch
- LTI persistence
  - `LtiOidcState` stores state/nonce records with expiry
  - `LtiLaunchSession` stores hashed launch-session tokens and safe launch context
- Embedded frontend pages
  - `/lti/tools/advising-dashboard`
  - `/lti/tools/registration`
- Mocked backend tests for LTI security and launch behavior
  - keys are generated in tests
  - Moodle JWTs are mocked and signed in tests
  - a live Moodle instance is not required for automated Step 3.3 tests

## Recommended Test Path

For a first verification pass, run the automated checks. They prove the LTI implementation without needing Moodle:

1. Start MySQL.
2. Load local environment variables.
3. Run Django checks and migration drift check.
4. Run the LTI-specific pytest file.
5. Run all integration tests.
6. Run frontend typecheck, lint, test, and build.

Only after those pass, use the optional manual Moodle launch flow.

## Prerequisites

### Linux And Arch Linux

The project baseline is:

- Python 3.11+
- Django 5
- MySQL 8.0
- Node.js 20 LTS or newer
- npm
- Docker and Docker Compose
- OpenSSL

On Arch Linux, install the usual local tooling:

```bash
sudo pacman -Syu
sudo pacman -S git uv python nodejs-lts-iron npm docker docker-compose openssl base-devel pkgconf mariadb-libs
sudo systemctl enable --now docker
docker --version
docker compose version
openssl version
```

If your user is not allowed to run Docker yet:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

If `uv venv --python 3.11 .venv` cannot find Python 3.11 on your machine, install it through uv:

```bash
uv python install 3.11
```

### Windows

Recommended path: use WSL2 with Ubuntu and follow the Linux commands inside WSL2. This is the closest match to the project and avoids native `mysqlclient` build issues.

Install the host tools:

- WSL2 with Ubuntu
- Docker Desktop with WSL integration enabled
- Git
- Node.js LTS if you also want to run the frontend outside WSL
- Python 3.11+ if you also want to run the backend outside WSL

Native PowerShell is possible, but WSL2 is simpler for this project. If you use native PowerShell, make sure these commands work:

```powershell
git --version
python --version
node --version
npm --version
docker --version
docker compose version
openssl version
```

If `openssl` is not available in PowerShell, use one of these:

- Git Bash, which usually includes OpenSSL
- WSL2
- a separately installed OpenSSL binary added to `PATH`

Native Windows note: if `pip install -r backend\requirements\dev.txt` fails while building `mysqlclient`, use WSL2 or install the required Microsoft C++ build tools and MySQL client headers. WSL2 is the recommended fix.

## Environment Loading Rule

The Django settings read environment variables directly. The project does not automatically load `.env.local`.

You must either:

- source `.env.local` in your shell before running backend commands, or
- use a local workflow that exports the same variables, or
- pass variables explicitly to Docker Compose.

The `.env.local` file is intentionally ignored by git through the existing `.env.*` ignore rule. Do not commit local tokens, private keys, or copied LTI launch JWTs.

## Create `.env.local` On Linux, Arch, Or WSL2

From the repository root:

```bash
cat > .env.local <<'EOF'
export DJANGO_SECRET_KEY='local-dev-secret-key-change-me-123456789'
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'

export MYSQL_DATABASE=modern_sis
export MYSQL_USER=modern_sis
export MYSQL_PASSWORD=modern_sis
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3313

export MOODLE_BASE_URL='http://127.0.0.1:8090'
export MOODLE_WS_TOKEN='local-placeholder-token'
export MOODLE_DEFAULT_CATEGORY_ID=1
export MOODLE_STUDENT_ROLE_ID=5
export MOODLE_EDITING_TEACHER_ROLE_ID=3
export MOODLE_INSTITUTION='Student Information System'
export MOODLE_GRADE_SOURCE='modern_sis'

export LTI_PLATFORM_ISSUER_ALLOWLIST='http://127.0.0.1:8090'
export LTI_CLIENT_ID='local-client-id'
export LTI_DEPLOYMENT_ID='local-deployment-id'
export LTI_PRIVATE_KEY_FILE='../local-secrets/lti_private.pem'
export LTI_PUBLIC_KEY_FILE='../local-secrets/lti_public.pem'
export LTI_KEY_ID='modern-sis-lti-local'
export LTI_PLATFORM_AUTH_LOGIN_URL='http://127.0.0.1:8090/mod/lti/auth.php'
export LTI_PLATFORM_AUTH_TOKEN_URL='http://127.0.0.1:8090/mod/lti/token.php'
export LTI_PLATFORM_JWKS_URL='http://127.0.0.1:8090/mod/lti/certs.php'
export LTI_LAUNCH_SUCCESS_REDIRECT_BASE=''
EOF
```

Load it before backend commands:

```bash
. ./.env.local
```

The key file paths above are correct when you run Django from `backend/`, because `../local-secrets/...` points back to the repository root.

## Create PowerShell Environment File

PowerShell cannot source the Bash `export` syntax in `.env.local`. If you are using native PowerShell, create a separate ignored file:

```powershell
@'
$env:DJANGO_SECRET_KEY = "local-dev-secret-key-change-me-123456789"
$env:DJANGO_DEBUG = "true"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"

$env:MYSQL_DATABASE = "modern_sis"
$env:MYSQL_USER = "modern_sis"
$env:MYSQL_PASSWORD = "modern_sis"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3313"

$env:MOODLE_BASE_URL = "http://127.0.0.1:8090"
$env:MOODLE_WS_TOKEN = "local-placeholder-token"
$env:MOODLE_DEFAULT_CATEGORY_ID = "1"
$env:MOODLE_STUDENT_ROLE_ID = "5"
$env:MOODLE_EDITING_TEACHER_ROLE_ID = "3"
$env:MOODLE_INSTITUTION = "Student Information System"
$env:MOODLE_GRADE_SOURCE = "modern_sis"

$env:LTI_PLATFORM_ISSUER_ALLOWLIST = "http://127.0.0.1:8090"
$env:LTI_CLIENT_ID = "local-client-id"
$env:LTI_DEPLOYMENT_ID = "local-deployment-id"
$env:LTI_PRIVATE_KEY_FILE = "..\local-secrets\lti_private.pem"
$env:LTI_PUBLIC_KEY_FILE = "..\local-secrets\lti_public.pem"
$env:LTI_KEY_ID = "modern-sis-lti-local"
$env:LTI_PLATFORM_AUTH_LOGIN_URL = "http://127.0.0.1:8090/mod/lti/auth.php"
$env:LTI_PLATFORM_AUTH_TOKEN_URL = "http://127.0.0.1:8090/mod/lti/token.php"
$env:LTI_PLATFORM_JWKS_URL = "http://127.0.0.1:8090/mod/lti/certs.php"
$env:LTI_LAUNCH_SUCCESS_REDIRECT_BASE = ""
'@ | Set-Content .env.local.ps1
```

Load it before backend commands:

```powershell
. .\.env.local.ps1
```

If PowerShell blocks script loading for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
. .\.env.local.ps1
```

## Generate LTI RSA Keys

Step 3.3 requires an RSA key pair for the SIS LTI tool.

Linux, Arch, or WSL2 from the repository root:

```bash
mkdir -p local-secrets
openssl genrsa -out local-secrets/lti_private.pem 2048
openssl rsa -in local-secrets/lti_private.pem -pubout -out local-secrets/lti_public.pem
chmod 600 local-secrets/lti_private.pem
```

PowerShell from the repository root:

```powershell
New-Item -ItemType Directory -Force local-secrets
openssl genrsa -out local-secrets/lti_private.pem 2048
openssl rsa -in local-secrets/lti_private.pem -pubout -out local-secrets/lti_public.pem
```

Expected result:

- `local-secrets/lti_private.pem` exists
- `local-secrets/lti_public.pem` exists
- the private key is not committed
- the public key is safe to expose through `GET /lti/jwks`

## Start MySQL 8

The local runbooks use port `3313` so they do not collide with a workstation MySQL or MariaDB on `3306`.

Linux, Arch, or WSL2:

```bash
docker run -d --name modern-sis-local-mysql \
  -e MYSQL_DATABASE=modern_sis \
  -e MYSQL_USER=modern_sis \
  -e MYSQL_PASSWORD=modern_sis \
  -e MYSQL_ROOT_PASSWORD=root \
  -p 127.0.0.1:3313:3306 mysql:8

docker exec modern-sis-local-mysql mysql -uroot -proot -e \
  "GRANT ALL PRIVILEGES ON *.* TO 'modern_sis'@'%'; FLUSH PRIVILEGES;"
```

PowerShell:

```powershell
docker run -d --name modern-sis-local-mysql `
  -e MYSQL_DATABASE=modern_sis `
  -e MYSQL_USER=modern_sis `
  -e MYSQL_PASSWORD=modern_sis `
  -e MYSQL_ROOT_PASSWORD=root `
  -p 127.0.0.1:3313:3306 mysql:8

docker exec modern-sis-local-mysql mysql -uroot -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'modern_sis'@'%'; FLUSH PRIVILEGES;"
```

If the container already exists:

```bash
docker start modern-sis-local-mysql
```

PowerShell uses the same command:

```powershell
docker start modern-sis-local-mysql
```

Check readiness:

```bash
docker exec modern-sis-local-mysql mysqladmin ping -h 127.0.0.1 -uroot -proot --silent
```

Expected result:

```text
mysqld is alive
```

## Backend Setup

### Linux, Arch, Or WSL2

From the repository root:

```bash
uv venv --python 3.11 .venv
. .venv/bin/activate
uv pip install -r backend/requirements/dev.txt
. ./.env.local
cd backend
```

Run Django checks and migrations:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
```

Expected results:

- `python manage.py check` reports no system-check issues
- `python manage.py makemigrations --check --dry-run` reports no migration drift
- `python manage.py migrate --noinput` applies migrations or reports no pending migrations

### Native PowerShell

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements\dev.txt
. .\.env.local.ps1
cd backend
```

Run Django checks and migrations:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
```

If dependency installation fails on native Windows, switch to WSL2. That is the supported low-friction path for this backend stack.

## Automated Backend Tests

Run the LTI-specific tests first:

```bash
cd backend
pytest -q apps/integration/tests/test_lti_tool_provider.py
```

Expected result:

- all Step 3.3 LTI tests pass
- current snapshot: `15 passed`
- no live Moodle container is required

Run all Moodle integration tests:

```bash
pytest -q apps/integration/tests
```

Expected result:

- Step 3.1 REST command tests pass
- Step 3.2 Lane A sync tests pass
- Step 3.3 Lane B LTI tests pass
- current snapshot: `32 passed`

Run the full backend confidence suite:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q --cov=apps --cov-report=term-missing
ruff check .
```

Expected result:

- Django checks pass
- migration drift check passes
- pytest passes
- ruff reports no lint errors

## Frontend Setup And Automated Checks

From the repository root:

```bash
cd frontend
npm install
npm run typecheck
npm run lint
npm test
npm run build
```

Expected result:

- TypeScript compiles with no errors
- ESLint reports no errors
- Vitest unit/component tests pass
- Vite production build completes

Current frontend snapshot:

- `npm test` runs the unit/component tests
- `npm run build` includes `tsc -b` before the Vite build
- Step 3.3 frontend pages are validated by typecheck/build and by the backend LTI session-contract tests

Optional browser regression check:

```bash
npx playwright install chromium
npm run test:e2e
```

The current Playwright suite covers the core SIS browser flows. It does not replace the optional live Moodle LTI launch check below.

## Optional Manual JWKS Endpoint Test

This verifies key loading and the public JWKS endpoint without Moodle.

Terminal 1, from the repository root:

```bash
. .venv/bin/activate
. ./.env.local
cd backend
python manage.py runserver 127.0.0.1:8000
```

Terminal 2:

```bash
curl http://127.0.0.1:8000/lti/jwks
```

If `jq` is installed:

```bash
curl -s http://127.0.0.1:8000/lti/jwks | jq .
```

PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/lti/jwks | ConvertTo-Json -Depth 6
```

Expected result:

- HTTP `200`
- JSON shape like:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "modern-sis-lti-local",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

Security check:

- the response must not contain `PRIVATE KEY`
- the response must not contain private RSA parameters such as `d`, `p`, or `q`

Directly opening an LTI frontend page without a launch is expected to show an LTI launch-required error because `/lti/api/session` requires a valid launch cookie.

## Optional Live Moodle Launch Verification

Automated tests are the required Step 3.3 verification path. A live Moodle launch is optional and verifies browser-to-Moodle wiring.

### 1. Start Moodle

From the repository root:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

Open Moodle:

```text
http://127.0.0.1:8090
```

Local bootstrap login:

- username: `admin`
- password: `ChangeMe123!`

If Moodle loads as unstyled HTML, stop the Moodle overlay, remove the Moodle volumes, keep `MOODLE_HOST` empty, and start again:

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

### 2. Start The SIS Backend And Frontend

For a host-run live LTI launch, use Django on `8000` and Vite on `5173`.

Backend terminal:

```bash
. .venv/bin/activate
. ./.env.local
export LTI_LAUNCH_SUCCESS_REDIRECT_BASE='http://127.0.0.1:5173'
cd backend
python manage.py migrate --noinput
python manage.py seed_demo_sis
python manage.py runserver 127.0.0.1:8000
```

PowerShell backend terminal:

```powershell
.\.venv\Scripts\Activate.ps1
. .\.env.local.ps1
$env:LTI_LAUNCH_SUCCESS_REDIRECT_BASE = "http://127.0.0.1:5173"
cd backend
python manage.py migrate --noinput
python manage.py seed_demo_sis
python manage.py runserver 127.0.0.1:8000
```

Frontend terminal:

```bash
cd frontend
npm run dev
```

Open the frontend once to confirm it is available:

```text
http://127.0.0.1:5173
```

### 3. Register The SIS As A Moodle External Tool

In Moodle admin:

1. Go to `Site administration > Plugins > Activity modules > External tool > Manage tools`.
2. Choose `Configure a tool manually`.
3. Use a clear name, such as `Modern SIS Advising`.
4. Use LTI version `LTI 1.3`.
5. Set the tool URL or target link URI to one embedded frontend page:
   - `http://127.0.0.1:5173/lti/tools/advising-dashboard`
   - or `http://127.0.0.1:5173/lti/tools/registration`
6. Set the OIDC login initiation URL:
   - `http://127.0.0.1:8000/lti/login`
7. Set the redirect URI:
   - `http://127.0.0.1:8000/lti/launch`
8. Set the public keyset or JWKS URL:
   - `http://127.0.0.1:8000/lti/jwks`
9. Save the tool.
10. Copy Moodle's generated client ID and deployment ID.

If Moodle asks for a public key directly instead of a JWKS URL, paste the contents of `local-secrets/lti_public.pem`. Never paste or upload `local-secrets/lti_private.pem` into Moodle.

Update your local environment with Moodle's generated values:

```bash
export LTI_CLIENT_ID='paste-moodle-client-id-here'
export LTI_DEPLOYMENT_ID='paste-moodle-deployment-id-here'
```

PowerShell:

```powershell
$env:LTI_CLIENT_ID = "paste-moodle-client-id-here"
$env:LTI_DEPLOYMENT_ID = "paste-moodle-deployment-id-here"
```

Restart the Django server after changing these values.

### 4. Launch From A Moodle Course

1. Create or open a Moodle course.
2. Add an `External tool` activity using the configured Modern SIS tool.
3. Open the activity from the course page.
4. Watch the Django terminal logs for:
   - `GET /lti/login`
   - `POST /lti/launch`
   - `GET /lti/api/session`

Expected result for a valid but unmapped launch:

- Moodle starts the OIDC flow.
- Django validates the launch.
- The browser redirects to the selected `/lti/tools/*` page.
- The page shows a limited or unmapped launch context.
- SIS roster, student profile, and enrollment data are not exposed until Moodle IDs map to SIS records.

Expected result for a mapped launch:

- Advising dashboard shows mapped SIS user, section, and roster data when the mapped SIS role is `ADVISOR`, `FACULTY`, or `ADMIN`.
- Registration page shows mapped SIS student and current enrollments when the mapped SIS role is `STUDENT`.

Important: an unmapped launch is not a Step 3.3 failure. It means LTI validation worked, but Lane A mapping data is not present for that Moodle user or course.

## Optional Lane A REST Verification

This is not required for the mocked Step 3.3 tests, but it helps prepare mapped live launches.

After you create the Moodle REST service user and token through the Phase 3 runbook, replace the placeholder token:

```bash
export MOODLE_WS_TOKEN='paste-the-generated-token-here'
cd backend
python manage.py verify_moodle_rest
```

Expected result:

- `Moodle REST connectivity verified.`
- a matched user count
- first matched Moodle username and Moodle user ID

Optional explicit lookup:

```bash
python manage.py verify_moodle_rest --username sis.service
```

Process pending Moodle sync work:

```bash
python manage.py process_moodle_sync
```

Retry failed work:

```bash
python manage.py process_moodle_sync --failed
```

## Expected Results Summary

| Check | Command | Expected result |
| --- | --- | --- |
| Django system check | `python manage.py check` | no system-check issues |
| Migration drift | `python manage.py makemigrations --check --dry-run` | no model changes detected |
| LTI pytest | `pytest -q apps/integration/tests/test_lti_tool_provider.py` | all LTI tests pass, current snapshot `15 passed` |
| Integration pytest | `pytest -q apps/integration/tests` | all integration tests pass, current snapshot `32 passed` |
| Full backend pytest | `pytest -q --cov=apps --cov-report=term-missing` | all backend tests pass |
| Backend lint | `ruff check .` from `backend/` | no lint errors |
| Frontend typecheck | `npm run typecheck` from `frontend/` | TypeScript passes |
| Frontend lint | `npm run lint` from `frontend/` | ESLint passes |
| Frontend tests | `npm test` from `frontend/` | Vitest passes |
| Frontend build | `npm run build` from `frontend/` | production build completes |
| JWKS endpoint | `curl http://127.0.0.1:8000/lti/jwks` | public JWK only, no private key material |
| Live Moodle launch | launch external tool from a Moodle course | redirects into `/lti/tools/*` with mapped or limited context |

## Common Errors And Fixes

### `KeyError: 'DJANGO_SECRET_KEY'`

Cause: environment variables were not loaded.

Fix:

```bash
. ./.env.local
cd backend
python manage.py check
```

PowerShell:

```powershell
. .\.env.local.ps1
cd backend
python manage.py check
```

### `Can't connect to MySQL server`

Cause: MySQL container is not running or `MYSQL_PORT` does not match the published port.

Fix:

```bash
docker start modern-sis-local-mysql
docker ps --filter name=modern-sis-local-mysql
```

Confirm `.env.local` has:

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3313
```

### `Access denied for user 'modern_sis'`

Cause: the local test database user does not have enough privileges to create the Django test database.

Fix:

```bash
docker exec modern-sis-local-mysql mysql -uroot -proot -e \
  "GRANT ALL PRIVILEGES ON *.* TO 'modern_sis'@'%'; FLUSH PRIVILEGES;"
```

### `mysqlclient` Fails To Install

Arch Linux fix:

```bash
sudo pacman -S base-devel pkgconf mariadb-libs
uv pip install -r backend/requirements/dev.txt
```

Windows fix: use WSL2. Native Windows may require Microsoft C++ build tools and MySQL client headers.

### `LTI public key is not configured`

Cause: the RSA keys do not exist or the key path is wrong for the current working directory.

Fix from the repository root:

```bash
mkdir -p local-secrets
openssl genrsa -out local-secrets/lti_private.pem 2048
openssl rsa -in local-secrets/lti_private.pem -pubout -out local-secrets/lti_public.pem
. ./.env.local
cd backend
python manage.py runserver 127.0.0.1:8000
```

The documented `.env.local` uses `../local-secrets/...` because Django commands are run from `backend/`.

### `/lti/api/session` Returns 401

Cause: there is no valid LTI launch cookie.

Fix: open the LTI tool through Moodle, not directly in the browser. Direct visits to `/lti/tools/advising-dashboard` or `/lti/tools/registration` are expected to show a launch-required state.

### `/lti/login` Returns A Client Or Issuer Error

Cause: Moodle's issuer, client ID, or deployment ID does not match the SIS environment.

Fix:

1. Copy the Moodle-generated client ID and deployment ID.
2. Update `LTI_CLIENT_ID` and `LTI_DEPLOYMENT_ID`.
3. Confirm `LTI_PLATFORM_ISSUER_ALLOWLIST` matches Moodle's issuer, usually `http://127.0.0.1:8090` for this local runbook.
4. Restart Django after changing environment variables.

### Moodle Launch Redirects To The Wrong Host

Cause: `LTI_LAUNCH_SUCCESS_REDIRECT_BASE` is missing for the host-run Django plus Vite workflow.

Fix:

```bash
export LTI_LAUNCH_SUCCESS_REDIRECT_BASE='http://127.0.0.1:5173'
```

PowerShell:

```powershell
$env:LTI_LAUNCH_SUCCESS_REDIRECT_BASE = "http://127.0.0.1:5173"
```

Restart Django and launch again.

### Moodle Loads As Plain Or Unstyled HTML

Cause: Moodle initialized with the wrong `MOODLE_HOST`.

Fix: keep `MOODLE_HOST` empty for local use and recreate the Moodle volumes with the reset commands in this guide.

### Port Already In Use

Common local ports:

- Django: `8000`
- Vite: `5173`
- SIS MySQL: `3313`
- Moodle: `8090`
- SIS dev proxy: `8080`

Fix: stop the conflicting process or change the relevant local port. Keep the environment variables and Moodle tool URLs consistent with the new port.

### PowerShell Cannot Run `.env.local.ps1`

Cause: the current process execution policy blocks local script loading.

Fix:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
. .\.env.local.ps1
```

## Cleanup

Stop Django and Vite with `Ctrl+C`.

Stop the local MySQL container:

```bash
docker rm -f modern-sis-local-mysql
```

Stop Moodle:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  down
```

Keep `local-secrets/` and `.env.local` only on your machine. Do not commit them.
