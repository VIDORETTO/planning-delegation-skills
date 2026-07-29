---
workflow_contract: skill-team/v3
handoff_type: routing-to-implementation
project_id: PRJ-009
producer_skill: route-ai-work-by-capability
consumer_skill: execute-routed-task
input_revision: 1
output_revision: 1
handoff_status: READY
validation_command: python skills/route-ai-work-by-capability/scripts/validate_routing.py docs/ai/compact-plan
validation_result: PASS
generated_at: 2026-07-27T12:00:00-03:00
---

# Routing to implementation handoff

## Identification

Routing revision 1 for F01-001.

## Summary

MODEL-STRONG executes F01-001 and MODEL-REVIEW independently reviews it.

## Artifact inventory

- `../routing/ROUTING.md`
- `../plan/TASKS.md`

## Preserved decisions

- F01-001 is dependency-ready and requires independent review.

## Allowed open questions

None.

## Blockers

None.

## Consumer write scope

Execute the routed task and record execution evidence.

## Forbidden files

- Routing assignments.

## Commands and results

`pytest -k parser`: PASS.

## Stop instruction

Acquire the executor writer lock for F01-001. Stop for an unplanned schema change and return material scope changes to planning.

## Registered models

MODEL-STRONG executes and MODEL-REVIEW independently reviews.

## Initial execution

F01-001 is dependency-ready.

## Gate status

Routing validation passed.

## Required reading

Read routing and the F01 task.

## Validation commands

Run `pytest -k parser`.

## Escalation

Stop for an unplanned schema change.

## Start protocol

Acquire the executor writer lock for F01-001.

## Continue protocol

Record evidence before handing work to review.

## Scope-change protocol

Return material scope changes to planning.
