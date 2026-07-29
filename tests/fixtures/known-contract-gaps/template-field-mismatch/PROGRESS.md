---
workflow_contract: skill-team/v3
project_id: tmpl-mismatch-test
project_slug: tmpl-mismatch-test
stage: PLAN
status: PLAN_IN_PROGRESS
stage_owner: create-spec-driven-plan
required_skill: create-spec-driven-plan
handoff_status: NOT_READY
brainstorm_revision: 1
plan_revision: 0
routing_revision: 0
plan_based_on_brainstorm_revision: null
routing_based_on_plan_revision: null
active_artifact: docs/ai/tmpl-mismatch-test/plan/00-MASTER.md
current_task: null
next_action: Formalizar requisitos candidatos e contratos
blockers: []
last_validation:
  command: null
  result: NOT_RUN
updated_at: 2026-07-29T00:00:00Z
---
# Template Field Mismatch

This fixture mirrors the planning PROGRESS template fields which use:
- `stage: PLAN` (should be `PLANNING`)
- `brainstorm_revision` (should be `discovery_revision`)
- `current_task` (should be `active_task`)
- `blockers: []` (should be `blockers: NONE`)
- Nested `last_validation` (should be flat `last_validation_command`/`last_validation_result`)
- `plan_based_on_brainstorm_revision` (obsolete field)
- `routing_based_on_plan_revision` (obsolete field)

A strict v3 validator must reject.
