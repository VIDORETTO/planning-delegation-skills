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
- Generate `plan/CONSISTENCY-REPORT.md` with [scripts/analyze_plan.py](scripts/analyze_plan.py) before routing.
- Never invoke routing, execution, review, or release in this operation.

## Exclusive stage ownership

Write only `plan/`, `PLAN-TO-ROUTING.md`, and plan fields in `PROGRESS.md`.

Start only when `PROGRESS.md` declares `required_skill: create-spec-driven-plan` with a validated
discovery handoff (`BRAINSTORM-TO-PLAN`, `CODEBASE-TO-PLAN`, `UX-AUDIT-TO-PLAN`, or a validated
combination), or `discovery/COMPACT-BRIEF.md` with no pending structural decisions.

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
| `compact` | `PROGRESS`, `SOURCE-REGISTER`, `PLAN-MANIFEST`, `00-MASTER`, `SPEC`, one phase with tasks, `TRACEABILITY`, `PLAN-TO-ROUTING` |
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

### 2.1 Generate the compact product specification

Create `plan/SPEC.md` from validated discovery using the SPEC template. It is a compact derived view,
not a replacement for discovery artifacts. Preserve discovery IDs and source authority in every
requirement origin. Define P1 journeys that each deliver independently observable value and include
testable Given/When/Then scenarios. Record functional and quality requirements with stable `REQ-*`
IDs, origin, priority, release, oracle, and state; copy those fields into traceability.

Write product behavior and measurable outcomes, not a preferred framework, runtime, database, or
deployment stack. An implementation detail is allowed only when an explicit product constraint
requires it; mark that requirement `Implementation constraint: EXPLICIT`. Return to discovery when
an actor, outcome, or product rule needed by a story is unconfirmed.

### 2.2 Clarify planning gaps incrementally

Ask exactly one plan-level material question per interaction. Persist it immediately in `plan/SPEC.md`
with a stable `Q-*` ID, decision key, source, authority, revision, recommendation, acceptance state, and
recomputed readiness. Do not repeat answered or superseded questions, and do not allow conflicting active
answers for one decision key. Recommendations remain `PROPOSAL` until accepted.

Planning may resolve only plan-level detail. If an answer changes the audience, problem, intended outcome,
or MVP, preserve the answer, mark it `RETURNED_TO_DISCOVERY`, set the return to
`brainstorm-idea-with-user`, and stop. Planning resumes only from a new validated discovery revision. Five
accepted questions is a checkpoint to summarize remaining gaps and ask whether to continue, never a hard
limit. Structural ambiguity blocks `PLAN_VALIDATED`.

### 3. Specify contracts to implementation-ready depth

Domain states, data ownership, APIs/events, security boundaries, retries, idempotency,
observability, deletion, migration, and rollback — only as deep as the profile and risk require.

### 3.1 Apply governance before and after design

For `standard` and `critical` profiles, create `GOVERNANCE.md` from the governance template and
`plan/GOVERNANCE-CHECK.md` from the governance-check template. `compact` explicitly permits both
records to be absent; if either exists, both must validate. Define versioned principles, authority,
rationale, amendments, and exceptions. Record every applicable principle before technical design and
again after contracts and tasks are designed.

Applicable law and stronger security controls take precedence over product convenience and any
exception. Explicit user decisions retain authority over product intent unless they conflict with law
or stronger security controls. Escalate such conflicts; never silently resolve them. A confirmed
conflict with a `MUST` principle blocks validation until it is resolved or has a traceable exception
with an authorized decision maker and rationale.

### 3.2 Check written requirement quality

Create one `plan/checklists/<domain>.md` record from the requirements-checklist template for each
applicable domain. Standard and critical plans must cover requirements completeness, clarity, internal
consistency, acceptance measurability, scenario coverage, and assumptions/dependencies; add the
authorization/isolation, retention/deletion, integration retry, migration/rollback, and observability/redaction
domains when applicable. Compact plans may use only applicable checklists.

Every item has a stable `CHK-*` ID, a written-requirement question, a `REQ-*` reference or explicit
`[Gap]`, `[Ambiguity]`, `[Conflict]`, or `[Assumption]` marker, and traceability. Do not use checklist items
as implementation tests. Mark unresolved items `CRITICAL` only when they block a safe plan; mark non-blocking
findings `ADVISORY`. Only unchecked critical items block `PLAN_VALIDATED`.

Set each checklist's specification revision to the current plan revision. After a material specification change,
re-evaluate every applicable checklist before validation and mark it `CURRENT`; a stale revision or incomplete
re-evaluation blocks validation.

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

### 5.1 Analyze cross-artifact consistency

Run `python scripts/analyze_plan.py docs/ai/<slug> --write` after traceability and checklist updates.
It inventories requirements, tasks, paths, revisions, and governance records, persists stable findings and
coverage metrics, and is deterministic for unchanged artifacts. Resolve every `BLOCKING` finding before
`PLAN_VALIDATED`; review or explicitly disposition `ADVISORY` findings without treating probabilistic semantic
judgment as a hard gate.

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
- [assets/SPEC.template.md](assets/SPEC.template.md)
- [assets/SOURCE-REGISTER.template.md](assets/SOURCE-REGISTER.template.md)
- [assets/TASK-CONTEXT.template.md](assets/TASK-CONTEXT.template.md)
- [assets/PLAN-TO-ROUTING.template.md](assets/PLAN-TO-ROUTING.template.md)
- [assets/GOVERNANCE.template.md](assets/GOVERNANCE.template.md)
- [assets/GOVERNANCE-CHECK.template.md](assets/GOVERNANCE-CHECK.template.md)

- [assets/REQUIREMENTS-CHECKLIST.template.md](assets/REQUIREMENTS-CHECKLIST.template.md)
- [assets/CONSISTENCY-REPORT.template.md](assets/CONSISTENCY-REPORT.template.md)

- [assets/PLAN-MANIFEST.template.md](assets/PLAN-MANIFEST.template.md)
