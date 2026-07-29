---
workflow_contract: skill-team/v3
project_id: obs-status-test
project_slug: obs-status-test
workflow_profile: standard
stage: BRAINSTORM
status: BRAINSTORM_READY
stage_owner: brainstorm-idea-with-user
required_skill: create-spec-driven-plan
successor_skill: create-spec-driven-plan
handoff_status: READY
discovery_revision: 1
plan_revision: 0
routing_revision: 0
implementation_revision: 0
review_revision: 0
release_revision: 0
active_artifact: docs/ai/obs-status-test/discovery/brainstorm/BRAINSTORM.md
active_task: null
active_batch: null
active_executor_model: null
active_reviewer_model: null
writer_skill: null
writer_task: null
next_action: Attempt planning from BRAINSTORM_READY
blockers: NONE
last_validation_command: NONE
last_validation_result: NOT_RUN
updated_at: 2026-07-29T00:00:00Z
---
# Obsolete Status Acceptance

This fixture uses:
- `stage: BRAINSTORM` (should be `DISCOVERY`)
- `status: BRAINSTORM_READY` (should be `DISCOVERY_READY`; DEC-006 says remove BRAINSTORM_READY)

A strict v3 validator must reject both.
