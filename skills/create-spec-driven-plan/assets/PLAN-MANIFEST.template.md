---
workflow_contract: skill-team/v3
project_id: <project-id>
project_slug: <project-slug>
workflow_profile: compact
plan_revision: 1
---

# Plan manifest

## Profile

`compact` | `standard` | `critical`

## Included documents

| Document | Required by profile | Present |
|---|---|---|
| `plan/00-MASTER.md` | all | yes |
| `plan/TRACEABILITY.md` | all | yes |
| `plan/phases/*.md` | all | yes |
| `plan/ANALYSIS.md` | standard+ | no |
| `plan/SECURITY.md` | standard+ | no |
| `plan/THREAT-MODEL.md` | critical | no |
| `plan/MIGRATION.md` | critical | no |
| `plan/ROLLBACK.md` | critical | no |

## Notes

- Compact omits irrelevant documents; it never weakens security gates for in-scope work.
- Critical requires every applicable control document listed above.
