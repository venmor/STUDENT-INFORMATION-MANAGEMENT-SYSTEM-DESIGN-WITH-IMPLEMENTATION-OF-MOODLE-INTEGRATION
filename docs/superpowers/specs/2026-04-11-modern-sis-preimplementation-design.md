# Modern SIS Pre-Implementation Design

## Status
Approved for repository baseline preparation. This document summarizes the design decisions captured in SRS v1.1 and the supporting architecture artifacts added before any application code is scaffolded.

## Goal
Turn the SRS from a high-quality concept document into a build-ready baseline with explicit technology choices, clear access boundaries, phased delivery, and supporting architecture artifacts that reduce design churn during implementation.

## Baseline Decisions

| Area | Decision | Why |
|---|---|---|
| Backend | Django 5 + Django REST Framework | Lowest-risk Python stack for auth, ORM, admin workflows, and migrations |
| Frontend | React 18 + TypeScript + Vite | Strong component model with a small deployment surface and no unnecessary framework complexity |
| Database | MySQL 8.0 | Matches existing SRS assumptions and keeps transactional SIS data in a familiar relational store |
| Async jobs | Celery + Redis | Proven fit for Moodle sync, ETL, and nightly risk processing |
| Moodle integration | REST web services + PyLTI1p3 | Standard Moodle integration path with the least custom protocol work |
| AI layer | OpenAI-compatible gateway + Qdrant | Keeps provider choice flexible while supporting RAG and auditability |
| Deployment | Docker-based Linux deployment | Simpler and more realistic than introducing Kubernetes in v1 |

## Key Corrections Applied To The SRS

1. The stack ambiguity was removed by locking the implementation baseline.
2. Moodle cross-references were corrected so enrollment sync and grade pass-back point to the right integration requirements.
3. The role model was tightened:
   - exactly one primary role
   - optional `wellbeing_coordinator` capability for restricted access
4. Advisor access was narrowed from "any student" to assigned advisees.
5. Financial flags and advising records were made explicit because other requirements already depended on them.
6. The wellbeing feature was de-risked:
   - rules-first triage
   - no LLM-only escalation decision
   - deletion rules that do not conflict with audit retention
7. The Moodle + SIS relationship was clarified as:
   - event-driven SIS to Moodle provisioning
   - scheduled Moodle to SIS analytics ingestion
   - LTI launch-based embedded tools

## Architecture Shape

### Core flow
- The SIS remains the administrative source of truth.
- Moodle receives provisioned users, sections, enrollments, and official grades from SIS events.
- Moodle engagement data is pulled into the analytics/vector layer on a scheduled basis.
- AI features consume institution-approved documents, SIS projections, and Moodle engagement summaries through a controlled gateway.

### Access boundaries
- `Admin` has full administrative scope.
- `Advisor` works only on assigned advisees.
- `Faculty` works only on assigned sections.
- `Student` works only on self-service and self-visibility surfaces.
- `wellbeing_coordinator` is a capability flag, not a new primary role.

### Data sensitivity boundaries
- SIS operational data lives in the main relational schema.
- Wellbeing data lives in a restricted schema.
- General AI logs live in `ai_audit_log`.
- Wellbeing events use a separate `wellbeing_audit_log` with minimal retained metadata.

## Delivery Plan Baseline

| Phase | Outcome |
|---|---|
| Phase 1 | Working SIS core + auth/RBAC + Moodle provisioning lane |
| Phase 2 | Embedded LTI tools + co-pilot + staff summarisation |
| Phase 3 | At-risk engine using stable SIS + Moodle analytics inputs |
| Phase 4 | Wellbeing support only after policy and safeguarding approval |

## Artifact Map

| Artifact | Path | Purpose |
|---|---|---|
| Repository index | `README.md` | Top-level purpose statement and document index for the repository |
| Docs index | `docs/README.md` | Directory-level entry point for maintained documentation |
| Revised SRS | `SRS_Modern_SIS.md` | Authoritative requirements baseline |
| Stack ADR | `docs/architecture/ADR-001-technology-baseline.md` | Locks the implementation stack and phasing rationale |
| Technology stack | `docs/architecture/technology-stack.md` | Explains the selected stack, database layout, and deployment recommendation |
| Architecture diagrams | `docs/architecture/architecture-diagrams.md` | Mermaid-based system, workflow, and deployment diagrams |
| ERD | `docs/diagrams/modern-sis-erd.md` | Shared domain model before schema creation |
| OpenAPI starter | `docs/api/openapi.yaml` | Initial contract surface for Phase 1 and Phase 2 APIs |
| Phase 1 foundation | `docs/phases/phase-01-foundation/README.md` | Phase-scoped baseline and deliverables tracker |
| Phase 1 changelog | `docs/phases/phase-01-foundation/CHANGELOG.md` | Phase-specific change tracking |
| Version control guide | `docs/process/version-control.md` | Branching, commit, tagging, and changelog conventions |

## Immediate Next Step
Do not scaffold the application yet. Review the revised SRS and these artifacts together, then decide whether the next move is:

1. schema-first design and migrations
2. API-first refinement of the OpenAPI contract
3. a formal implementation plan for Phase 1 only
