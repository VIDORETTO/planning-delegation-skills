---
workflow_contract: skill-team/v3
handoff_type: plan-to-routing
project_id: PRJ-009
producer_skill: create-spec-driven-plan
consumer_skill: route-ai-work-by-capability
input_revision: 1
output_revision: 1
handoff_status: READY
validation_command: python skills/create-spec-driven-plan/scripts/validate_plan.py docs/ai/compact-plan
validation_result: PASS
generated_at: 2026-07-27T12:00:00-03:00
---

# Plan to routing handoff

## Identification

- Plan revision: 1
- Discovery revision used: 1

## Summary

The compact plan defines one pending task to return a defined error for malformed payloads.

## Artifact inventory

- `plan/00-MASTER.md`
- `plan/SPEC.md`
- `plan/TRACEABILITY.md`
- `plan/CONSISTENCY-REPORT.md`

## Preserved decisions

- NONE

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
| `python skills/create-spec-driven-plan/scripts/validate_plan.py tests/fixtures/compact-plan` | PASS |

## Stop instruction

Invoke `route-ai-work-by-capability` separately. It must not change plan semantics.
