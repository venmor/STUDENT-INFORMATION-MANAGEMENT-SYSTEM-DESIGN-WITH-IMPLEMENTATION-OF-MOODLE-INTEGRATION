# Modern SIS Technology Stack

## Status

This document is the authoritative technology-stack recommendation for the Modern SIS project. It reflects the locked baseline in `SRS_Modern_SIS.md` v1.1 and supersedes older optional stack wording in earlier planning documents.

## Recommended Stack

| Area | Recommended technology | Why this was favored |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite + React Router + TanStack Query + Tailwind CSS | Strong ecosystem, fast development loop, explicit typing, good fit for role-based dashboards, and low deployment complexity |
| Backend API | Python 3.11+ + Django 5 + Django REST Framework | Mature, boring, and reliable stack for CRUD-heavy systems, RBAC, admin workflows, ORM-backed modeling, and migrations |
| Authentication | JWT access/refresh tokens | Matches the SRS, supports SPA frontend integration cleanly, and keeps API boundaries explicit |
| Primary database | MySQL 8.0 | Relational fit for SIS transactions, consistent with current SRS assumptions, and straightforward for academic records and reporting |
| Background jobs | Celery + Redis | Proven answer for retries, Moodle sync, ETL, scheduled processing, and at-risk batch jobs |
| Cache / coordination | Redis | Needed for Celery broker/backing store, rate limiting, nonce storage, and short-lived coordination data |
| Moodle integration | Moodle REST web services API + PyLTI1p3 | Standard Moodle-compatible approach with the least protocol risk |
| Vector store | Qdrant | Simple dedicated vector database for RAG, easy to self-host in Docker, and avoids overloading the transactional database |
| AI provider layer | OpenAI-compatible gateway | Keeps the app provider-flexible while enforcing audit, rate-limit, and governance controls in one place |
| Object/file storage | S3-compatible storage | Good fit for source documents, transcript exports, and imported knowledge-base assets |
| Reverse proxy / TLS | Caddy or Nginx | Clean HTTPS termination and routing in a Docker-based deployment |
| CI/CD | GitHub Actions | Fits the repository workflow and supports test/build/deploy automation without extra platform complexity |
| Local / demo deployment | Docker Compose on Linux VM | Best operational fit for Django, Celery, Redis, MySQL, Qdrant, and Moodle-connected workflows |

## Why This Stack Was Favored

### 1. It fits the shape of the product

This system is not a simple content site or single-purpose API. It is a multi-role academic operations platform with:

- heavy relational data modeling
- access control and audit requirements
- background processing
- external system integration
- retrieval-backed AI features
- privacy-sensitive workflows

That favors a conventional full-stack architecture over a highly fragmented or heavily serverless design.

### 2. It optimizes for correctness and maintainability over novelty

The project has more to lose from architectural complexity than from missing theoretical scalability. Django, DRF, Celery, Redis, and MySQL are all well understood, well documented, and easy to reason about under project constraints.

### 3. It matches the current SRS and architecture work

The current SRS v1.1 already assumes:

- Django migrations
- MySQL
- Celery retry queues
- Redis-backed nonce and rate-limiting behavior
- Docker-based deployment

The recommended stack keeps the technical baseline aligned with those assumptions instead of reopening core architecture decisions.

### 4. It keeps Moodle integration straightforward

Moodle integration is already one of the highest-risk parts of the project. Adding extra deployment or runtime novelty would only make debugging harder. Python and Django keep the Moodle REST and LTI integration surface predictable.

### 5. It supports staged capability rollout cleanly

The same stack can handle:

- Wave 1 core SIS + provisioning
- Wave 2 embedded tools + co-pilot + summarisation
- Wave 3 at-risk engine
- Wave 4 wellbeing support

without a platform rewrite between phases.

## Detailed Stack Rationale

### Frontend: React 18 + TypeScript + Vite

Chosen because:

- dashboards and role-specific interfaces map cleanly to React component composition
- TypeScript improves safety on forms, API contracts, and permission-aware UI logic
- Vite keeps local iteration fast and avoids unnecessary framework complexity
- React has better long-term hiring and ecosystem depth than trying to keep multiple frontend options open

### Backend: Django 5 + Django REST Framework

Chosen because:

- the product is CRUD-heavy and policy-heavy, which suits Django extremely well
- Django admin is useful for controlled internal operations and debugging
- the ORM and migration system reduce accidental schema drift
- DRF gives predictable REST patterns for the frontend and future integration
- Django is easier to hand over and maintain than a more custom FastAPI architecture for this project

### Database: MySQL 8.0

Chosen because:

- SIS data is strongly relational
- transactional consistency matters for enrollments, grades, and audit trails
- the current SRS already commits to MySQL
- it is easy to provision, back up, and run in a demo or production-like environment

### Redis + Celery

Chosen because:

- retryable Moodle sync is a first-class requirement
- nightly ETL and at-risk jobs need background execution
- Redis also solves nonce storage and rate limiting without adding another service
- Celery is a proven fit for exactly this kind of Python workload

### Qdrant

Chosen because:

- the AI layer needs document retrieval, not a second transactional database
- Qdrant is easy to run in Docker and purpose-built for vector search
- it keeps RAG concerns isolated from core SIS data storage

## Database Architecture

The recommended data layer is intentionally split by purpose:

- `MySQL`: authoritative SIS data, audit records, mappings, advising notes, enrollment state
- `Redis`: queue broker, short-lived locks, rate limiting, LTI nonce storage
- `Qdrant`: vector embeddings for co-pilot knowledge retrieval
- `S3-compatible object storage`: PDFs, imported source docs, exported transcripts, static artifacts if needed

This split is favored because it keeps each store doing one job well instead of forcing one database to handle unrelated workloads.

## Deployment Recommendation

### Primary recommendation

Deploy the demo and first production-like environment on a Linux VM using Docker Compose.

Recommended services:

- `frontend`
- `backend`
- `celery-worker`
- `celery-beat`
- `redis`
- `mysql`
- `qdrant`
- `caddy` or `nginx`

Why this was favored:

- closest match to the current architecture
- easiest to operate and debug
- simplest way to host background workers
- easiest way to demonstrate Moodle sync and LTI callbacks end-to-end
- fewer hidden platform constraints than a serverless deployment

### Demonstration note

For demonstration, correctness and predictability matter more than elastic scaling. A single well-configured VM is a better demo platform than a more fragmented deployment with multiple platform assumptions.

## Vercel Analysis

### Short answer

Vercel is not the best primary deployment platform for the full current architecture.

### Why not as the primary host

The current design depends on:

- Django
- Celery workers
- Redis
- MySQL
- scheduled ETL and retryable background jobs
- Moodle integration callbacks

Those are more naturally hosted in a long-running container-based environment than in a frontend-first serverless platform.

### Where Vercel can still help

Vercel can be useful in a hybrid setup for:

- frontend preview deployments
- supervisor review links
- polished UI demonstrations

### Best Vercel use for this project

If desired later:

- deploy the React frontend to Vercel
- keep backend, worker, Redis, MySQL, and Qdrant on a Linux host

That gives you a clean frontend demo experience without forcing the whole system into a mismatched hosting model.

## Alternatives Considered And Not Favored

### FastAPI instead of Django

Not favored because:

- it would require more explicit architecture work for admin-heavy workflows
- the project benefits more from convention than flexibility
- the current problem is delivery risk, not raw framework performance

### Vue instead of React

Not favored because:

- it adds no decisive benefit for this project
- React has the stronger ecosystem fit for the expected team and demo lifecycle
- the stack had to be narrowed, not kept open

### PostgreSQL + pgvector instead of MySQL + Qdrant

Not favored for v1 because:

- the SRS already assumes MySQL
- changing the core DB now adds churn without solving a real constraint
- Qdrant gives dedicated vector capability without changing the transactional baseline

### Kubernetes for deployment

Not favored because:

- it adds operational complexity well beyond the needs of the current project
- the current goal is a stable demonstration and maintainable first implementation
- Docker Compose is easier to explain, run, and debug

## Document Alignment Note

The following documents are aligned with this stack recommendation:

- `SRS_Modern_SIS.md`
- `docs/architecture/ADR-001-technology-baseline.md`
- `docs/superpowers/specs/2026-04-11-modern-sis-preimplementation-design.md`
- `docs/diagrams/modern-sis-erd.md`
- `docs/diagrams/legacy/modern-sis-system-architecture.svg`

The following legacy planning document still contains older optional choices and should be treated as historical context unless revised:

- `Modern_SIS_Setup_Guide.docx`
