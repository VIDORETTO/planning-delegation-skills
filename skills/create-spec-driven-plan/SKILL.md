---
name: create-spec-driven-plan
description: >
  Create or repair an implementation-ready, spec-driven plan from validated discovery artifacts
  or a sufficiently bounded change brief. Use to formalize requirements, contracts, phases,
  tasks, dependencies, acceptance, evidence, rollback, traceability, and change control.
  Support compact, standard, and critical profiles. Do not choose execution models, implement
  tasks, review code, or approve releases.
---

# Create Spec-Driven Plan

Produce a versioned planning system that another agent can execute without reconstructing product
intent. This skill owns only the planning stage of `skill-team/v3`.

## Load resources

- Read [references/planning-method.md](references/planning-method.md).
- Copy and adapt assets; do not invent a parallel document system.
- Run [scripts/validate_plan.py](scripts/validate_plan.py) after every plan change.
- Never invoke routing, execution, review, or release in this operation.

## Exclusive stage ownership

Write only `plan/`, `PLAN-TO-ROUTING.md`, and plan fields in `PROGRESS.md`.

Start only when `PROGRESS.md` declares `required_skill: create-spec-driven-plan` with a validated
discovery handoff (`BRAINSTORM-TO-PLAN`, `CODEBASE-TO-PLAN`, `UX-AUDIT-TO-PLAN`, or a validated
combination), or a compact change brief with no pending structural decisions.

At entry set `stage: PLANNING`, `status: PLAN_IN_PROGRESS`, `stage_owner` and `writer_skill` to
this skill, `handoff_status: NOT_READY`. Preserve discovery artifacts and revisions.

At completion:

1. validate planning artifacts for the active profile;
2. generate `handoffs/PLAN-TO-ROUTING.md`;
3. increment `plan_revision`;
4. set `status: PLAN_VALIDATED`, `required_skill: route-ai-work-by-capability`, `handoff_status: READY`;
5. clear `writer_skill`;
6. stop.

## Profiles

| Profile | Required artifacts |
|---|---|
| `compact` | `PROGRESS`, `SOURCE-REGISTER`, `PLAN-MANIFEST`, `00-MASTER`, one phase with tasks, `TRACEABILITY`, `PLAN-TO-ROUTING` |
| `standard` | compact plus applicable analysis, scope, journeys, rules, architecture, domain/data, API, security, quality, operations, roadmap, decisions/risks |
| `critical` | standard plus threat model, migration, rollback, DR, negative/adversarial tests, release gates, strong review requirements |

Profiles never weaken security controls.

## Workflow

### 1. Consume discovery

Read `PROGRESS.md`, the ready handoff(s), discovery artifacts, and `SOURCE-REGISTER.md`. Reject
stale or incomplete handoffs. Preserve IDs (`DEC-*`, `ASM-*`, `RISK-*`, `BR-*`, `JRN-*`, `CR-*`,
investigation evidence IDs, UX finding IDs). Formalize candidates as `REQ-*` with origin retained.

### 2. Establish authority and bound the product

Classify statements as MUST, SHOULD, MAY, INFERRED, PROPOSAL, REJECTED, or DEFERRED. Separate
first usable release, total vision, non-goals, and future work. Define measurable release gates
before tasks.

### 3. Specify contracts to implementation-ready depth

Domain states, data ownership, APIs/events, security boundaries, retries, idempotency,
observability, deletion, migration, and rollback — only as deep as the profile and risk require.

### 4. Decompose phases and tasks

Every task needs stable ID, requirement/decision origins, state, priority, risk, executor
`UNASSIGNED`, reviewer `NONE`, dependencies, mandatory reading, write scope, forbidden scope,
observable objective, inputs/outputs/errors, invariants, security/privacy, expected
implementation, tests, acceptance, rollback, evidence, and escalation conditions.

Use `plan/task-context/<TASK-ID>.md` for extensive context instead of duplicating large blocks.
Require real before/after examples only when they reduce ambiguity — not for new files, simple
config, docs, removals, or acceptance fully covered by tests.

Dependencies must exist and be acyclic. At most one `IN_PROGRESS` task. `COMPLETE` requires
evidence. `BLOCKED` requires a blocker.

### 5. Traceability and continuation

Map source/candidate → requirement → decision → release → task → oracle → evidence. Progress
pointer identifies active artifact, current task, next action, blockers, last validation, and
synchronized revisions.

### 6. Validate and hand off

```text
python skills/create-spec-driven-plan/scripts/validate_plan.py docs/ai/<slug>
```

Then stop. Do not route or implement.

## Change control

- Local detail inside contract → update task/evidence.
- Structural gap → `REPLAN_REQUIRED`, `required_skill: create-spec-driven-plan`.
- Intent change → return to `brainstorm-idea-with-user`.
- Technical contradiction → return to `investigate-existing-codebase`.
- Unapproved UX recommendation → no task until product decision.

## Prohibitions

- Do not choose models or implement.
- Do not overwrite discovery decisions or revive rejected suggestions.
- Do not leave placeholders, broken links, or unverifiable acceptance in ready plans.
- Do not mark planning artifacts as implemented features.


## Assets

Copy and adapt:

- [assets/MASTER.template.md](assets/MASTER.template.md)
- [assets/PROGRESS.template.md](assets/PROGRESS.template.md)
- [assets/PHASE.template.md](assets/PHASE.template.md)
- [assets/ANALYSIS.template.md](assets/ANALYSIS.template.md)
- [assets/TRACEABILITY.template.md](assets/TRACEABILITY.template.md)
- [assets/SOURCE-REGISTER.template.md](assets/SOURCE-REGISTER.template.md)
- [assets/TASK-CONTEXT.template.md](assets/TASK-CONTEXT.template.md)
- [assets/PLAN-TO-ROUTING.template.md](assets/PLAN-TO-ROUTING.template.md)

- [assets/PLAN-MANIFEST.template.md](assets/PLAN-MANIFEST.template.md)
