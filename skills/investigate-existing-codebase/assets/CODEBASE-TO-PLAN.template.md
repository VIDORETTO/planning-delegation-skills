---
workflow_contract: skill-team/v3
handoff_type: codebase-to-plan
project_id: <id>
producer_skill: investigate-existing-codebase
consumer_skill: create-spec-driven-plan
input_revision: 1
output_revision: 1
handoff_status: READY
validation_command: python skills/investigate-existing-codebase/scripts/validate_investigation.py docs/ai/<slug>
validation_result: PASS
generated_at: <ISO-8601>
---

# Codebase to plan handoff

## Summary
<summary>

## Artifact inventory
- discovery/codebase/INVESTIGATION.md
- discovery/codebase/EVIDENCE.md

## Preserved decisions
- NONE

## Open questions allowed in planning
- <minor>

## Blockers
- NONE

## Consumer write scope
- plan/

## Forbidden files
- discovery/codebase/ except consumption metadata

## Stop instruction
Invoke create-spec-driven-plan separately. Do not implement.
