---
name: create-spec-driven-plan
description: Create or repair implementation-ready, spec-driven project plans from a validated brainstorm handoff. Use when Codex must preserve product intent, formalize requirements, define contracts, phases, atomic tasks, traceability and validation, then prepare a handoff for capability-based routing without performing routing or implementation.
---

# Create Spec-Driven Plan

Produce a versioned planning system that another agent can execute without reconstructing product intent. This skill owns only the planning stage of `planning-delegation/v2`.

## Load resources

- Read [references/planning-method.md](references/planning-method.md) completely.
- Copy and adapt the assets instead of inventing a parallel document system.
- Run [scripts/validate_plan.py](scripts/validate_plan.py) after every plan change.
- Never invoke `route-ai-work-by-capability` in this operation.

## Exclusive stage ownership

Execute only the stage belonging to this skill. Do not invoke, execute or mix the next skill in the same operation.

This skill may start only when `PROGRESS.md` declares:

~~~yaml
workflow_contract: planning-delegation/v2
stage: BRAINSTORM
status: BRAINSTORM_READY
next_skill: create-spec-driven-plan
handoff_status: READY
~~~

It also requires `handoffs/BRAINSTORM-TO-PLAN.md`, and its brainstorm revision must equal `brainstorm_revision` in `PROGRESS.md`. If the current state belongs to another skill, do not modify that stage's artifacts; report the required skill. A legacy project without v2 state must be explicitly migrated before planning.

At entry, change only the operational pointer to `stage: PLAN`, `status: PLAN_IN_PROGRESS`, `active_skill: create-spec-driven-plan`, and `handoff_status: NOT_READY`. Preserve brainstorm artifacts and revisions.

At completion:

1. validate all planning artifacts;
2. generate `handoffs/PLAN-TO-ROUTING.md`;
3. increment `plan_revision` and record `plan_based_on_brainstorm_revision`;
4. update `PROGRESS.md` to `PLAN_VALIDATED`;
5. set `next_skill: route-ai-work-by-capability` and `handoff_status: READY`;
6. stop.

## Workflow

### 1. Validate and consume the brainstorm handoff

Read `PROGRESS.md`, `handoffs/BRAINSTORM-TO-PLAN.md`, the active brainstorm artifact, `SOURCE-REGISTER.md`, and only then other referenced sources. Reject stale or incomplete handoffs.

In `plan/ANALYSIS.md`, record:

- brainstorm revision and handoff path;
- preserved decisions and answered questions;
- imported assumptions;
- rejected suggestions that remain rejected;
- candidate requirements and their stable origins.

Do not repeat answered interview questions. Preserve `DEC-*`, `ASM-*`, `RISK-*`, `BR-*`, `JRN-*` and `CR-*` IDs. When formalizing a candidate, create a `REQ-*` and retain its `CR-*` origin in traceability.

### 2. Establish authority and reconstruct intent

Create or update `SOURCE-REGISTER.md` before making design decisions. Classify statements as MUST, SHOULD, MAY, INFERRED, PROPOSAL, REJECTED or DEFERRED. Treat prior assistant text as advisory, not authority.

Analyze the repository before proposing greenfield structure. Record contradictions rather than silently resolving conflicts. Label every inference and its evidence.

### 3. Bound the product and specify contracts

- Separate first usable release, total vision, non-goals and future work.
- Define measurable release gates before tasks.
- Specify domain states, data ownership, APIs/events, security boundaries, retries, idempotency, observability, deletion, migration and rollback only to implementation-ready depth.
- Use defaults for non-blocking choices and decision records for material tradeoffs.

### 4. Build the document system

Under `docs/ai/<project-slug>/`, use the shared `PROGRESS.md` and create/update:

- `SOURCE-REGISTER.md`, `CONTEXT-INDEX.md`, `GLOSSARY.md`;
- `plan/00-MASTER.md`, `ANALYSIS.md`, `PRODUCT-SCOPE.md`, `USER-JOURNEYS.md`, `BUSINESS-RULES.md`;
- `ARCHITECTURE.md`, `DOMAIN-DATA.md`, `API-CONTRACTS.md`, `SECURITY.md`, `OPERATIONS.md`;
- `QUALITY-EVALUATION.md`, `ROADMAP.md`, `TRACEABILITY.md`, `DECISIONS-RISKS.md`, `REFERENCES.md`, `HISTORY.md`;
- `plan/phases/F00.md` and later phases;
- `plan/task-context/<TASK-ID>.md` for critical or extensive tasks;
- `handoffs/PLAN-TO-ROUTING.md` only after validation.

`AGENTS.md` is discovery-only. `PROGRESS.md` is the sole operational pointer. Detail documents are authoritative only for their subjects. Do not duplicate mutable status in `00-MASTER.md` or `AGENTS.md`.

### 5. Decompose into phases and tasks

Every task must include stable ID, requirement and decision IDs, executor `UNASSIGNED`, reviewer `NONE`, state, priority, risk, rationale, mandatory reading, dependencies, write scope, non-scope, observable objective, contracts/errors, invariants, security/privacy, expected implementation, tests, acceptance, rollback, evidence and escalation conditions.

Dependencies must exist and form an acyclic graph. A task must not depend on itself. Tasks may be `PENDING`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE` or `CANCELLED`; at most one task is `IN_PROGRESS`. A `COMPLETE` task requires evidence. A `BLOCKED` task requires a blocker.

### 6. Add traceability and deterministic continuation

Map original source/candidate requirement to formal requirement, decision, release, task, oracle, security control and evidence. Every task maps to at least one requirement; every active requirement maps to a task.

The progress pointer must identify the active artifact, current task, next action, blockers, last validation and synchronized revisions. The next task must exist and have complete dependencies.

### 7. Validate and hand off

Run:

~~~text
python skills/create-spec-driven-plan/scripts/validate_plan.py docs/ai/<slug>
~~~

Generate `PLAN-TO-ROUTING.md` with plan/brainstorm revisions, counts, unassigned tasks, hard gates, mixed tasks, dependency validation, open questions, defaults, commands/results and the exact files routing may alter. Then set:

~~~yaml
stage: PLAN
status: PLAN_VALIDATED
active_skill: create-spec-driven-plan
next_skill: route-ai-work-by-capability
handoff_status: READY
~~~

Do not route tasks or implement the product.

## Change control

- Small change: update task and traceability, increment `plan_revision`, and invalidate routing if affected.
- Structural change (integration, schema, actor or MVP): set `REPLAN_REQUIRED`, `next_skill: create-spec-driven-plan`.
- Product-intent change (audience, problem or primary outcome): set `REBRAINSTORM_REQUIRED`, `next_skill: brainstorm-idea-with-user`.

Record the classification and reason. An implementation agent must not silently choose a category.

## Output contract

Report planning directory, master entrypoint, consumed brainstorm revision, plan revision, phase/task/requirement counts, validation command/result, handoff path, unresolved blockers and the next skill. Keep the user summary short and stop after handoff.

## Failure rules

- Do not plan from a stale or unauthorized handoff.
- Do not overwrite brainstorm decisions or revive rejected suggestions.
- Do not expose private chain-of-thought; provide rationale and evidence.
- Do not leave placeholders, broken links, ambiguous task order or unverifiable acceptance.
- Do not mark planning artifacts as implemented features.
- Do not repair missing product requirements or architecture during routing; return to this skill through `REPLAN_REQUIRED`.
