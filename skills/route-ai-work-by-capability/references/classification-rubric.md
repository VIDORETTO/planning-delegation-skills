# Capability and cost routing rubric

## Contents

1. Goal
2. Tier definition
3. Hard gates
4. Scoring dimensions
5. Decision thresholds
6. Cost-benefit model
7. Splitting tasks
8. Dependency routing
9. Review and handoff
10. Examples
11. Anti-patterns

## 1. Goal

Route work to the least expensive model that can complete it with acceptable expected risk.

The relevant cost is:

- model usage;
- human/model review;
- retries;
- downstream rework;
- data/security incident risk;
- schedule delay from poor handoff.

The cheapest call is not necessarily the cheapest delivery.

## 2. Tier definition

### STRONG

Use for tasks requiring:

- ambiguity resolution;
- multi-component reasoning;
- architecture;
- critical correctness;
- adversarial/security analysis;
- novel algorithms;
- difficult debugging;
- high-impact tradeoffs.

### ECONOMY

Use for tasks with:

- closed contract;
- explicit steps;
- small blast radius;
- deterministic checks;
- easy rollback;
- established pattern;
- repetitive/configuration/documentation work.

If a user names models, map names to these roles explicitly and retain names in task fields.

## 3. Hard gates

Any hard gate routes to STRONG regardless of score:

| Gate | Why |
|---|---|
| domain architecture/public API | errors propagate to all consumers |
| auth/security/privacy/tenancy | incident impact is high |
| destructive/data migration | reversal may be impossible |
| concurrency/idempotency/distributed state | failures are nondeterministic |
| financial/legal/critical business mapping | plausible wrong output causes harm |
| ambiguous parser/OCR/entity resolution | requires algorithms and abstention |
| workflow durability/replay | versioning and failure semantics are subtle |
| evaluation/promotion threshold | decides what reaches production |
| incident response/DR | requires system-wide reasoning |

Do not downgrade because the spec is long or the strong model is temporarily unavailable.

## 4. Scoring dimensions

Score each 0–3 when no hard gate applies.

### Ambiguity/novelty

- 0: exact established pattern;
- 1: small local choice;
- 2: multiple viable approaches;
- 3: requirements/algorithm need discovery.

### Coupling/blast radius

- 0: isolated docs/config;
- 1: one component;
- 2: several modules/consumers;
- 3: cross-cutting foundation.

### Reversibility

- 0: delete/regenerate safely;
- 1: easy rollback;
- 2: migration/compatibility work;
- 3: irreversible/external state.

### State/concurrency

- 0: stateless;
- 1: simple local persistence;
- 2: transactions/retries;
- 3: distributed/concurrent/replay.

### Data correctness

- 0: presentation only;
- 1: non-critical mapping;
- 2: important structured data;
- 3: critical identity/money/permission.

### Verification difficulty

- 0: formatter/schema/static check;
- 1: deterministic unit/contract test;
- 2: integration/golden dataset;
- 3: probabilistic/adversarial/production-like.

### External variability

- 0: no dependency;
- 1: stable local tool;
- 2: external API/provider;
- 3: multiple providers/version-sensitive behavior.

### Specification completeness

Reverse score:

- 0: inputs/outputs/tests fully specified;
- 1: minor details;
- 2: missing cases;
- 3: requires design.

## 5. Decision thresholds

Suggested two-tier thresholds:

- 0–6: ECONOMY;
- 7–11: ECONOMY only with strong contract and cheap review; otherwise STRONG;
- 12+: STRONG.

Hard gates override.

When near threshold, ask:

- Can a deterministic test catch likely failure before downstream work?
- Can the result be discarded cheaply?
- Is the decision already documented?
- Would a wrong answer affect security, data or later architecture?

## 6. Cost-benefit model

Use a qualitative table:

| Factor | Economy | Strong |
|---|---|---|
| direct inference cost | lower | higher |
| success on explicit wiring | high | high |
| success on ambiguity | variable | higher |
| review need | higher on difficult work | lower |
| downstream rework | high if misrouted | lower on hard work |

Example:

- Formatting CI YAML costs little and has deterministic validation: ECONOMY.
- Designing idempotency keys costs more with STRONG, but a mistake duplicates data and contaminates later phases: STRONG.

## 7. Splitting tasks

Split a mixed task before assignment:

~~~text
Original:
Design auth architecture, implement middleware, write docs.

Split:
AUTH-001 STRONG — decide identity/tenant/authorization contract.
AUTH-002 ECONOMY — implement middleware from approved contract.
AUTH-003 ECONOMY — generate examples and operator docs.
AUTH-004 STRONG — run adversarial authorization review.
~~~

Rules:

- preserve dependencies;
- create new IDs;
- update traceability;
- do not have two executors edit one task concurrently;
- keep acceptance per subtask.

Do not split implementation from its essential tests.

## 8. Dependency routing

The queue is not “all economy first, then all strong.” It follows readiness.

For each iteration:

1. find IN_PROGRESS task owned by active tier;
2. otherwise compute PENDING tasks whose dependencies are COMPLETE;
3. filter by active tier;
4. choose the earliest priority/roadmap item;
5. if empty, request the tier owning the blocking dependency.

Show switching cadence:

~~~text
ECONOMY setup -> STRONG core contract -> ECONOMY wiring
-> STRONG evaluation -> ECONOMY docs -> STRONG release gate
~~~

Avoid artificial busywork for a model whose queue is not ready.

## 9. Review and handoff

### Economy completion

Require:

- deterministic checks;
- no unplanned contract change;
- files and commands recorded;
- escalation if ambiguity appeared.

### Strong completion

Require:

- decision/ADR;
- negative/adversarial tests;
- downstream contract explicit;
- mechanical follow-up ready for economy.

### Model switch

Checkpoint:

- task/state;
- diff;
- tests/results;
- decisions;
- exact next action;
- required executor.

Do not transfer an in-progress task across tiers unless the user explicitly reassigns it or it is formally split.

## 10. Examples

### Economy

- initialize repository;
- create workspace metadata;
- configure formatter/linter from approved choices;
- wire REST handlers to existing use cases;
- create CLI commands from stable SDK;
- generate docs/examples;
- instrument existing boundaries;
- implement admin UI against stable API.

### Strong

- define domain/state machine;
- schema/migration strategy;
- outbox/idempotency;
- tenant isolation;
- parsing and entity resolution;
- hybrid retrieval;
- prompt/tool security;
- durable workflows;
- deletion/DR;
- quality thresholds.

### Context-dependent

S3 adapter:

- ECONOMY if port, key policy and security contract are complete;
- STRONG if storage architecture, encryption/tenancy or retention is undecided.

E2E task:

- ECONOMY if scenario and expected outputs are complete and core is stable;
- STRONG if failures require diagnosing algorithmic or distributed behavior.

## 11. Anti-patterns

- “Big task = strong model.”
- “All code = strong, all docs = cheap.”
- Assigning based only on model name.
- Duplicate ownership.
- Letting economy silently choose a new architecture.
- Letting strong do every task.
- Skipping dependencies to keep a model utilized.
- No persisted active executor.
- No routing audit.
- Counting inference savings while ignoring rework.
