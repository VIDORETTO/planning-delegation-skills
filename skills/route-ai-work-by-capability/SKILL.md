---
name: route-ai-work-by-capability
description: >
  Assign validated plan tasks to registered AI models and independent reviewers using required
  tools, capabilities, hard gates, risk, dependencies, verification difficulty, and total delivery
  cost. Use only after the plan is validated. Produce assignments, batches, locks, switch
  checkpoints, and an implementation handoff. Do not repair plan semantics or implement tasks.
---

# Route AI Work by Capability

Route validated implementation tasks to registered models by capability, tools, risk, and total
delivery cost. This skill owns only the routing stage of `skill-team/v3`.

## Required resources

1. [references/classification-rubric.md](references/classification-rubric.md)
2. [assets/ROUTING.template.md](assets/ROUTING.template.md)
3. [assets/MODEL-CAPABILITIES.template.md](assets/MODEL-CAPABILITIES.template.md)
4. [assets/MODEL-SWITCH-CHECKPOINT.template.md](assets/MODEL-SWITCH-CHECKPOINT.template.md)
5. [assets/ROUTING-TO-IMPLEMENTATION.template.md](assets/ROUTING-TO-IMPLEMENTATION.template.md)
6. [assets/AGENTS.template.md](assets/AGENTS.template.md) as discovery index only
7. [scripts/validate_routing.py](scripts/validate_routing.py)

## Exclusive stage ownership

Write only `routing/`, authorized task assignment fields, and routing fields in `PROGRESS.md`.
Do not repair incomplete plans and do not implement.

When finished:

1. validate routing;
2. generate `handoffs/ROUTING-TO-IMPLEMENTATION.md`;
3. update `PROGRESS.md` to `IMPLEMENTATION_READY`;
4. set `required_skill: execute-routed-task`;
5. stop.

Resume only when `required_skill` equals this skill.

## Input gate

Require `status: PLAN_VALIDATED`, `required_skill: route-ai-work-by-capability`, ready
`PLAN-TO-ROUTING.md`, synchronized `plan_revision`, valid dependency graph, and every routable
task with ID, objective, dependencies, write scope, tests, acceptance, and evidence contract.

If the plan is incomplete, set `REPLAN_REQUIRED` and `required_skill: create-spec-driven-plan`.
Do not invent requirements, tasks, or contracts.

## Workflow

### 1. Register models

Create `routing/MODEL-CAPABILITIES.md` with stable Model IDs. Record real name/version, assessment
date, tools, repo access, write, terminal, vision, navigation, context, code/architecture
capability, strengths, limitations, relative cost, autonomy, review policy, evidence, and
validity. Never hardcode brand prestige. Never route from undated assumptions.

Any number of models may be registered. Two-tier setups are a special case, not the rule.

### 2. Classify tasks

Apply hard gates first: architecture/public API, auth/security/privacy/tenancy, destructive
migration, concurrency/idempotency/distributed state, critical financial/legal/medical data,
ambiguous parsing/inference, durable workflows, production promotion, incident response, DR.

When no gate applies, score rubric dimensions. Record score, hard gate, confidence, evidence,
error cost, review cost, re-execution cost, and rationale. Thresholds are configurable defaults.

Split mixed tasks only if the plan already authorizes the split; otherwise `REPLAN_REQUIRED`.

### 3. Assign executor and reviewer

Exactly one executor per task. Reviewer is not a co-owner. Modes: `NONE`, `SAMPLE`,
`REQUIRED_BEFORE_COMPLETE`, `REQUIRED_BEFORE_RELEASE`, `ADVERSARIAL_REVIEW`. Executor and
reviewer must differ whenever review is required.

### 4. Build dependency-aware batches

Preserve the plan graph. No conflicting locks. No internal unmet dependencies in parallel batches.
Compute first globally ready task, next ready task per model, first switch, and blockers.

### 5. Install switch checkpoints

Use the checkpoint template on every model change. Never transfer an in-progress task between
executors without recorded reassignment.

### 6. Keep AGENTS.md as an index

Discovery instructions only. `PROGRESS.md` remains the sole operational pointer.

### 7. Validate and transition

```text
python skills/route-ai-work-by-capability/scripts/validate_routing.py docs/ai/<project-slug>
```

On success increment `routing_revision` and set:

```yaml
stage: ROUTING
status: IMPLEMENTATION_READY
stage_owner: route-ai-work-by-capability
required_skill: execute-routed-task
successor_skill: review-implementation-evidence
handoff_status: READY
writer_skill: null
```

Stop. Do not start implementation.

## Change control

- Bad assignment/capability/batch → `REROUTE_REQUIRED`
- Incomplete plan semantics → `REPLAN_REQUIRED`
- Intent change → brainstorm
- Technical contradiction → investigation

## Prohibitions

- Do not repair plan semantics.
- Do not implement tasks.
- Do not assign unregistered models.
- Do not claim readiness unless validation succeeds.
