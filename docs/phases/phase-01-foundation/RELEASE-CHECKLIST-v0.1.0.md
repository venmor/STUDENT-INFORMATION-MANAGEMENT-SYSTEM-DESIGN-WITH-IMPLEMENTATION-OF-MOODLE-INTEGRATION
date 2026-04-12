# Phase 1 Release Checklist `v0.1.0`

## Purpose

Use this checklist before creating the `v0.1.0` tag for the documentation baseline.

## Scope Check

- [ ] Repository purpose and current status are clear in `README.md`
- [ ] Documentation entry points are clear in `docs/README.md`
- [ ] Phase 1 deliverables are frozen in `docs/phases/phase-01-foundation/README.md`
- [ ] Phase 1 changes are recorded in `docs/phases/phase-01-foundation/CHANGELOG.md`
- [ ] Repository-wide changes are recorded in `CHANGELOG.md`

## Baseline Artifact Check

- [ ] `docs/project/modern-sis-problem-statement-and-vision.md` is present and aligned
- [ ] `docs/project/SRS_Modern_SIS.md` is present and aligned
- [ ] `docs/project/modern-sis-setup-guide.md` is normalized to the chosen stack baseline
- [ ] `docs/architecture/ADR-001-technology-baseline.md` is present
- [ ] `docs/architecture/technology-stack.md` is present
- [ ] `docs/architecture/architecture-diagrams.md` is present
- [ ] `docs/diagrams/modern-sis-erd.md` is present
- [ ] `docs/api/openapi.yaml` is present

## Structure Check

- [ ] Rendered SVG diagram exports are grouped under `docs/diagrams/rendered/mermaid-svg/`
- [ ] Figma/FigJam PNG exports are grouped under `docs/diagrams/rendered/figma-png/`
- [ ] FigJam manifest and links are grouped under `docs/diagrams/rendered/figjam-links/`
- [ ] Historical `.docx` files are archived under `docs/archive/source-docx/`
- [ ] Legacy static architecture SVG is stored under `docs/diagrams/legacy/`

## Version Control Check

- [ ] `git status` is understood before commit
- [ ] Only intended Phase 1 baseline files are staged
- [ ] Commit message is clear and scoped
- [ ] Annotated tag `v0.1.0` is created after the commit
- [ ] Tag message describes the documentation baseline release

## Suggested Commands

```bash
git status --short
git add README.md CHANGELOG.md docs/
git commit -m "docs: freeze phase-1 baseline and add implementation plan"
git tag -a v0.1.0 -m "Documentation baseline for Modern SIS Phase 1"
git show --stat v0.1.0
```
