---
workflow_contract: skill-team/v3
handoff_type: implementation-to-review
project_id: <PROJECT_ID>
producer_skill: execute-routed-task
consumer_skill: review-implementation-evidence
input_revision: <ROUTING_REVISION>
output_revision: <IMPLEMENTATION_REVISION>
handoff_status: NOT_READY
validation_command: python skills/execute-routed-task/scripts/validate_execution.py docs/ai/<project-slug>
validation_result: NOT_RUN
generated_at: <ISO-8601>
---

# Handoff — Implementation to Review

## Identification

- Project: `<PROJECT_ID>` / `<project-slug>`
- Implementation revision: `<INT>`
- Routing revision consumed: `<INT>`
- Evidence: `../execution/EVIDENCE.md`
- History: `../execution/HISTORY.md`

## Summary

<Which tasks/batch were executed, executor models used, overall outcome.>

## Artifact inventory

- `execution/EVIDENCE.md`
- `execution/HISTORY.md`
- `blockers/*.md` (if any remain open)

## Preserved decisions

<Any in-scope decisions the executor made within contract, with task IDs.>

## Allowed open questions

<Non-blocking questions the reviewer may resolve without reopening planning or routing.>

## Blockers

<State `None.` or list unresolved `blockers/<TASK-ID>.md` entries requiring reviewer or later-stage
attention.>

## Consumer write scope

`review-implementation-evidence` may create/update `review/*`, `findings/*`, and this stage's outgoing
handoff. It must not edit `execution/*` or implementation source files.

## Forbidden files

- `execution/EVIDENCE.md`
- `execution/HISTORY.md`

## Commands and results

| Command | Result |
|---|---|
| `<test/build/lint command>` | PASS \| FAIL |
| `python skills/execute-routed-task/scripts/validate_execution.py docs/ai/<project-slug>` | PASS \| FAIL |

## Stop instruction

`review-implementation-evidence` independently verifies this work; it does not implement fixes
itself. If review is waived for this batch per routing, `validate-release-readiness` may consume this
handoff directly instead.
