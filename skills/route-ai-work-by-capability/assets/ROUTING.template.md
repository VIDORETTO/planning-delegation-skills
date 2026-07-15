---
workflow_contract: planning-delegation/v2
document_type: routing
plan_revision: <PLAN_REVISION>
routing_revision: <ROUTING_REVISION>
routing_based_on_plan_revision: <PLAN_REVISION>
status: VALIDATION_PENDING
updated_at: <ISO-8601>
---

# Model routing

## Validation basis

- Plan handoff: `../handoffs/PLAN-TO-ROUTING.md`
- Model registry: `../MODEL-CAPABILITIES.md`
- Dependency graph: VALID | INVALID
- Plan revision consumed: <PLAN_REVISION>

## Rules

1. Every plan task appears exactly once.
2. Every executor and reviewer is registered.
3. Hard gates require a STRONG executor.
4. Dependencies control task and batch readiness.
5. A reviewer is not a task owner.
6. Concurrent batches cannot share write locks.
7. Mixed tasks return to planning unless the validated plan authorizes a split.

## Assignments

| Task | Executor | Tier | Hard gate | Score | Confidence | Reviewer | Review mode | Batch | Risk | Reversibility | Verification | Blast radius | Spec completeness | Rework cost | Files/Components | Locks | Rationale |
|---|---|---|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <TASK-ID> | <MODEL-ID> | <TIER> | NONE | <0-24> | HIGH | NONE | NONE | <BATCH-ID> | LOW | HIGH | EASY | SMALL | COMPLETE | LOW | `<path>` | `<lock-or-NONE>` | <reason> |

## Scores

Every task without a hard gate must have all dimensions scored 0–3.

| Task | Ambiguity | Coupling | Irreversibility | State/concurrency | Data correctness | Verification difficulty | External variability | Specification incompleteness | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| <TASK-ID> | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Batches

### Batch <TIER>-B01

- Executor: <MODEL-ID>
- Entry dependencies: NONE
- Tasks: <TASK-ID>
- Shared context: `<path-or-section>`
- Files: `<path>`
- Locks: `<lock-or-NONE>`
- Execution: SEQUENTIAL | PARALLEL
- Validation command: `<command>`
- Stop condition: <condition>
- Next switch: <MODEL-ID and task>

## Current readiness

- Initial global task: <TASK-ID>
- Initial global executor: <MODEL-ID>
- Next task for <MODEL-ID>: <TASK-ID-or-NONE>
- First switch: <MODEL-ID> to <MODEL-ID> before <TASK-ID>
- Blocking dependency: <TASK-ID-or-NONE>

## Review policy

- `NONE`: no separate reviewer.
- `SAMPLE`: post-completion sample.
- `REQUIRED_BEFORE_COMPLETE`: review blocks task completion.
- `REQUIRED_BEFORE_RELEASE`: review blocks release, not task completion.
- `ADVERSARIAL_REVIEW`: independent hostile/negative-path review.

## Update rule

Any plan change invalidates routing until revisions and assignments are synchronized and validation passes again.
