# Handoff — Plan to routing

## Identification

- Workflow contract: `planning-delegation/v2`
- Plan revision: <INTEGER>
- Brainstorm revision used: <INTEGER>
- Generated at: <ISO_8601_TIMESTAMP>
- Producer skill: `create-spec-driven-plan`
- Consumer skill: `route-ai-work-by-capability`

## Plan inventory

- Requirements: <COUNT>
- Phases: <COUNT>
- Tasks: <COUNT>
- Unassigned tasks: <TASK_IDS>
- Tasks with hard gates: <TASK_IDS_OR_NONE>
- Potentially mixed tasks: <TASK_IDS_OR_NONE>

## Dependency graph

- Result: VALID
- Command: `<VALIDATION_COMMAND>`

## Open matters

- Open questions: <IDS_OR_NONE>
- Defaults adopted: <DEC_IDS_OR_NONE>
- Blocking matters: none

## Validation

- Command: `python skills/create-spec-driven-plan/scripts/validate_plan.py docs/ai/<SLUG>`
- Result: VALID

## Routing write scope

- `plan/ROUTING.md`
- `MODEL-CAPABILITIES.md`
- `handoffs/ROUTING-TO-IMPLEMENTATION.md`
- routing fields in `PROGRESS.md`
- Executor, Reviewer and review metadata in phase tasks

Routing must not alter requirements, architecture, contracts, dependencies or acceptance criteria. If those are incomplete, set `REPLAN_REQUIRED` and return to `create-spec-driven-plan`.
