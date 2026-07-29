---
workflow_contract: skill-team/v3
handoff_type: brainstorm-to-plan
project_id: <PROJECT_ID>
producer_skill: brainstorm-idea-with-user
consumer_skill: create-spec-driven-plan
input_revision: <DISCOVERY_REVISION>
output_revision: <DISCOVERY_REVISION>
handoff_status: NOT_READY
validation_command: python skills/brainstorm-idea-with-user/scripts/validate_brainstorm.py docs/ai/<PROJECT_SLUG>
validation_result: NOT_RUN
generated_at: <ISO_8601_TIMESTAMP>
---

# Brainstorm to plan handoff

## Identification
- Discovery revision: <DISCOVERY_REVISION>

## Summary
<VALIDATED_DISCOVERY_SUMMARY>

## Artifact inventory
- `discovery/brainstorm/BRAINSTORM.md`

## Preserved decisions
- <DECISION_OR_NONE>

## Allowed open questions
- <NON_STRUCTURAL_QUESTION_OR_NONE>

## Blockers
- NONE

## Consumer write scope
- `plan/`

## Forbidden files
- `discovery/brainstorm/`

## Commands and results
| Command | Result |
|---|---|
| `<VALIDATION_COMMAND>` | NOT_RUN |

## Stop instruction
Invoke `create-spec-driven-plan` separately. Do not implement.
