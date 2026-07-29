---
workflow_contract: skill-team/v3
document_type: release-readiness-decision
project_id: <PROJECT_ID>
project_slug: <project-slug>
release_revision: <INT>
review_revision_consumed: <INT>
workflow_profile: compact | standard | critical
decision: RELEASE_READY | RELEASE_BLOCKED
updated_at: <ISO-8601>
---

# Release Readiness Decision

## Identification

- Project: `<PROJECT_ID>` / `<project-slug>`
- Workflow profile: `<compact | standard | critical>`
- Source handoff: `../handoffs/REVIEW-TO-RELEASE.md` (or `IMPLEMENTATION-TO-REVIEW.md` if review waived)

## Gate evaluation

| Gate | Result | Evidence |
|---|---|---|
| Implementation and review | PASS \| FAIL \| ACCEPTED_RISK | <citation> |
| Tests | PASS \| FAIL \| ACCEPTED_RISK | <citation> |
| Security and privacy | PASS \| FAIL \| ACCEPTED_RISK | <citation> |
| Migration and rollback | PASS \| FAIL \| ACCEPTED_RISK \| N/A | <citation> |
| Observability | PASS \| FAIL \| ACCEPTED_RISK | <citation> |
| Operational documentation | PASS \| FAIL \| ACCEPTED_RISK | <citation> |

## Accepted risk register

| ID | Gate | Rationale | Owner | Expiration or review condition | Non-waivable gate confirmed |
|---|---|---|---|---|---|
| RISK-001 | <gate> | <rationale> | <owner> | <date or measurable review condition> | YES \| N/A |

## Blockers

State `None.` for `RELEASE_READY`. Otherwise:

| Gate | Why it fails | Resolved by |
|---|---|---|
| <gate> | <reason, cite evidence> | <upstream skill or human decision> |

## Decision

`<RELEASE_READY | RELEASE_BLOCKED>` — <one-line rationale>

## Next required skill

`<NONE (human deploys) | execute-routed-task | review-implementation-evidence | create-spec-driven-plan>`
