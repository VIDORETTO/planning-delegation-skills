---
name: create-spec-driven-plan
description: Create or repair implementation-ready, spec-driven project plans from conversations, repositories, product ideas, requirement documents, or incomplete backlogs. Use when Codex must analyze goals and concerns, close requirement gaps, define scope and architecture, produce phased roadmaps and atomic tasks, add acceptance tests and traceability, create master instructions for future AI agents, or make a plan resumable through repeated “start/continue” commands.
---

# Create Spec-Driven Plan

Produce a planning system that another agent can execute without reconstructing product intent. Record decisions, evidence, assumptions and tradeoffs; never expose private chain-of-thought.

## Load resources

- Read [references/planning-method.md](references/planning-method.md) for analysis, decomposition and quality heuristics.
- Copy/adapt templates from assets instead of inventing the document structure.
- Run [scripts/validate_plan.py](scripts/validate_plan.py) after writing or changing a plan.
- If the user requests routing by model capability or cost, also use the route-ai-work-by-capability skill.

## Workflow

### 1. Inventory the source of truth

1. Locate conversations, briefs, current code, existing plans, constraints and agent instructions.
2. Read all user-designated primary sources completely.
3. Inspect the repository before proposing a greenfield structure.
4. Separate:
   - explicit requirements;
   - inferred needs;
   - prior assistant suggestions;
   - decisions already made;
   - unresolved decisions;
   - constraints and non-goals.
5. Treat earlier assistant output as input, not authority.

Do not implement the system while the requested deliverable is only planning.

### 2. Reconstruct intent

Create a concise analysis covering:

- problem and desired outcome;
- users and operating modes;
- explicit and implicit concerns;
- critical failure modes;
- quality/security/cost expectations;
- contradictions and missing decisions;
- improvements adopted and suggestions rejected;
- practical definition of success.

For inferred requirements, label the inference and explain its evidence. Avoid fabricated certainty.

### 3. Bound the product

1. Define principles and invariants.
2. Separate total vision, first usable release and future backlog.
3. Choose vertical slices that prove an end-to-end capability.
4. State non-goals per release.
5. Define measurable release gates before listing tasks.
6. Prefer replaceable contracts over implementing every provider/format immediately.

### 4. Specify architecture and contracts

Define only what implementation needs:

- components and dependency direction;
- deployment modes;
- domain entities and state transitions;
- persistence and versioning;
- APIs/SDK/CLI/events;
- security boundaries;
- idempotency, retries and publication semantics;
- observability and deletion;
- testing/evaluation.

Record defaults for non-blocking decisions. Use ADR placeholders for decisions that must wait for evidence.

### 5. Build the document system

At minimum create:

1. master execution document;
2. progress pointer;
3. product/scope analysis;
4. architecture and domain contracts;
5. security/privacy plan;
6. quality/evaluation plan;
7. roadmap/releases;
8. phase specifications;
9. traceability matrix;
10. decisions/risks/pending register;
11. references;
12. history/handoff log.

Adapt [assets/MASTER.template.md](assets/MASTER.template.md), [assets/PROGRESS.template.md](assets/PROGRESS.template.md), [assets/PHASE.template.md](assets/PHASE.template.md), [assets/ANALYSIS.template.md](assets/ANALYSIS.template.md), and [assets/TRACEABILITY.template.md](assets/TRACEABILITY.template.md).

Declare document authority and the mandatory reading order. Keep exactly one operational progress pointer.

### 6. Decompose into phases and tasks

For every phase define:

- objective and value;
- entry/exit conditions;
- dependencies;
- explicit non-scope;
- deliverables;
- tasks;
- phase-level gate.

For every task define:

- stable ID and title;
- state;
- executor/owner when routing applies;
- dependencies;
- observable objective;
- inputs, outputs and errors;
- implementation steps;
- invariants/security concerns;
- tests and evidence;
- acceptance criteria.

Split tasks that mix independent design and mechanical work. Do not create tiny tasks that cannot be verified independently.

### 7. Make continuation deterministic

The master/progress protocol must tell an agent how to:

- start from an empty repository;
- inspect and preserve existing work;
- resume an in-progress task;
- select the next ready task;
- mark completion only with evidence;
- handle a real blocker;
- update history and next action;
- react to “start” and “continue” without asking repeated questions.

Use PENDING, IN_PROGRESS, BLOCKED, COMPLETE and CANCELLED, or a clearly mapped equivalent. Never use “almost done”.

### 8. Add traceability and gates

Map each requirement to phase/task and expected test/evidence. Include cross-cutting gates for:

- security;
- data isolation;
- migrations;
- idempotency;
- provenance;
- rollback/deletion;
- quality/regression;
- cost and performance.

Every critical requirement must have a testable oracle, not only a confidence score.

### 9. Audit

Run:

~~~text
python skills/create-spec-driven-plan/scripts/validate_plan.py <planning-directory>
~~~

Use --require-executor only when every task must include an Executor field.

Fix:

- duplicate/malformed task IDs;
- missing task state/executor;
- broken local links;
- absent core documents;
- inconsistent task counts;
- stale progress pointers.

Then manually verify that all release gates are measurable and that no task claims implementation already exists.

## Output contract

Report:

- planning directory;
- master entrypoint;
- current/next task;
- phase/task counts;
- audit result;
- implementation status;
- major defaults or unresolved blockers.

Keep the user-facing summary short; the plan files carry the detail.

## Failure rules

- Do not hide uncertainty behind exhaustive prose.
- Do not list every possible feature in the first release.
- Do not use a taxonomy as a substitute for implementation order.
- Do not mark planning artifacts as implemented features.
- Do not leave future agents to infer task order, state or acceptance.
- Do not expose private reasoning; provide reproducible method, rationale and evidence.
