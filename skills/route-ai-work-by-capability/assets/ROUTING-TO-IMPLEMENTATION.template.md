---
workflow_contract: skill-team/v3
handoff_type: routing-to-implementation
project_id: <PROJECT_ID>
producer_skill: route-ai-work-by-capability
consumer_skill: execute-routed-task
input_revision: <PLAN_REVISION>
output_revision: <ROUTING_REVISION>
handoff_status: NOT_READY
validation_command: python skills/route-ai-work-by-capability/scripts/validate_routing.py docs/ai/<PROJECT_SLUG>
validation_result: NOT_RUN
generated_at: <ISO_8601_TIMESTAMP>
---

# Routing to implementation handoff

## Identification
- Routing revision: <ROUTING_REVISION>

## Summary
<ASSIGNMENT_AND_REVIEW_POLICY_SUMMARY>

## Artifact inventory
- `routing/ROUTING.md`
- `routing/MODEL-CAPABILITIES.md`

## Preserved decisions
- <ROUTING_DECISION_OR_NONE>

## Allowed open questions
- NONE

## Blockers
- NONE

## Consumer write scope
- <TASK_DECLARED_WRITE_SCOPE>

## Forbidden files
- `plan/`
- `routing/`

## Commands and results
| Command | Result |
|---|---|
| `<VALIDATION_COMMAND>` | NOT_RUN |

## Stop instruction
Invoke `execute-routed-task` separately for one dependency-ready task.
