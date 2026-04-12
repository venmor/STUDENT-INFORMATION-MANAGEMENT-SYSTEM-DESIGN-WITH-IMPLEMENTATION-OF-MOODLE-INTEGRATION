# Diagrams Index

This directory contains both diagram source material and rendered outputs for the Modern SIS baseline.

## Source Of Truth

- [Architecture Diagrams](../architecture/architecture-diagrams.md): Mermaid source for use case, context, component, sequence, activity, state, and deployment diagrams.
- [ERD Draft](modern-sis-erd.md): Mermaid ERD and domain model baseline.

## Rendered Outputs

| Path | Contents |
|---|---|
| `rendered/mermaid-svg/` | SVG exports of the Mermaid architecture diagrams |
| `rendered/figma-png/` | PNG exports generated from the editable FigJam/Figma diagrams |
| `rendered/figjam-links/` | Manifest and editable links for the FigJam diagram sources |
| `legacy/` | Earlier static diagram artifacts kept for reference |

## Notes

- The Mermaid Markdown files are the editable source of truth for architecture diagrams in this repo.
- Rendered assets are useful for quick viewing and presentations, but they should be regenerated from the Markdown source if the architecture changes.
- Legacy diagrams should not be updated unless there is a specific reason to preserve historical visual context.
