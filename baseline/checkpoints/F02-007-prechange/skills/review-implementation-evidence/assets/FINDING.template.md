---
workflow_contract: skill-team/v3
document_type: review-finding
finding_id: FND-<NNN>
classification: BLOCKING | HIGH | MEDIUM | LOW | QUESTION | OUT_OF_SCOPE
gap_type: missing | partial | contradicts | unrequested
requirement_ids: REQ-<NNN>[, REQ-<NNN> ...]
task_id: <TASK-ID>
evidence_path: <relative-path-to-reviewed-code-or-evidence>
return_owner: execute-routed-task | route-ai-work-by-capability | create-spec-driven-plan | investigate-existing-codebase | brainstorm-idea-with-user
status: OPEN | RESOLVED
---

# Finding <FND-NNN>

## Location

`path/file.ext:line` or artifact section.

## Traceability and evidence

- Gap type: `<missing | partial | contradicts | unrequested>`
- Requirement(s): `REQ-<NNN>`
- Task: `<TASK-ID>`
- Actual evidence: `<evidence_path>` — state the observed code, command result, or artifact fact.

## What is wrong

<Concrete description, not a general impression.>

## Why it matters

<Real impact: correctness, security, regression, contract, or scope.>

## Suggested resolution

<Concrete next step. Do not implement it here.>

## Routed to

`<execute-routed-task | route-ai-work-by-capability | create-spec-driven-plan | investigate-existing-codebase | brainstorm-idea-with-user>`
