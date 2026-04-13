# Delivery Phases

This directory organizes work by delivery phase so planning, scope, and change tracking remain readable as the project moves from documentation into implementation.

## Phases

| Phase | Status | Path | Purpose |
|---|---|---|---|
| Phase 1 - Foundation | Active | `phase-01-foundation/` | Documentation baseline, repo structure, schema/API preparation, and change-control setup |
| Phase 2 - Core Build | In Progress | `phase-02-core-build/` | Core SIS implementation in isolation: backend/frontend scaffolding, auth, RBAC, and core modules |
| Phase 3 - Moodle Integration | Planned | `phase-03-moodle-integration/` | Lane A provisioning and Lane B LTI delivery |
| Phase 4 - AI Features | Planned | `phase-04-ai-features/` | Co-pilot, summarisation, at-risk engine, and approval-gated wellbeing support |

## Rules

- Each active phase should have its own `README.md`.
- Each active phase should maintain its own `CHANGELOG.md`.
- Major phase decisions that affect architecture or scope should also update the repository root `CHANGELOG.md`.
