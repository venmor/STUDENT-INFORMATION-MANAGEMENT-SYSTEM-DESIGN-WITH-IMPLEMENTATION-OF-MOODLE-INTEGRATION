# Phase 3.5 Operational Visibility Documentation Design

## Status

Documentation-only design prepared on 2026-04-27 for a planned future enhancement layer. This slice updates project documentation only and does not authorize or implement runtime work.

## Context

The repository currently reflects:

- Phase 2 complete on `main`
- Phase 3 Step 3.1 complete
- Phase 3 Step 3.2 complete
- Phase 3 Step 3.3 as the next implementation step
- Phase 3 Step 3.4 as the verification and analytics-ingestion close-out step after LTI

The current gap is not implementation. The gap is that the authoritative planning documents do not yet describe the operational-completion layer that should sit between proven Moodle integration and the later AI, at-risk, and wellbeing phases.

That missing layer matters because several high-value SIS capabilities are neither pure Moodle integration nor AI:

- sync monitoring and retry visibility
- notifications
- audit viewing
- calendar/deadline centralisation
- aggregate admin reporting
- student document handling
- optional applicant intake

Without documenting that layer now, future implementation sessions would be forced to invent scope and sequencing.

## Goal

Insert a planned future layer named `Phase 3.5 — SIS Operational Visibility and Completion Layer` into the project documentation so that:

- Step 3.3 remains the immediate next implementation step
- Step 3.4 remains the required integration proof step after LTI
- Phase 3.5 is explicitly documented as starting only after Step 3.4
- the SRS, setup guide, phase docs, indexes, and changelogs all agree on the sequence
- a future implementation session can build each Phase 3.5 slice without inventing requirements

## Scope

### In Scope

- update the setup guide to insert Phase 3.5 between Step 3.4 and Phase 4
- update the SRS with planned operational-completion requirements and IDs
- update the Phase 3 README so the future sequence is explicit
- update the phase index and docs index
- update the root README roadmap wording
- update root and Phase 3 changelogs
- add documentation-only superpowers spec and plan artifacts for traceability

### Out Of Scope

- backend code
- frontend code
- migrations
- APIs
- models
- tests
- runtime configuration
- any Step 3.3, Step 3.4, or Phase 3.5 implementation work

## Required Ordering

The documentation must preserve this sequence exactly:

1. Phase 3 Step 3.3 — LTI v1.3 tool-provider delivery
2. Phase 3 Step 3.4 — full integration verification and analytics ingestion
3. Phase 3.5 — SIS Operational Visibility and Completion Layer
4. Phase 4 — AI data, RAG, and workflow acceleration

`Step 3.3` must remain the immediate next implementation step after this documentation update.

## Phase 3.5 Structure To Document

### Step 3.5A — Moodle Sync Monitoring Dashboard

Document as a planned admin-only operational UI over the existing Step 3.2 foundation:

- `IntegrationOutboxEvent`
- `MoodleUserMap`
- `MoodleCourseMap`
- `process_moodle_sync`
- the Moodle Lane A sync engine

The documented scope must include filtering, status visibility, mapping visibility, attempts/error display, and manual retry actions from the UI.

### Step 3.5B — Notification Center

Document as in-app notifications first:

- recipient
- title/message
- category/type
- read or unread status
- severity or priority
- optional deep link
- role-relevant academic and operational events

The docs must explicitly exclude email/SMS gateways unless later scoped.

### Step 3.5C — Audit/Admin Activity Viewer

Document as a read-only admin console over existing and future audit records:

- student record change history
- user and role changes
- advisor assignment changes
- grade officialisation and change events
- Moodle sync events
- later AI audit visibility

The docs must explicitly forbid editing or deleting audit events through the UI.

### Step 3.5D — Academic Calendar and Deadline Rules

Document as the central source for:

- academic year and term records
- registration windows
- add/drop deadlines
- grade-submission deadlines
- exam periods

The docs must state that future enrollment/drop enforcement and later AI deadline answers should use these rules rather than scattered dates.

### Step 3.5E — Admin Reporting Dashboard

Document as lightweight institutional reporting, not BI:

- active students
- programme/year distributions
- enrollment totals
- section capacity usage
- academic standing breakdown
- low-attendance counts
- active financial flags
- grade-submission completion
- Moodle sync health summary

CSV export may be documented as optional where straightforward.

### Step 3.5F — Student Document Management

Document as secure student-linked file handling with:

- document type
- file metadata
- uploader
- visibility
- access control
- audit logging

The docs must state that uploaded files are stored outside git and that broad exposure of sensitive documents is prohibited.

### Step 3.5G — Admissions / Applicant Intake

Document as `optional/future` only.

It must be clearly marked as:

- not part of the immediate Step 3.3 or Step 3.4 path
- not a blocker for Phase 4
- only implementable later if time and supervisor scope allow, ideally after most main implementation and before final QA

## SRS Design Decisions

### 1. Put Phase 3.5 In Functional Requirements, Not In Moodle Or AI Sections

These capabilities are cross-cutting SIS operational features. They are not strictly Moodle API requirements and they are not AI features. The clearest home is a new planned functional-requirements subsection after existing core SIS modules.

Recommended section:

- `3.6 Operational Visibility & Completion Enhancements`

### 2. Use Explicit Planned Requirement IDs

The SRS update will define:

- `FR-OPS-001` Moodle sync monitoring dashboard
- `FR-OPS-002` Notification center
- `FR-OPS-003` Audit/admin activity viewer
- `FR-OPS-004` Academic calendar and deadline rules
- `FR-OPS-005` Admin reporting dashboard
- `FR-DOC-001` Student document management
- `FR-ADM-001` Admissions / applicant intake, optional/future

These IDs are sufficient to anchor future design and testing work without claiming implementation now.

### 3. Update The Rollout Baseline Separately From Implementation Order

The SRS rollout table should acknowledge that the operational-completion layer sits after proven Moodle integration and before AI-heavy phases. That makes the planning sequence consistent with the updated setup guide while preserving the fact that Step 3.3 remains next.

## Setup Guide Design Decisions

### 1. Insert A Separate `PHASE 3.5` Heading

Do not bury these items under Step 3.4 or Phase 4. They are distinct from both and need their own planning identity.

### 2. Keep Each 3.5 Item At The “Future Slice” Level

Each Step 3.5A–3.5G should include:

- purpose
- expected deliverables
- non-goals

That is enough guidance for future implementation while staying honest that nothing is being built now.

### 3. Preserve Step 3.3 As Next

The setup guide must explicitly say that:

- Step 3.3 is still next
- Step 3.4 remains the verification gate before Phase 3.5 starts

### 4. Treat 3.5G As Scope-Contingent

Admissions must be documented as optional/future and excluded from the core dependency chain.

## Files To Update

- `docs/project/modern-sis-setup-guide.md`
- `docs/project/SRS_Modern_SIS.md`
- `docs/phases/phase-03-moodle-integration/README.md`
- `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- `docs/phases/README.md`
- `docs/README.md`
- `README.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-04-27-phase-03-5-operational-visibility-documentation.md`
- `docs/superpowers/plans/2026-04-27-phase-03-5-operational-visibility-documentation.md`

## Acceptance Criteria

This documentation slice is complete when:

- the setup guide includes Phase 3.5 after Step 3.4 and before Phase 4
- the SRS includes planned operational-completion requirements and IDs
- the Phase 3 README states that Step 3.3 remains next and Phase 3.5 follows Step 3.4
- the docs indexes and root README reflect the new planned layer
- root and Phase 3 changelogs record the documentation change
- no code, models, tests, migrations, or runtime behavior are added

## Verification

Reasonable verification for this slice:

- `git diff --check`
- inspect changed Markdown with `sed`
- grep for misleading wording such as `implemented Phase 3.5` or `completed Phase 3.5`
- grep for `Step 3.3` to confirm it remains the next implementation step
