# Delivery Phases

This directory organizes work by delivery phase so planning, scope, and change tracking remain readable as the project moves from documentation into implementation.

## Phases

| Phase | Status | Path | Purpose |
|---|---|---|---|
| Phase 1 - Foundation | Frozen | `phase-01-foundation/` | Documentation baseline, repo structure, schema/API preparation, and change-control setup |
| Phase 2 - Core Build | Complete | `phase-02-core-build/` | Core SIS implementation in isolation: backend/frontend scaffolding, auth, RBAC, and core modules |
| Phase 3 - Moodle Integration | Complete through Step 3.5F | `phase-03-moodle-integration/` | Steps 3.1 through 3.5F establish local Moodle, Lane A sync, Lane B LTI delivery, integration verification, Moodle engagement ingestion, sync monitoring, notifications, audit viewing, calendar rules, reporting, and student documents |
| Phase 3.5 - Operational Visibility & Completion | Complete through Step 3.5F | `phase-03-moodle-integration/` | Step 3.5G Admissions / Applicant Intake is skipped as optional/future scope |
| Phase 4 - AI Foundation | In Progress | `phase-04-ai-foundation/` | Step 4.1 implements unified analytics snapshots, Qdrant/vector-store foundations, institutional knowledge ingestion, and retrieval-only admin verification without implementing co-pilot, summarisation, at-risk scoring, or wellbeing |

## Rules

- Each active phase should have its own `README.md`.
- Each active phase should maintain its own `CHANGELOG.md`.
- Major phase decisions that affect architecture or scope should also update the repository root `CHANGELOG.md`.
