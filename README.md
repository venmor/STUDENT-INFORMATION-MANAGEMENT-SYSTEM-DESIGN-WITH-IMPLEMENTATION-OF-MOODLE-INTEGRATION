# Modern Student Information System

Modern SIS is a proposed institutional platform that keeps the Student Information System as the authoritative academic and administrative record, integrates Moodle as the learning environment, and adds governed AI features for support and decision assistance.

The purpose of the project is to reduce operational fragmentation across student records, course administration, Moodle activity, advising, and support workflows. The intended outcome is earlier intervention, less manual reconciliation, better student visibility, and stronger institutional auditability.

## Current Status

This repository is currently a pre-implementation design baseline. It contains requirements, architecture, diagrams, and setup guidance. It does not yet contain the application codebase.

## What The System Is Intended To Do

- manage student records, courses, enrollments, grades, attendance, and advising context
- provision users, sections, enrollments, and official grades into Moodle
- embed selected SIS workflows inside Moodle using LTI v1.3
- provide AI-assisted co-pilot, summarisation, at-risk insights, and approval-gated wellbeing support
- enforce audit logging, role boundaries, and privacy controls throughout

## Approved Baseline

- Backend: `Python 3.11+`, `Django 5`, `Django REST Framework`
- Frontend: `React 18`, `TypeScript`, `Vite`
- Primary database: `MySQL 8.0`
- Background jobs: `Celery + Redis`
- Moodle integration: `Moodle REST API + PyLTI1p3`
- Vector store: `Qdrant`
- AI provider model: `OpenAI-compatible gateway`
- Deployment: `Docker Compose` on a Linux host for development, staging, and demonstration

## Recommended Reading Order

1. [Docs Index](docs/README.md)
2. [Problem Statement And Vision](docs/project/modern-sis-problem-statement-and-vision.md)
3. [Software Requirements Specification (SRS)](docs/project/SRS_Modern_SIS.md)
4. [Phase 1 Foundation](docs/phases/phase-01-foundation/README.md)
5. [ADR-001 Technology Baseline](docs/architecture/ADR-001-technology-baseline.md)
6. [Technology Stack](docs/architecture/technology-stack.md)
7. [Architecture Diagrams](docs/architecture/architecture-diagrams.md)
8. [ERD Draft](docs/diagrams/modern-sis-erd.md)
9. [OpenAPI Starter](docs/api/openapi.yaml)
10. [Setup Guide](docs/project/modern-sis-setup-guide.md)
11. [Version Control Guidance](docs/process/version-control.md)
12. [Pre-Implementation Design Summary](docs/superpowers/specs/2026-04-11-modern-sis-preimplementation-design.md)

## Repository Index

| Path | Role | Status |
|---|---|---|
| `docs/project/modern-sis-problem-statement-and-vision.md` | Strategic purpose, problem, and product vision | Authoritative |
| `docs/project/SRS_Modern_SIS.md` | Functional and non-functional requirements baseline | Authoritative |
| `docs/phases/phase-01-foundation/README.md` | Active phase entry point for the documentation baseline | Active |
| `docs/phases/phase-01-foundation/CHANGELOG.md` | Phase 1 scoped change history | Active |
| `docs/architecture/ADR-001-technology-baseline.md` | Locks the stack and phased delivery decisions | Authoritative |
| `docs/architecture/technology-stack.md` | Explains the selected stack, database split, and deployment rationale | Authoritative |
| `docs/architecture/architecture-diagrams.md` | Renderable Mermaid architecture and workflow diagrams | Authoritative |
| `docs/diagrams/README.md` | Diagram asset index and rendered-output layout | Maintained |
| `docs/diagrams/modern-sis-erd.md` | Domain model and ERD baseline | Authoritative |
| `docs/api/openapi.yaml` | Initial API contract surface | Authoritative draft |
| `docs/project/modern-sis-setup-guide.md` | Implementation order and build sequence guidance | Maintained |
| `docs/process/version-control.md` | Branching, commit, tagging, and changelog guidance | Maintained |
| `CHANGELOG.md` | Repository-wide change log | Maintained |
| `docs/superpowers/specs/2026-04-11-modern-sis-preimplementation-design.md` | Summary of the approved baseline decisions | Maintained |
| `docs/diagrams/legacy/modern-sis-system-architecture.svg` | Static architecture illustration created before the Mermaid pack | Reference |
| `docs/archive/source-docx/Modern_SIS_Purpose_and_Problems.docx` | Original source Word document for early vision work | Historical source |
| `docs/archive/source-docx/Modern_SIS_Setup_Guide.docx` | Original source Word document for setup guidance | Historical source |

## Delivery Phases

- Phase 1: Core SIS, authentication, RBAC, audit logging, Moodle Lane A provisioning
- Phase 2: Moodle Lane B embedded tools, student co-pilot, staff summarisation
- Phase 3: At-risk engine
- Phase 4: Wellbeing support after institutional policy and safeguarding approval

## Architecture Notes

- The SIS is the administrative source of truth.
- Moodle remains the learning platform, not the administrative system.
- Lane A is event-driven SIS to Moodle provisioning and grade pass-back.
- Lane B is Moodle-to-SIS launch via LTI v1.3 for embedded tools.
- Moodle engagement data is ingested on a schedule for analytics and at-risk processing.
- Wellbeing data is isolated from general AI audit logs and requires stricter access controls.

## Historical Source Material

The archived Word documents under [docs/archive/source-docx](docs/archive/source-docx) are kept as historical source material. The maintained Markdown files in `docs/` are the versions that should be reviewed and evolved going forward.
