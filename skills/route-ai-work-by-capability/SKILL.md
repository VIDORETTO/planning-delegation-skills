---
name: route-ai-work-by-capability
description: Classify and route implementation tasks among AI models by capability, risk and cost, then create enforceable ownership, switching and handoff instructions. Use when a user has a phased plan/backlog and wants stronger models for architecture or critical work, cheaper/weaker models for mechanical implementation, model-specific task queues, an AGENTS.md routing protocol, or validation that every task has exactly one suitable executor.
---

# Route AI Work by Capability

Minimize total expected delivery cost, not only inference price. A cheap model that causes architectural rework is expensive; a strong model used for repetitive wiring is wasteful.

## Load resources

- Read [references/classification-rubric.md](references/classification-rubric.md) before assigning tasks.
- Adapt [assets/AGENTS.template.md](assets/AGENTS.template.md) and [assets/ROUTING.template.md](assets/ROUTING.template.md).
- Run [scripts/validate_routing.py](scripts/validate_routing.py) after classification.
- If tasks lack stable IDs, dependencies or acceptance criteria, use the create-spec-driven-plan skill first.

## Workflow

### 1. Normalize model tiers

Map user-provided models to capability roles:

- STRONG: best reasoning/reliability; higher cost.
- ECONOMY: lower cost; follows explicit, narrow specs.

Keep the user-facing names in output, for example GROK_4_5 and COMPOSER. Do not infer the active model; the user or persisted progress sets it.

For more than two models, define ordered tiers and review boundaries before routing.

### 2. Verify task readiness

Every routable task must have:

- stable ID;
- one observable objective;
- dependencies;
- bounded scope;
- tests/acceptance;
- no hidden architectural decision.

Split tasks that combine high-risk design and mechanical follow-up. Do not split silently after an executor starts; create new IDs and update traceability.

### 3. Classify with hard gates

Assign STRONG immediately when a task includes any hard gate:

- architecture or public contract;
- security, authorization, privacy or tenant isolation;
- schema migration/data loss risk;
- concurrency, idempotency, distributed workflow or atomic publication;
- novel/ambiguous algorithm or inference;
- critical financial/legal/business association;
- parser/OCR/layout reconciliation;
- production rollback/DR;
- evaluation threshold/promotion decision.

Otherwise score the rubric. Route ECONOMY only when the task is explicit, reversible, narrow and deterministically testable.

Do not classify by task length or filename count alone.

### 4. Optimize total expected cost

Estimate qualitatively:

~~~text
expected_total_cost =
  model_execution_cost
  + probability_of_rework × impact_of_rework
  + review_and_coordination_cost
~~~

Use STRONG when rework can invalidate downstream tasks. Use ECONOMY when output can be cheaply tested and replaced.

### 5. Make dependency-aware queues

1. Preserve the original dependency graph.
2. Assign every task exactly once.
3. Compute the next ready task per tier.
4. Show expected model switching points by phase.
5. Never skip an unmet dependency to keep a model busy.
6. When no task is ready for the active tier, return AGUARDANDO_EXECUTOR and name the required tier/task.

Avoid parallel work that edits the same contracts/files unless the plan explicitly isolates it.

### 6. Embed ownership

Create a routing document with:

- tier definitions;
- classification rules;
- all task IDs and assigned executor;
- rationale category;
- switching cadence;
- initial ready task per executor;
- update/audit rules.

Also add an Executor/Owner field directly to every task specification. The routing matrix is the audit source; the task field prevents accidental execution when only a phase file is open.

### 7. Create repository agent instructions

The root AGENTS.md must tell future agents:

- which master/context document to read first;
- progress and routing read order;
- phrases that select each executor;
- how selection persists across “continue”;
- that executor identification comes from the user;
- how to select compatible ready work;
- not to take work from another queue;
- how to checkpoint on model switch;
- what a lower-tier agent must escalate;
- how completion evidence is recorded.

Use the AGENTS asset as a starting point, preserving any higher-priority repository instructions.

### 8. Update progress state

Persist:

- Active executor;
- Active queue;
- Current task;
- Next ready task globally;
- Next ready task per executor;
- required switch/dependency;
- last complete task;
- next concrete action.

An executor announcement alone may act as “continue” after implementation starts if the user wants that behavior. Before initial start authorization, only persist the selection.

### 9. Validate

Run:

~~~text
python skills/route-ai-work-by-capability/scripts/validate_routing.py \
  <tasks-directory> <routing-document> \
  --tiers <ECONOMY_NAME>,<STRONG_NAME>
~~~

The validator must report:

- same task set in specs and routing;
- no duplicate route;
- no missing task;
- embedded Executor fields match the matrix;
- count per tier.

Manually review hard gates; a mechanically valid assignment can still be unsafe.

## Lower-tier escalation rule

The ECONOMY executor must stop and record STRONG_REVIEW_REQUIRED when it discovers:

- missing/contradictory contract;
- new schema or migration decision;
- security policy ambiguity;
- unanticipated concurrency/state issue;
- failing critical oracle requiring algorithm change;
- a need to broaden scope.

It may fix local syntax/config/test issues within the task; it may not invent a new architecture to proceed.

## Strong-tier rule

The STRONG executor should:

- resolve hard decisions and record ADRs;
- make downstream mechanical work explicit;
- correct a completed economy dependency only when it blocks strong work, with history;
- avoid consuming the economy queue merely because it can.

## Output contract

Report:

- tier/model mapping;
- counts;
- routing document;
- root agent instructions;
- initial ready task and executor;
- first switching point;
- validation result.

## Failure rules

- Do not use model brand prestige as the rubric.
- Do not assign one task to multiple executors.
- Do not route an unready task.
- Do not let a cheap model make an implicit high-impact decision.
- Do not let the strong model become a bottleneck for deterministic wiring.
- Do not claim savings without considering rework and review.
