# ADR-001: Technology Baseline And Delivery Phasing

## Status
Accepted

## Context
The original SRS and setup material described multiple interchangeable stack options:

- Django or FastAPI
- React or Vue
- Docker or Kubernetes-style deployment language
- generic ORM and migration wording

That flexibility was useful during proposal drafting, but it creates avoidable implementation risk now. The repository currently contains requirements and architecture documents only. There is no existing application code that would justify preserving multiple stack options.

The project also includes higher-risk areas such as Moodle integration, AI governance, and wellbeing workflows. These need a low-complexity implementation baseline and phased delivery.

## Decision
Adopt the following baseline for v1:

- Backend: Python 3.11+, Django 5, Django REST Framework
- Frontend: React 18, TypeScript, Vite
- Database: MySQL 8.0
- Async and background jobs: Celery + Redis
- Moodle integration: Moodle REST web services API + PyLTI1p3
- AI gateway: OpenAI-compatible provider abstraction
- Vector store: Qdrant
- Deployment: Docker Compose for development and staging, Docker-based Linux deployment for production
- CI/CD: GitHub Actions

Delivery is phased:

1. Phase 1: SIS core, auth/RBAC, audit logging, Moodle Lane A
2. Phase 2: Moodle Lane B, student co-pilot, staff summarisation
3. Phase 3: At-risk engine
4. Phase 4: Wellbeing support after institutional privacy and safeguarding approval

## Rationale

- Django reduces incidental complexity for authentication, admin-style workflows, ORM-backed models, and migrations.
- React + Vite keeps the frontend modern without introducing unnecessary SSR or hosting complexity.
- MySQL already exists as an SRS dependency, so changing the primary store now would add churn without benefit.
- Celery + Redis is a boring and reliable answer for sync, ETL, and nightly processing.
- Docker-based deployment is easier to set up, debug, and demonstrate than Kubernetes for this project stage.
- Phasing isolates the hardest and most ethically sensitive work until the core operational system is stable.

## Consequences

### Positive
- Fewer moving parts before the first working increment
- Cleaner alignment between requirements, diagrams, and implementation
- Easier onboarding for reviewers and future contributors
- Lower risk of architecture drift during development

### Negative
- Future migration to a different backend or frontend stack becomes an explicit change rather than an open option
- Some scalability and platform patterns remain intentionally deferred until evidence justifies them

## Deferred

- Native mobile clients
- Kubernetes orchestration
- Multi-tenant architecture
- Direct payment processing
- LLM-only wellbeing triage

## Review Trigger
Revisit this ADR only if one of the following happens:

- the supervisor requires a different deployment/runtime constraint
- the institution mandates a different database or hosting platform
- a future phase needs a capability the current baseline cannot reasonably support
