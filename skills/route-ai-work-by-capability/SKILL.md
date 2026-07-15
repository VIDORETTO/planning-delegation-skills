---
name: route-ai-work-by-capability
description: Route tasks from a validated spec-driven plan to registered AI models by capability, risk and total delivery cost. Produces auditable assignments, reviewers, batches, model-switch checkpoints and a validated implementation handoff. Use only after create-spec-driven-plan has produced PLAN_VALIDATED.
---

# Route AI Work by Capability

Route validated implementation tasks to the least expensive model that can deliver them with acceptable expected risk. This skill owns only the routing stage of `planning-delegation/v2`.

## Required resources

Before routing:

1. read [references/classification-rubric.md](references/classification-rubric.md);
2. use [assets/ROUTING.template.md](assets/ROUTING.template.md);
3. use [assets/MODEL-CAPABILITIES.template.md](assets/MODEL-CAPABILITIES.template.md);
4. use [assets/MODEL-SWITCH-CHECKPOINT.template.md](assets/MODEL-SWITCH-CHECKPOINT.template.md);
5. use [assets/ROUTING-TO-IMPLEMENTATION.template.md](assets/ROUTING-TO-IMPLEMENTATION.template.md);
6. adapt [assets/AGENTS.template.md](assets/AGENTS.template.md) only as a discovery index;
7. run [scripts/validate_routing.py](scripts/validate_routing.py).

## Exclusive stage ownership

Execute only routing. Do not invoke, execute or mix planning, brainstorm or implementation in the same operation.

When finished:

1. validate routing artifacts;
2. generate `handoffs/ROUTING-TO-IMPLEMENTATION.md`;
3. update `PROGRESS.md`;
4. set `next_skill: implementation`;
5. stop.

If the current state belongs to another skill, do not modify its artifacts. Report the required skill and stop.

## Input gate

Start only when all conditions are true in the project workflow directory:

~~~yaml
workflow_contract: planning-delegation/v2
stage: PLAN
status: PLAN_VALIDATED
active_skill: create-spec-driven-plan
next_skill: route-ai-work-by-capability
handoff_status: READY
~~~

Additionally require:

- `handoffs/PLAN-TO-ROUTING.md` exists;
- `plan/00-MASTER.md`, phase/task specifications and `plan/TRACEABILITY.md` exist;
- handoff `plan_revision` equals `PROGRESS.md` `plan_revision`;
- handoff `brainstorm_revision` equals `plan_based_on_brainstorm_revision`;
- the dependency graph and plan validation result are valid;
- every routable task has a stable ID, objective, dependencies, bounded write scope, tests, non-empty acceptance criteria and evidence contract;
- no hidden architecture, schema or contract decision remains inside a mechanical task.

If the plan is incomplete, do not repair requirements, architecture, contracts or task definitions and do not generate routing. Update only the workflow pointer:

~~~yaml
stage: PLAN
status: REPLAN_REQUIRED
active_skill: route-ai-work-by-capability
next_skill: create-spec-driven-plan
handoff_status: NOT_READY
~~~

Record precise validation failures and stop.

## Workflow

### 1. Register models

Create `MODEL-CAPABILITIES.md`. Use stable model IDs and record real name/version, tier, assessment date, context, tools, vision/navigation capabilities, strengths, limitations, code and architecture quality, relative cost and review policy.

Model capabilities are time-sensitive. Never route from brand prestige or an undated assumption. User-provided names remain visible, but task fields use registered Model IDs.

### 2. Classify tasks

Apply hard gates first. Architecture/public API, auth/security/privacy/tenancy, destructive migration, concurrency/idempotency/distributed state, critical financial/legal rules, ambiguous inference/parsing, durable workflows, production promotion and incident recovery require STRONG.

When no gate applies, score every rubric dimension. Record total, confidence and rationale. Include risk, reversibility, verification difficulty, blast radius, specification completeness and rework cost.

Split mixed tasks only if the validated plan already authorizes the split. Otherwise return `REPLAN_REQUIRED`; routing must not silently create requirements, tasks or contracts.

### 3. Assign executor and reviewer

Every task has exactly one executor. A reviewer is not a co-owner.

Allowed review modes:

- `NONE`;
- `SAMPLE`;
- `REQUIRED_BEFORE_COMPLETE`;
- `REQUIRED_BEFORE_RELEASE`;
- `ADVERSARIAL_REVIEW`.

Use a registered STRONG reviewer when risk, verification difficulty or policy requires it. Executor and reviewer must differ whenever review is required.

### 4. Build dependency-aware batches

Group compatible ready tasks to reduce model switching. Each batch records executor, entry dependencies, tasks, shared context, files, locks, validation command, stop condition and next switch.

Preserve the plan graph. A batch may contain only tasks whose internal order and external dependencies are explicit. Never place concurrent tasks in batches that write the same locked file or component.

Compute:

- first globally ready task;
- next ready task per model;
- first model switch;
- blocking dependency where a queue is empty.

### 5. Install switch checkpoints

Every model change uses the mandatory checkpoint template. Record revisions, task state, changed files, diff, commands, passing/failing tests, decisions, contract changes, remaining risk, exact next command and required reading.

Never transfer an in-progress task between executors. Reassignment requires a recorded plan/routing change or an authorized task split.

### 6. Keep AGENTS.md as an index

The root `AGENTS.md` contains discovery instructions only:

1. read `PROGRESS.md`;
2. read its `active_artifact`;
3. read the current handoff;
4. read task-referenced contracts.

`PROGRESS.md` is the only operational pointer. Do not duplicate current status, queue state, active executor or task assignment in `AGENTS.md`.

### 7. Create implementation handoff

Create `handoffs/ROUTING-TO-IMPLEMENTATION.md` with plan/routing revisions, model registry, initial tasks, first switch, escalation, required reading, validation commands/results, gate state and protocols for `start`, `continue` and scope change.

### 8. Validate and transition

Run:

~~~text
python skills/route-ai-work-by-capability/scripts/validate_routing.py docs/ai/<project-slug>
~~~

On success increment `routing_revision`, preserve `routing_based_on_plan_revision`, and set:

~~~yaml
stage: ROUTING
status: IMPLEMENTATION_READY
active_skill: route-ai-work-by-capability
next_skill: implementation
handoff_status: READY
active_artifact: docs/ai/<project-slug>/handoffs/ROUTING-TO-IMPLEMENTATION.md
~~~

Do not start implementation. Stop after reporting artifacts, counts, initial ready task/executor, first switch and validation result.

## Escalation and change control

An implementer must stop when it finds a missing/contradictory contract, schema decision, security ambiguity, concurrency issue, critical oracle failure or scope expansion.

- Small change: update task and traceability, increment `plan_revision`, and update routing revision if affected.
- Structural change: set `REPLAN_REQUIRED`, `next_skill: create-spec-driven-plan`.
- Product-intent change: set `REBRAINSTORM_REQUIRED`, `next_skill: brainstorm-idea-with-user`.

The implementer records the reason but does not silently choose or execute another stage.

## Output contract

Produce only:

- `plan/ROUTING.md`;
- `MODEL-CAPABILITIES.md`;
- model-switch checkpoint template/reference;
- `handoffs/ROUTING-TO-IMPLEMENTATION.md`;
- routing fields in existing task specs where authorized;
- the minimal `AGENTS.md` discovery index;
- the routing transition in `PROGRESS.md`.

Do not claim readiness unless validation succeeds.
