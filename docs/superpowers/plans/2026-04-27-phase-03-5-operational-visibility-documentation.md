# Phase 3.5 Operational Visibility Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans when implementing this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document a planned `Phase 3.5 — SIS Operational Visibility and Completion Layer` after Phase 3 Step 3.4 and before Phase 4 without implementing any application code.

**Architecture:** This is a documentation-only slice. Update the setup guide, SRS, phase documentation, indexes, and changelogs so they all describe the same future sequence: Step 3.3 next, Step 3.4 verification after that, then Phase 3.5 as a planned enhancement layer.

**Tech Stack:** Markdown documentation, git worktree workflow, repository changelog conventions

---

## Status

Plan written on 2026-04-27 from the approved documentation brief and the current Phase 3 repository state.

## File Map

- Create: `docs/superpowers/specs/2026-04-27-phase-03-5-operational-visibility-documentation.md`
- Create: `docs/superpowers/plans/2026-04-27-phase-03-5-operational-visibility-documentation.md`
- Modify: `docs/project/modern-sis-setup-guide.md`
- Modify: `docs/project/SRS_Modern_SIS.md`
- Modify: `docs/phases/phase-03-moodle-integration/README.md`
- Modify: `docs/phases/phase-03-moodle-integration/CHANGELOG.md`
- Modify: `docs/phases/README.md`
- Modify: `docs/README.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`

## Task 1: Add Documentation Traceability Artifacts

- [ ] Create the documentation-only spec in `docs/superpowers/specs/2026-04-27-phase-03-5-operational-visibility-documentation.md`.
- [ ] Create the documentation-only plan in `docs/superpowers/plans/2026-04-27-phase-03-5-operational-visibility-documentation.md`.
- [ ] Keep both files explicit that this slice does not implement code, tests, migrations, or runtime behavior.

## Task 2: Update The Setup Guide

- [ ] Insert `Phase 3.5 — SIS Operational Visibility and Completion Layer` after Step 3.4 and before Phase 4 in `docs/project/modern-sis-setup-guide.md`.
- [ ] Add Steps `3.5A` through `3.5G`.
- [ ] For each step, document:
  - purpose
  - expected deliverables
  - non-goals
- [ ] Preserve the sequencing language that Step 3.3 remains the next implementation step and Step 3.4 remains the required precursor to Phase 3.5.
- [ ] Update the sprint-timeline appendix so Phase 3.5 appears after Moodle integration and before AI work.
- [ ] Mark Step `3.5G Admissions / Applicant Intake` as optional/future and non-blocking.

## Task 3: Update The SRS

- [ ] Bump the SRS version and revision history in `docs/project/SRS_Modern_SIS.md`.
- [ ] Add `3.6 Operational Visibility & Completion Enhancements` under Functional Requirements.
- [ ] Add requirement IDs:
  - `FR-OPS-001`
  - `FR-OPS-002`
  - `FR-OPS-003`
  - `FR-OPS-004`
  - `FR-OPS-005`
  - `FR-DOC-001`
  - `FR-ADM-001`
- [ ] Make the section explicit that these are planned post-Step-3.4 enhancements, not current implementation.
- [ ] Update the rollout/capability guidance so Phase 3.5 appears after Moodle integration and before AI-heavy phases.
- [ ] Mark admissions as optional/future and non-MVP unless later approved.

## Task 4: Update The Phase Guides And Indexes

- [ ] Update `docs/phases/phase-03-moodle-integration/README.md` with a `Planned Phase 3.5 After Step 3.4` section.
- [ ] Keep `Step 3.3` listed as the next implementation step.
- [ ] Add concise descriptions for `3.5A` through `3.5G`.
- [ ] Update `docs/phases/README.md` so the phase table mentions the planned Phase 3.5 layer.
- [ ] Update `docs/README.md` so the project-level docs index reflects the newly documented roadmap layer if needed.

## Task 5: Update The Repository README And Changelogs

- [ ] Update `README.md` current-status wording so it says:
  - Step 3.3 remains next
  - Step 3.4 remains the verification gate
  - Phase 3.5 is documented as planned after Step 3.4
- [ ] Update `CHANGELOG.md` with documentation-only wording.
- [ ] Update `docs/phases/phase-03-moodle-integration/CHANGELOG.md` with documentation-only wording.
- [ ] Ensure no changelog entry claims implementation.

## Task 6: Verify The Documentation Slice

- [ ] Run:

```bash
git diff --check
```

- [ ] Inspect key changed sections with:

```bash
sed -n '150,320p' docs/project/modern-sis-setup-guide.md
sed -n '1,220p' docs/project/SRS_Modern_SIS.md
sed -n '1,220p' docs/phases/phase-03-moodle-integration/README.md
```

- [ ] Confirm no misleading wording exists:

```bash
rg -n "implemented Phase 3\\.5|completed Phase 3\\.5|Phase 3\\.5 is complete" \
  docs README.md CHANGELOG.md
```

- [ ] Confirm Step 3.3 remains next:

```bash
rg -n "Step 3\\.3|next implementation step" \
  docs/phases/phase-03-moodle-integration/README.md README.md docs/project/modern-sis-setup-guide.md
```

## Task 7: Commit, Merge, And Push

- [ ] Commit with:

```bash
git add docs/project/modern-sis-setup-guide.md \
  docs/project/SRS_Modern_SIS.md \
  docs/phases/phase-03-moodle-integration/README.md \
  docs/phases/phase-03-moodle-integration/CHANGELOG.md \
  docs/phases/README.md \
  docs/README.md \
  README.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-04-27-phase-03-5-operational-visibility-documentation.md \
  docs/superpowers/plans/2026-04-27-phase-03-5-operational-visibility-documentation.md
git commit -m "docs: add phase 3.5 operational visibility roadmap"
```

- [ ] Merge the branch into `main`.
- [ ] Push `main` and the documentation branch if needed by local workflow.
