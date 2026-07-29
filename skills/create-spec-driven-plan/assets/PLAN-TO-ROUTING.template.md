---
workflow_contract: skill-team/v3
handoff_type: plan-to-routing
project_id: <PROJECT_ID>
producer_skill: create-spec-driven-plan
consumer_skill: route-ai-work-by-capability
input_revision: <DISCOVERY_REVISION>
output_revision: <PLAN_REVISION>
handoff_status: NOT_READY
validation_command: python skills/create-spec-driven-plan/scripts/validate_plan.py docs/ai/<PROJECT_SLUG>
validation_result: NOT_RUN
generated_at: <ISO_8601_TIMESTAMP>
---

# Plan to routing handoff

## Identification
- Plan revision: <PLAN_REVISION>
- Discovery revision used: <DISCOVERY_REVISION>

## Summary
<PLAN_SUMMARY>

## Artifact inventory
- `plan/00-MASTER.md`
- `plan/TRACEABILITY.md`

## Preserved decisions
- <DECISION_OR_NONE>

## Allowed open questions
- NONE

## Blockers
- NONE

## Consumer write scope
- `routing/`

## Forbidden files
- `plan/`

## Commands and results
| Command | Result |
|---|---|
| `<VALIDATION_COMMAND>` | NOT_RUN |

## Stop instruction
Invoke `route-ai-work-by-capability` separately. It must not change plan semantics.
