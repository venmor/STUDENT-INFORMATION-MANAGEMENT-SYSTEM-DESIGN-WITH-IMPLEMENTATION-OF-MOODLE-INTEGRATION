# Version Control And Change Management

This document defines the minimum version-control discipline for the Modern SIS project as it moves from Phase 1 documentation work into implementation.

## Branching

- `main` is the protected baseline branch.
- Use short-lived feature branches for active work.
- Recommended naming:
  - `docs/phase-01-<topic>`
  - `feat/phase-02-<topic>`
  - `fix/<topic>`
  - `chore/<topic>`

## Commit Conventions

Use clear, conventional commit prefixes:

- `docs:` documentation changes
- `feat:` new functionality
- `fix:` bug fixes
- `refactor:` structural code improvements without behavior changes
- `chore:` repo maintenance or non-feature cleanup
- `test:` test additions or updates

Examples:

- `docs: reorganize diagram assets and add phase-1 changelog`
- `feat: add student profile and advising note models`
- `fix: correct moodle enrollment retry behavior`

## Change Logs

- Update the repository root [CHANGELOG.md](../../CHANGELOG.md) for cross-phase or repo-wide changes.
- Update the active phase changelog for work scoped to that phase.
- If a change affects requirements, update the document version or revision history in the affected file as well.

## Tags And Versions

- Use semantic-style project tags once code implementation starts.
- Recommended early tags:
  - `v0.1.0` for the documentation baseline
  - `v0.2.0` after Phase 2 implementation planning is complete
  - `v0.3.0` after the first working Phase 2 implementation slice

## Pull Request Expectations

- One focused concern per PR where practical.
- Link the PR to the relevant phase and document path.
- Include:
  - scope summary
  - files changed
  - verification performed
  - any follow-up work deferred

## Document Versioning

- `SRS_Modern_SIS.md` should use explicit version numbers and revision history.
- ADRs should remain append-only in intent. Update status or add a new ADR rather than silently rewriting decision history.
- Phase documents should record notable structural changes in `CHANGELOG.md`.

## Phase Discipline

- Do not start a new phase without a readable README and changelog for that phase.
- If a change crosses phase boundaries, document it in both the current phase changelog and the root changelog.
