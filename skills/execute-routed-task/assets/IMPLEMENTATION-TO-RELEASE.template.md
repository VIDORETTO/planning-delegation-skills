---
workflow_contract: skill-team/v3
handoff_type: implementation-to-release
project_id: <PROJECT_ID>
producer_skill: execute-routed-task
consumer_skill: validate-release-readiness
input_revision: <ROUTING_REVISION>
output_revision: <IMPLEMENTATION_REVISION>
handoff_status: NOT_READY
validation_command: python skills/execute-routed-task/scripts/validate_execution.py docs/ai/<PROJECT_SLUG>
validation_result: NOT_RUN
generated_at: <ISO_8601_TIMESTAMP>
---

# Implementation to release handoff

## Identification
- Implementation revision: <IMPLEMENTATION_REVISION>

## Summary
<COMPLETED_TASKS_AND_WAIVER_REASON>

## Artifact inventory
- `execution/EVIDENCE.md`
- `execution/HISTORY.md`

## Preserved decisions
- <DECISION_OR_NONE>

## Allowed open questions
- NONE

## Blockers
- NONE

## Consumer write scope
- `release/`

## Forbidden files
- `execution/`

## Commands and results
| Command | Result |
|---|---|
| `<VALIDATION_COMMAND>` | NOT_RUN |

## Stop instruction
Invoke `validate-release-readiness` separately. The routing waiver must be explicit.
