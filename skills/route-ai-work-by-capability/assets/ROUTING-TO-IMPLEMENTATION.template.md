---
workflow_contract: skill-team/v3
document_type: routing-to-implementation-handoff
plan_revision: <PLAN_REVISION>
routing_revision: <ROUTING_REVISION>
routing_based_on_plan_revision: <PLAN_REVISION>
producer_skill: route-ai-work-by-capability
consumer: implementation
handoff_status: NOT_READY
generated_at: <ISO-8601>
---

# Handoff — Routing to implementation

## Identification

- Plan revision: <PLAN_REVISION>
- Routing revision: <ROUTING_REVISION>
- Routing document: `../plan/ROUTING.md`
- Model registry: `../MODEL-CAPABILITIES.md`

## Registered models

| Model ID | Tier | Review policy |
|---|---|---|
| <MODEL-ID> | <TIER> | <policy> |

## Initial execution

- Initial global task: <TASK-ID>
- Initial executor: <MODEL-ID>
- Next task for <MODEL-ID>: <TASK-ID-or-NONE>
- First switch: <checkpoint description>

## Gate status

- Plan validation: VALID | INVALID
- Dependency graph: VALID | INVALID
- Traceability: VALID | INVALID
- Routing validation: VALID | INVALID
- File locks: VALID | INVALID

## Required reading

1. `../PROGRESS.md`
2. `../plan/ROUTING.md`
3. task context and referenced contracts
4. `../MODEL-CAPABILITIES.md`

## Validation commands

| Command | Result |
|---|---|
| `<command>` | PASS | FAIL |

## Escalation

Stop on missing/contradictory contract, schema change, security ambiguity, concurrency issue, critical oracle failure or scope expansion. Record the reason and request the appropriate workflow stage.

## Start protocol

1. Confirm `PROGRESS.md` status is `IMPLEMENTATION_READY`.
2. Confirm plan/routing revisions equal this handoff.
3. Load the initial task's required context.
4. Mark only that task `IN_PROGRESS`.
5. Execute its smallest verified batch.

## Continue protocol

1. Resume the compatible `IN_PROGRESS` task.
2. Otherwise choose the first dependency-ready task assigned to the active model.
3. Never take another model's task.
4. Record evidence before completion.
5. Use a model-switch checkpoint before changing models.

## Scope-change protocol

- Small/local: update task and traceability; increment plan revision and reroute if affected.
- Structural: `REPLAN_REQUIRED` and `required_skill: create-spec-driven-plan`.
- Product intent: `REBRAINSTORM_REQUIRED` and `required_skill: brainstorm-idea-with-user`.

## Handoff authorization

Set `handoff_status: READY` only when every gate above is valid and `PROGRESS.md` has been updated to `IMPLEMENTATION_READY`.
