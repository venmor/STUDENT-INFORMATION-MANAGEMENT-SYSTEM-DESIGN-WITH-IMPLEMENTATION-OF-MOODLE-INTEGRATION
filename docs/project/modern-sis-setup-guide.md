# Modern Student Information System Setup Guide

> Converted from `Modern_SIS_Setup_Guide.docx` and normalised to align with `SRS_Modern_SIS.md` v1.1, `ADR-001`, and `docs/architecture/technology-stack.md`. The `.docx` remains historical source material; this Markdown file is the maintained version.

## Overview — What you are building and why this order matters

This guide covers every practical step required to design, build, test, and deploy the Modern SIS platform described in your final year project proposal. The steps are ordered so that each phase produces a stable foundation for the next. Skipping phases or reordering them will cause integration bugs that are extremely difficult to trace.

### Technology stack at a glance

| **Layer** | **Technology** | **Purpose** |
| --- | --- | --- |
| Backend | Python 3.11+ + Django 5 + Django REST Framework | REST API, business logic, RBAC, audit workflows |
| Database | MySQL 8.0 | Relational SIS data store |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS | Role-specific web interfaces |
| Auth | JWT (access + refresh tokens) + RBAC | Secure, stateless authentication |
| Sync engine | Moodle REST web services + Celery + Redis | Provisioning and grade pass-back |
| LTI | PyLTI1p3 + RSA key pair + JWKS endpoint | Embedding SIS tools inside Moodle |
| Vector store | Qdrant | RAG knowledge base for AI co-pilot |
| AI provider layer | OpenAI-compatible gateway | Co-pilot, summarisation, and explanation generation with provider flexibility |
| Containers | Docker + Docker Compose | Reproducible development, staging, and demonstration deployment |
| CI/CD | GitHub Actions | Automated test and build pipeline |

## PHASE 1 — Requirements analysis & system architecture (Weeks 1–2)

*Why first: Everything downstream breaks if the architecture is wrong. Agree on data models, API contracts, and governance before writing a single line of application code.*

### Step 1.1 — Set up your development environment

1. Install Git and create a private GitHub/GitLab repository for the project.
2. Install Node.js 20 LTS and Python 3.11+ on each developer machine.
3. Install Docker Desktop (or Docker Engine on Linux) and Docker Compose.
4. Install VS Code with the Python, ESLint, Prettier, and REST Client extensions.
5. Install Postman or Insomnia for API testing throughout the project.
6. Set up a shared project management board (Trello, Notion, or GitHub Projects) with columns: Backlog, In Progress, Review, Done.

> Tip: Use a .env file per service from day one. Never hardcode credentials anywhere. Add .env to .gitignore immediately.

### Step 1.2 — Write the Software Requirements Specification (SRS)

1. List all functional requirements: student records CRUD, enrollment management, grade management, course catalog, RBAC with four primary roles (student, advisor, faculty, admin), plus the `wellbeing_coordinator` capability flag for designated staff.
2. List all non-functional requirements: response time under 2s for 95% of requests, JWT session expiry, HTTPS only, audit logging, and institutional privacy and consent controls for student data.
3. Document each Moodle integration requirement: which Moodle web service functions you will call, what data flows in each direction.
4. Document each AI capability: co-pilot knowledge sources, staff summarisation workflow, at-risk signal definitions, and wellbeing rules, consent, and escalation criteria.
5. Get supervisor sign-off on the SRS before proceeding.

### Step 1.3 — Design the database schema (MySQL)

1. Draw an Entity-Relationship Diagram (ERD) covering: students, users, roles, courses, enrollments, grades, academic\_standing, attendance\_records, financial\_flags.
2. Add Moodle-link tables: moodle\_user\_map (sis\_user\_id, moodle\_user\_id), moodle\_course\_map (sis\_course\_id, moodle\_course\_id).
3. Add AI and restricted audit tables: ai\_audit\_log (session\_id, user\_id, input\_text, output\_text, approved\_by, timestamp), at\_risk\_alerts (student\_id, signal\_type, severity, advisor\_acknowledged), and wellbeing\_audit\_log in a separate restricted schema.
4. Version-control your schema using Django migrations from day one.
5. Peer-review the ERD with both team members before creating any database objects.

> Tip: Keep the Moodle-link tables separate from your core schema. This makes it easy to re-sync if Moodle IDs ever change.

### Step 1.4 — Define API contracts

1. Write an OpenAPI 3.1 specification (openapi.yaml) before building the backend.
2. Define all REST endpoints: POST /auth/login, GET /students/{id}, POST /enrollments, PUT /grades/{id}, etc.
3. Define the Moodle sync endpoints your system will call internally.
4. Define AI service endpoints: POST /ai/copilot/query, POST /ai/summarise, GET /ai/at-risk/{student\_id}.
5. Share the spec with the supervisor for feedback before implementation.

### Step 1.5 — Write the AI Governance Plan

1. Document which AI capabilities require human approval before outputs become official records.
2. Define audit log retention policy (minimum 2 years).
3. List the NIST AI RMF controls you will implement: GOVERN 1.1 (policies), MAP 1.5 (risk identification), MEASURE 2.5 (bias testing), MANAGE 2.2 (human review queue).
4. Document the wellbeing feature consent flow: how students opt in, what data is stored, who can access it.
5. Get supervisor sign-off before building any AI feature.

> Tip: Print this plan and pin it above your workstation. Every AI feature decision should be checked against it.

## PHASE 2 — Core SIS backend development (Weeks 3–5)

*Why second: You cannot integrate what does not exist. Build and test the SIS in complete isolation so that any bugs surfacing later are clearly integration bugs, not core bugs.*

### Step 2.1 — Bootstrap the backend project

1. Use Django 5 with Django REST Framework as the backend baseline.
2. Create the project structure: /backend (Django app), /frontend (React app), /infra (Docker configs), /docs (SRS, ERD, API spec).
3. Set up a virtual environment and install dependencies: Django, djangorestframework, djangorestframework-simplejwt, mysqlclient, celery, redis, requests, and PyLTI1p3.
4. Configure Django settings to read all secrets from environment variables.
5. Connect to MySQL and run initial migrations.

**Commands**

```bash

python -m venv venv && source venv/bin/activate

pip install django djangorestframework djangorestframework-simplejwt mysqlclient celery redis requests PyLTI1p3

django-admin startproject sis\_backend .

python manage.py migrate

```

### Step 2.2 — Implement authentication and RBAC

1. Implement JWT-based authentication: POST /auth/login returns access\_token (15 min expiry) and refresh\_token (7 day expiry).
2. Create a primary Role model with four roles: STUDENT, ADVISOR, FACULTY, ADMIN.
3. Add support for narrowly scoped capability flags, starting with `wellbeing_coordinator`, without weakening the primary role model.
4. Implement central API access-control middleware backed by named route policies so every protected API endpoint is covered by one shared RBAC enforcement layer. Route-specific decorators should not be the primary enforcement mechanism.
5. Write unit tests for: login with valid credentials, login with wrong password, token refresh, role-based access denial, and capability-gated access.
6. Test all auth endpoints in Postman before moving to the next step.

> Tip: Use Django's built-in password hashing framework with bcrypt (`BCryptSHA256PasswordHasher`) so the implementation matches the SRS requirement for bcrypt with a minimum work factor of 12. Never implement custom password hashing.

### Step 2.3 — Build core SIS modules

1. Student Records module: CRUD for student profiles (personal info, programme, year of study), academic standing (good, probation, suspended), attendance flags.
2. Course Catalog module: CRUD for courses, sections, timetables, credit hours, capacity limits.
3. Enrollment module: enroll student in course (check capacity), drop course, transfer, bulk enrollment upload via CSV.
4. Grade Management module: enter grades per student per course, compute GPA, generate transcript PDF, grade status (draft vs official).
5. User Administration module: create/deactivate accounts, assign roles, reset passwords.
6. Write at least 80% unit test coverage for all modules before moving to Phase 3.

### Step 2.4 — Build the frontend (React 18 + TypeScript + Vite)

1. Scaffold with Vite: npm create vite@latest frontend -- --template react-ts.
2. Install Tailwind CSS, TanStack Query (for server state), React Router, and Axios.
3. Build role-specific dashboards: Student (view grades, register for courses, AI co-pilot chat), Advisor (student search, unified profile view, at-risk alerts), Faculty (grade entry, class roster), Admin (user management, system status).
4. Implement protected routes: redirect unauthenticated users to login, redirect to role-specific home on success.
5. Connect all frontend forms to your REST API endpoints and test end-to-end in the browser.

**Commands**

```bash

npm create vite@latest frontend -- --template react-ts

cd frontend && npm install

npm install tailwindcss @tailwindcss/vite axios @tanstack/react-query react-router-dom

```

> Tip: Build the Advisor unified student profile view early — it will be the most-used screen and will expose data model gaps before you add Moodle data.

### Step 2.5 — Set up continuous integration

1. Create a GitHub Actions workflow: on every push to main, run all backend unit tests and fail the build if coverage drops below 80%.
2. Add a linting step: flake8 for Python, ESLint for TypeScript.
3. Add a docker build step to verify the Docker image builds cleanly.
4. Set up a staging environment (a second Docker Compose stack) separate from your local development environment.

## PHASE 3 — Moodle integration (Weeks 6–9)

*Why third: The SIS must be stable before you wire it to an external system. Establish Lane A (provisioning) first — it is simpler — then tackle Lane B (LTI v1.3), which involves cryptographic flows that take time to debug.*

### Step 3.1 — Stand up a Moodle instance

1. Install Moodle 4.3+ using the official Docker image. Do not use a production Moodle for development.
2. Enable Moodle web services: Site administration > Plugins > Web services > Overview — follow the five-step wizard.
3. Create a dedicated web service user in Moodle with the 'webservice' role.
4. Enable the REST protocol and generate an API token for your SIS service account.
5. Test connectivity: call core\_user\_get\_users from Postman using the token and confirm you receive a JSON response.

**Commands**

```bash

```

## docker-compose.yml snippet for Moodle

services:

moodle:

image: bitnami/moodle:4

ports:

- '8080:8080'

environment:

- MOODLE\_DATABASE\_HOST=db

- MOODLE\_DATABASE\_NAME=moodle

- MOODLE\_DATABASE\_USER=moodle

- MOODLE\_DATABASE\_PASSWORD=secret

### Step 3.2 — Build the provisioning sync engine (Lane A)

1. Create a MoodleSyncService class in your backend that wraps Moodle REST calls using the requests library.
2. Implement user provisioning: when a new student or staff account is created in the SIS, call core\_user\_create\_users in Moodle and store the returned moodle\_user\_id in moodle\_user\_map.
3. Implement course shell provisioning: when a new course section is created in the SIS, call core\_course\_create\_courses in Moodle and store the mapping.
4. Implement enrollment sync: when a student enrolls via the SIS, call enrol\_manual\_enrol\_users in Moodle.
5. Implement grade pass-back: when a final grade is marked official in the SIS, call gradereport\_user\_get\_grade\_items and then core\_grades\_update\_grades to push the grade into Moodle's gradebook.
6. Implement error handling: if a Moodle call fails, log the error, queue a retry via Celery, and alert the admin.
7. Write integration tests against your local Moodle Docker instance.

> Tip: Use event-driven sync (trigger on SIS database events) rather than polling on a cron schedule. It is more responsive and generates less load.

### Step 3.3 — Implement LTI v1.3 tool provider (Lane B)

Step 3.3 implements Lane B. Step 3.1 and Step 3.2 implemented the local Moodle and Lane A foundation; Phase 3.5 remains future scope after Step 3.4.

1. Install or keep the approved LTI dependency footprint: PyLTI1p3 is included in the backend requirements.
2. Generate an RSA key pair for the SIS LTI tool and store it outside tracked source:
   - `openssl genrsa -out local-secrets/lti_private.pem 2048`
   - `openssl rsa -in local-secrets/lti_private.pem -pubout -out local-secrets/lti_public.pem`
3. Configure the SIS with environment variables:
   - `LTI_PLATFORM_ISSUER_ALLOWLIST`
   - `LTI_CLIENT_ID`
   - `LTI_DEPLOYMENT_ID`
   - `LTI_PRIVATE_KEY` or `LTI_PRIVATE_KEY_FILE`
   - `LTI_PUBLIC_KEY` or `LTI_PUBLIC_KEY_FILE`
   - `LTI_KEY_ID`
   - `LTI_PLATFORM_AUTH_LOGIN_URL`
   - `LTI_PLATFORM_AUTH_TOKEN_URL`
   - `LTI_PLATFORM_JWKS_URL`
   - `LTI_LAUNCH_SUCCESS_REDIRECT_BASE`
4. Expose `GET /lti/jwks`. It returns the SIS public key in JWKS format and never returns private key material.
5. Implement `GET /lti/login`. Moodle redirects here first; the SIS validates `iss`, `client_id`, `login_hint`, and `target_link_uri`, creates state/nonce records, and redirects to Moodle's OIDC authorization endpoint.
6. Implement `POST /lti/launch`. It validates the signed Moodle ID token, including signature, issuer, audience/client id, expiry, nonce/state, deployment id, message type, and target link URI.
7. Create a safe SIS-side launch session. The implementation stores a hashed opaque session token, not the raw LTI JWT. Step 3.3 uses DB-backed state/nonce replay protection with a 10-minute expiry because Redis remains optional in the current stack.
8. Map Moodle context to SIS records with `MoodleUserMap` and `MoodleCourseMap`. If mapping is missing, fail safely with a limited unmapped launch context instead of exposing SIS data.
9. Build two LTI-served pages:
   - `/lti/tools/advising-dashboard`: read-only course-context advising workspace with mapped SIS section and roster data when the mapped SIS role is advisor, faculty, or admin.
   - `/lti/tools/registration`: read-only student registration context with mapped SIS student and current enrollments. Register/drop mutations remain in the standard SIS enrollment workflow until Step 3.4 verifies the full action path.
10. Register the SIS as an LTI tool in Moodle: Site administration > Plugins > Activity modules > External tool > Manage tools > Configure a tool manually.
11. Use these local registration values when testing through the shared proxy:
   - Tool URL / launch target: `http://127.0.0.1:8080/lti/tools/advising-dashboard` or `http://127.0.0.1:8080/lti/tools/registration`
   - OIDC login URL: `http://127.0.0.1:8080/lti/login`
   - Redirect URI: `http://127.0.0.1:8080/lti/launch`
   - JWKS URL: `http://127.0.0.1:8080/lti/jwks`
   - Client ID and deployment ID: copy from Moodle into SIS env vars
12. Test the full LTI launch flow from a Moodle course page. Confirm mapped launches show SIS context and unmapped launches show a limited diagnostic context.

**Commands**

```bash
mkdir -p local-secrets
openssl genrsa -out local-secrets/lti_private.pem 2048
openssl rsa -in local-secrets/lti_private.pem -pubout -out local-secrets/lti_public.pem
```

For a fresh-machine Step 3.3 verification path, use `docs/phases/phase-03-moodle-integration/STEP_3_3_TESTING.md`. It documents Linux/Arch, Windows with WSL2 or PowerShell, `.env.local`, MySQL, backend tests, frontend checks, JWKS probing, optional live Moodle launch verification, expected results, and common fixes.

> Tip: LTI launches fail silently in many configurations. Add detailed logging to your launch endpoint from the start so you can see exactly where the OIDC flow breaks.

### Step 3.4 — Verify integration flow and analytics ingestion

1. Create a test student in the SIS and confirm the account appears in Moodle within 5 seconds.
2. Enroll the student in a course via the SIS and confirm Moodle shows the enrollment.
3. Enter a final grade in the SIS and confirm it appears in the Moodle gradebook.
4. Launch the advising dashboard from a Moodle course page and confirm it loads the advisor session, course roster, and student-selection flow correctly.
5. Run the nightly Moodle engagement ETL and confirm updated engagement data lands in the SIS analytics tables before any at-risk processing job runs.
6. Document every test case in a test matrix spreadsheet.

## PHASE 3.5 — SIS operational visibility and completion layer (Planned after Step 3.4)

*Why here: After Step 3.4 proves Moodle integration end-to-end, this planned layer makes the SIS more operationally visible, complete, and demo-ready before AI-heavy phases begin. It is not the next implementation task now. Step 3.3 is complete, Step 3.4 remains next, and Phase 3.5 should start only after Step 3.4 is complete.*

### Step 3.5A — Moodle sync monitoring dashboard

**Purpose**

Make the Step 3.2 Moodle Lane A sync engine visible and manageable from the admin UI.

**Expected deliverables**

1. Admin-only dashboard for Moodle sync state.
2. Views for pending, processed, and failed integration outbox events.
3. Filters by event type, status, date, and related SIS record.
4. Event details showing attempts count, last attempt time, processed time, and last error.
5. Read views for Moodle user mappings and Moodle course mappings.
6. Manual retry action for failed sync events from the UI.

**Non-goals**

- Do not replace the existing sync service.
- Do not add LTI behavior here.
- Do not require live Moodle for normal UI test runs.

### Step 3.5B — Notification center

**Purpose**

Provide in-app notifications for important SIS events across roles.

**Expected deliverables**

1. Notification model covering recipient, title, message, category, read/unread status, severity, optional related-record link, and created timestamp.
2. Student notifications for enrollment success, course drop, grade release, correction-request status, and relevant academic-status changes.
3. Advisor notifications for academic-standing changes, attendance issues, later at-risk alerts, and advising workflow events.
4. Faculty notifications for roster changes, grade-deadline reminders, and section updates.
5. Admin notifications for Moodle sync failures, correction requests, account events, and later AI or wellbeing alerts.
6. Notification bell or notification page with mark-as-read and type filtering.

**Non-goals**

- Do not implement email or SMS delivery unless a later slice scopes it explicitly.
- Start with in-app notifications only.

### Step 3.5C — Audit/admin activity viewer

**Purpose**

Expose existing and future audit logs through a readable admin interface.

**Expected deliverables**

1. Admin-only audit/activity viewer.
2. Views for student record changes, user creation/deactivation, role and capability changes, advisor assignments, grade officialisation and grade changes, and Moodle sync failures/actions.
3. Later support for AI audit-log viewing once Phase 4 is implemented.
4. Filters by actor, action type, target record, module, severity, and date range.
5. Read-only audit UI with no mutation path.

**Non-goals**

- Do not allow editing or deleting audit records.
- Do not expose restricted wellbeing audit data outside authorised wellbeing scope.

### Step 3.5D — Academic calendar and deadline rules

**Purpose**

Centralise academic dates so enrollment, drops, grading, and later AI deadline answers all use the same institutional rules.

**Expected deliverables**

1. Academic year and semester or term records.
2. Academic calendar events.
3. Registration windows and add/drop deadlines.
4. Grade-submission deadlines and exam periods.
5. Student-facing important-date views.
6. Faculty-facing grade-deadline views.
7. Admin calendar-management screens.
8. Future enrollment and drop workflows that consult calendar rules instead of relying only on scattered section dates.
9. Calendar data ready to feed the later RAG knowledge base for co-pilot deadline questions.

**Non-goals**

- Do not build a full timetable scheduler here.
- Do not implement room-conflict optimisation unless a later slice scopes it.

### Step 3.5E — Admin reporting dashboard

**Purpose**

Give admins a high-level institutional view of SIS operations and academic health.

**Expected deliverables**

1. Read-only admin dashboard cards and tables for:
   - total active students
   - students by programme and year
   - active enrollments
   - section capacity usage
   - full or near-full sections
   - students by academic standing
   - low-attendance counts
   - active financial flags
   - grade-submission completion
   - Moodle sync health summary
2. Optional CSV export for straightforward aggregate views.
3. Reporting APIs that stay aggregate and operational rather than becoming a full BI platform.

**Non-goals**

- Do not build a full business-intelligence platform.
- Do not add predictive analytics here; later at-risk and AI phases own that work.

### Step 3.5F — Student document management

**Purpose**

Allow authorised users to attach and manage supporting documents on student records.

**Expected deliverables**

1. Student-linked document records with document type, file reference, uploader, description, visibility level, status, and timestamps.
2. Baseline document types such as NRC/ID, admission letter, transcript, medical note, appeal letter, clearance form, proof document, and other.
3. Admin and advisor upload and view permissions.
4. Student visibility only for document categories explicitly marked student-visible.
5. Audit events when documents are uploaded, viewed, updated, or removed.
6. File storage outside git and outside the committed repository tree.

**Non-goals**

- Do not build a full enterprise document-workflow platform.
- Do not process payments or fee receipts as a billing system.
- Do not expose sensitive documents broadly.

### Step 3.5G — Admissions / applicant intake (Optional/future)

**Purpose**

Optionally model the pre-student applicant stage and convert accepted applicants into SIS users and student records.

**Expected deliverables**

1. Applicant profile and programme-applied-for fields.
2. Application states: draft, submitted, under review, accepted, rejected, waitlisted.
3. Applicant document handling and review notes.
4. Admission decision capture.
5. Conversion flow from accepted applicant into `User` plus `StudentProfile`.
6. Audit trail of review, decision, and conversion.

**Non-goals**

- No payment gateway.
- No full applicant portal unless later approved.
- No scholarship or financial-aid processing.
- No replacement for the core student-record lifecycle.

**Scope gate**

This step is optional/future only. It must not block Step 3.4, Phase 4 AI work, or the main final-year deliverables. Attempt it only if time and supervisor scope allow after most main implementation is complete and before final QA.

## PHASE 4 — Phase 2 AI features: data, co-pilot, and summarisation (Weeks 11–12)

*Why after Phase 3.5: The early AI features depend on clean SIS data, proven Moodle engagement ingestion, and a clearer operational layer for sync visibility, deadlines, reporting, and audit review. Build only the Phase 2 features here; the at-risk engine and wellbeing workflows remain later-phase work.*

### Step 4.1 — Set up the unified data warehouse and vector store

1. Create a scheduled ETL job that copies SIS data (attendance, grades, financial flags, academic standing) into a unified analytics schema.
2. Pull Moodle engagement data periodically via the web services API: last course access time, forum post count, quiz attempt count, assignment submission dates.
3. Install Qdrant as the vector database for RAG.
4. Ingest institution knowledge sources into the vector store: course catalog PDF, academic regulations, registration procedures, academic calendar, fee schedules.
5. Write a test query: 'What is the deadline to drop a course?' and confirm a relevant chunk is retrieved.

**Commands**

```bash

```

## Run Qdrant locally

docker run -p 6333:6333 qdrant/qdrant

pip install qdrant-client openai tiktoken langchain

> Tip: Chunk documents at 512 tokens with 64-token overlap. Test retrieval quality before building the co-pilot on top of it.

### Step 4.2 — Build the student service co-pilot

1. Create a POST /ai/copilot/query endpoint that accepts a natural language question and a student\_id.
2. On each request: embed the question using an embedding model, retrieve the top-5 relevant chunks from the vector store, build a prompt including the retrieved context and the question, and call the configured OpenAI-compatible gateway.
3. Return the answer with source references so the student can verify information.
4. Log every request and response to ai\_audit\_log with timestamp, student\_id, and a confidence flag.
5. If the LLM returns a low-confidence response (detectable via self-evaluation prompt), append: 'Please verify this with the Registrar office.'
6. Test with 20 sample questions covering registration, fees, academic calendar, and graduation requirements.

> Tip: Start with a single hosted provider behind the gateway and keep provider selection environment-configurable. Do not bake provider-specific assumptions into the application layer.

### Step 4.3 — Build staff workflow acceleration (summarisation)

1. Create a POST /ai/summarise endpoint that accepts raw text (advising notes, helpdesk ticket) and returns a structured JSON summary: { key\_issues, recommended\_actions, urgency\_level }.
2. Build a UI component in the Advisor dashboard: paste or type notes, click Summarise, review the AI output, edit it, then click Approve to save it as an official record.
3. The Approve button calls a separate endpoint POST /advising/notes that requires the human-edited text — the raw AI output is never stored as an official record.
4. Log the original text, the AI output, the human edits, and the approving user to ai\_audit\_log.
5. Test with five real-world-style advising scenarios.

## PHASE 5 — Phase 3 at-risk insight engine (Week 13)

*Why after Phase 4: The at-risk engine depends on stable SIS records, completed Moodle engagement ETL, and agreed signal thresholds. It should explain risk after the data pipelines and operational visibility are trustworthy, not before.*

### Step 5.1 — Build the at-risk insight engine

1. Create a Celery periodic task that runs nightly and processes every active student only after the Moodle engagement ETL has completed successfully.
2. For each student, evaluate the configured SIS and Moodle signals using deterministic thresholds stored in configuration, not hardcoded in business logic.
3. Classify each student into low, medium, or high severity based on the active signal combination rules defined in the SRS.
4. For Medium and High severity cases, call the LLM only to generate a short advisor-facing explanation based on the already-determined active signals.
5. Store the result in at\_risk\_alerts with severity, active signals, LLM explanation, creation timestamp, and acknowledged status.
6. Surface High and Medium alerts in the Advisor dashboard as a prioritised list with an Acknowledge action.
7. Log the evaluated signals, prompt, LLM output, and final stored explanation to ai\_audit\_log.

> Tip: The rules classify risk; the LLM explains it. Do not let the model decide severity on its own.

## PHASE 6 — Phase 4 opt-in wellbeing support (Week 14, approval-gated)

*Why after Phase 5: Wellbeing workflows are the most privacy-sensitive and ethically sensitive part of the system. They should be implemented only after policy, staffing, and safeguarding approvals are in place.*

### Step 6.1 — Complete the policy and staffing gate

1. Confirm the institution has approved the wellbeing consent language, retention schedule, deletion policy, and escalation process.
2. Confirm at least one staff member has been assigned the `wellbeing_coordinator` capability and is actively responsible for responding to Escalate notifications.
3. Confirm the restricted wellbeing schema and audit-log design have been reviewed before implementation begins.

### Step 6.2 — Build the opt-in wellbeing support feature

1. Add a Wellbeing Check-in button in the student portal, visible only after the student has explicitly consented in their account settings.
2. The check-in form asks: 'How are you feeling today?' on a 1–5 scale, plus an optional free-text comment.
3. Send the data to POST /ai/wellbeing/triage. Determine the Normal, Concerning, or Escalate classification with a deterministic rules engine using the mood rating and institution-approved keywords/rules.
4. Use the LLM only to help draft supportive wording for non-escalation outcomes if desired. The LLM must never be the sole escalation decision-maker.
5. For Escalate outcomes, create a real-time notification to users assigned the `wellbeing_coordinator` capability and display crisis support contacts to the student.
6. Store wellbeing records in a separate restricted schema and log only minimum safeguarding metadata in the restricted wellbeing audit log.
7. Allow the student to view and delete their own wellbeing history, with free-text content removed irreversibly within 24 hours.
8. Aggregate anonymised weekly mood trends for institutional reporting with no individual student identifiable.

> Tip: This feature should not ship without policy approval, assigned staff coverage, and a tested escalation runbook.

## PHASE 7 — Testing & quality assurance (Week 14)

*Why this order: You cannot test integration before it exists, and you cannot test AI outputs until the data pipelines that feed them are working. Test from the inside out.*

### Step 7.1 — Unit testing

1. Target: 80% code coverage minimum across all backend modules.
2. Use pytest for Python. Run: pytest --cov=. --cov-report=html and review the HTML report for untested branches.
3. Test every API endpoint for: happy path, invalid input (400/422 as applicable), unauthorised access (401/403), and not-found (404).
4. Test every database constraint: duplicate enrollment, enrollment in a full course, grade entry for a non-enrolled student.
5. Use Vitest and React Testing Library for frontend component tests. Test: login form validation, role-based route protection, grade entry form submission.

**Commands**

```bash

pip install pytest pytest-cov pytest-django

pytest --cov=sis\_backend --cov-report=html

# Open the generated htmlcov/index.html report in your browser.

```

### Step 7.2 — Integration testing

1. Test the full SIS-to-Moodle provisioning flow end-to-end: create a student in the SIS API, confirm the Moodle account exists, confirm the moodle\_user\_map entry is correct.
2. Test the grade pass-back flow: enter an official grade in the SIS, confirm it appears in the Moodle gradebook within the expected time window.
3. Test the LTI v1.3 launch flow from Moodle to the advising dashboard using an automated Playwright test.
4. Test the nightly ETL and confirm the at-risk engine does not run when ETL has failed or left stale data.
5. Test the AI co-pilot with 20 sample questions and record whether the answer was accurate, partially accurate, or wrong. Target: at least 85% accuracy on questions answerable from your knowledge base.

### Step 7.3 — Security testing

1. Run OWASP ZAP against the backend API to scan for SQL injection, XSS, and insecure direct object references.
2. Manually test that a student cannot access another student's records by manipulating URL parameters.
3. Verify that all LTI JWT signatures are validated — try replaying an old launch token and confirm it is rejected.
4. Confirm that all AI audit logs are immutable: attempt to delete a log entry via the API and confirm it fails.
5. If wellbeing is enabled, verify that wellbeing records are accessible only to users with the `wellbeing_coordinator` capability and that deleted free-text does not remain in the audit trail.
6. Verify HTTPS is enforced: confirm HTTP requests are redirected to HTTPS and no sensitive data appears in URL query strings.

> Tip: OWASP ZAP is free and Docker-deployable. Run it in active scan mode against your staging environment, not production.

### Step 7.4 — User acceptance testing

1. Recruit at least one representative from each stakeholder group: a student, an academic advisor, a lecturer, and an admin officer.
2. Provide a written UAT scenario for each role. Example student scenario: 'Log in, view your current enrollment, ask the co-pilot when the fee payment deadline is, and, if Phase 4 is enabled, submit a wellbeing check-in.'
3. Observe testers silently — do not guide them. Record where they hesitate or get confused.
4. Collect feedback on a structured form: task success rate, time on task, satisfaction rating (1–5), open comments.
5. Fix all critical usability issues before deployment. Document and backlog non-critical ones.

## PHASE 8 — Deployment, documentation & handover (Week 15)

*A system that cannot be deployed and maintained by someone else is not finished. Write documentation as if you will not be available to explain it.*

### Step 8.1 — Containerise the full stack

1. Write a Dockerfile for the Django backend.
2. Write a Dockerfile for the React frontend (multi-stage: build stage with Node, serve stage with Nginx or Caddy).
3. Write a docker-compose.yml that starts: db (MySQL), redis (Celery broker), backend, frontend, qdrant (vector store), moodle (for testing), and a reverse proxy.
4. Write a docker-compose.prod.yml for the production-like environment with environment variables sourced from a .env.prod file.
5. Test: docker compose up --build and verify all services start cleanly and the full application works.

**Commands**

```bash

docker compose up --build

docker compose ps # all services should show 'running'

curl http://localhost:8000/api/health # should return {status: ok}

```

### Step 8.2 — Write all documentation

1. System Administrator Guide: installation steps, environment variable reference, database backup procedure, how to update Moodle API tokens, how to rotate LTI RSA keys.
2. User Manual — Student: how to log in, view grades, register for courses, use the AI co-pilot, manage wellbeing check-in consent.
3. User Manual — Advisor: how to search for students, read the unified profile, interpret at-risk alerts, acknowledge alerts, use workflow summarisation.
4. User Manual — Faculty: how to enter grades, view class rosters, access the Moodle integration.
5. User Manual — Admin: how to create accounts, assign roles, monitor AI audit logs, generate system reports.
6. API Documentation: export your OpenAPI spec and host it on Swagger UI or Redoc.
7. AI Governance Report: the completed NIST AI RMF compliance record, audit procedures, and bias test results.

> Tip: Use Docusaurus or MkDocs to publish the documentation as a static website — it is much more readable than a single Word file.

### Step 8.3 — Final review and handover

1. Conduct a final demonstration to the supervisor covering all six project objectives.
2. Deliver: all source code in the Git repository with a clean README, all Docker files and scripts, all documentation, the AI governance plan and audit log samples, and the test coverage report.
3. Run a short training workshop (30–60 minutes) for designated institutional staff covering admin tasks and AI feature oversight.
4. Hand over the .env.prod template and secret rotation procedures to the designated system administrator.

## Appendix A — 15-week sprint timeline

| **Week(s)** | **Phase** | **Primary deliverable** |
| --- | --- | --- |
| 1–2 | Phase 1 — Architecture | SRS, ERD, OpenAPI spec, AI governance plan |
| 3 | Phase 2 — Backend core | Auth, RBAC, database migrations, CI pipeline |
| 4 | Phase 2 — SIS modules | Student records, course catalog, enrollment, grades |
| 5 | Phase 2 — Frontend | Role dashboards, protected routes, API integration |
| 6–7 | Phase 3 — Lane A sync | Moodle provisioning, enrollment sync, grade pass-back |
| 8–9 | Phase 3 — Lane B LTI + Step 3.4 verification | LTI v1.3 provider, advising dashboard, registration tool, end-to-end Moodle verification, analytics ingestion proof |
| 10 | Phase 3.5 — Operational visibility layer | Sync monitoring, notifications, audit viewer, calendar/deadline rules, reporting, document-management baseline |
| 11 | Phase 4 — Data & RAG | Unified data warehouse, vector store, knowledge ingestion |
| 12 | Phase 4 — AI features | Co-pilot and workflow summarisation |
| 13 | Phase 5 — At-risk engine | Nightly risk processing, alert explanations, advisor workflow |
| 14 | Phase 6 — Wellbeing support | Consent flow, rules-based triage, restricted audit trail |
| 15 | Phase 7–8 — QA, deployment & handover | Coverage report, integration matrix, OWASP scan, UAT fixes, Docker stack, documentation, final demo, training |

> Note: Step 3.5G Admissions / applicant intake is optional/future. If it is attempted at all, treat it as a scope-contingent enhancement before final QA rather than part of the critical path.

## Appendix B — Key dependencies and install commands

Run these commands in order after cloning the repository.

## 1. Python backend dependencies

pip install django djangorestframework djangorestframework-simplejwt mysqlclient celery redis requests PyLTI1p3 \

openai qdrant-client tiktoken langchain pytest pytest-cov pytest-django

## 2. Frontend dependencies

cd frontend && npm install tailwindcss @tailwindcss/vite axios @tanstack/react-query react-router-dom \

vitest @testing-library/react @testing-library/jest-dom jsdom

## 3. Start all services

docker compose up --build -d

## 4. Run migrations

docker compose exec backend python manage.py migrate

## 5. Run tests

docker compose exec backend pytest --cov=. --cov-report=term

**NOTE** Always create and activate a Python virtual environment before installing backend packages. Never install into the system Python.
