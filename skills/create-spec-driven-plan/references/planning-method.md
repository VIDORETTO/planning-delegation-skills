# Planning method

This method implements workflow contract `skill-team/v3`. Planning consumes a validated brainstorm handoff and produces a validated routing handoff. It never performs either adjacent stage.

## Stage contract

Entry requires discovery ready with `required_skill: create-spec-driven-plan`, `handoff_status: READY`, and matching discovery revisions in `PROGRESS.md` and the consumed handoff (`BRAINSTORM-TO-PLAN`, `CODEBASE-TO-PLAN`, and/or `UX-AUDIT-TO-PLAN`). Planning owns `PLAN_IN_PROGRESS` and `PLAN_VALIDATED` only. Exit requires a validated `PLAN-TO-ROUTING.md`, synchronized revisions and `required_skill: route-ai-work-by-capability`; then stop.

`PROGRESS.md` is the only operational pointer. `AGENTS.md` is an index, the handoff is the stage input contract, and subject documents own their detailed domains.

## Contents

1. Planning target
2. Evidence extraction
3. Requirement reconstruction
4. Gap analysis
5. Scope and vertical slices
6. Architecture depth
7. Document system
8. Task decomposition
9. Acceptance and evaluation
10. Continuity protocol
11. Plan auditing
12. Anti-patterns

## 1. Planning target

The target is not a long document. It is an executable decision system:

- the next action is unambiguous;
- dependencies prevent unsafe skipping;
- contracts constrain implementation;
- tests decide completion;
- progress survives context loss;
- another model can work without rereading the entire conversation.

Optimize for implementation correctness, not maximum page count.

## 2. Evidence extraction

Build a source matrix before designing:

| Source | Authority | Extract |
|---|---|---|
| explicit user decisions | highest for product intent | required outcomes and constraints, subject to recorded change control |
| user-provided files | high | domain facts and accepted decisions |
| repository | high for current state | code, stack, conventions and debt |
| existing plan | medium | intent, status and assumptions |
| prior assistant answer | advisory | candidate ideas and missed risks |
| external documentation | factual | current APIs, versions and limits |

For each statement classify:

- MUST: explicit non-negotiable;
- SHOULD: important but negotiable;
- MAY: extension;
- INFERRED: necessary implication;
- PROPOSAL: planner improvement;
- REJECTED/DEFERRED.

Record conflicts rather than silently choosing whichever appears last, unless source authority resolves them.

## 3. Requirement reconstruction

Analyze five layers:

1. Outcome — what changes for the user?
2. Capability — what must the system do?
3. Quality — how safe, fast, accurate and observable?
4. Operation — how installed, updated, resumed and deleted?
5. Evolution — how new providers/formats/features enter?

Extract user concerns as failure statements:

- “The system must update only changed fields” becomes “volatile-only changes must not trigger semantic recomputation.”
- “Do not mix products and prices” becomes “critical cross-record association errors must be zero in the release oracle; uncertain fields abstain.”

This converts anxiety into gates.

## 4. Gap analysis

Check every concept for:

- owner/actor;
- input;
- output;
- identity;
- lifecycle/state;
- persistence;
- permission;
- failure/retry;
- versioning;
- deletion;
- observability;
- test oracle.

Common gaps in conversational plans:

- no first release;
- no state machine;
- no source of truth;
- no idempotency;
- no atomic publication;
- no data isolation;
- no negative tests;
- no compatibility/version strategy;
- no cost limit;
- “AI decides” without schema, allowlist or validator.

Add missing controls, but distinguish planner proposals from user requirements.

## 5. Scope and vertical slices

Prefer vertical slices over layer-only phases.

Weak sequence:

1. build every parser;
2. build every database adapter;
3. build UI;
4. finally connect them.

Stronger sequence:

1. foundation/contracts;
2. one simple source end to end;
3. one high-value complex source;
4. generalize the proven abstractions;
5. production hardening;
6. ecosystem expansion.

A vertical slice should include intake, validation, persistence, user-facing access, tests and failure handling.

Use release levels:

- R0: reproducible foundation;
- R1: first usable path;
- R2+: high-value domain slices;
- production release: security/operations/DR;
- future: breadth and optional UX.

## 6. Architecture depth

Specify architecture at three levels:

### Stable core

- domain terms;
- invariants;
- state transitions;
- boundaries;
- public contracts;
- data ownership.

### Reference implementation

- chosen runtime/database/framework;
- local and production deployment;
- first adapters.

### Replaceable options

- providers;
- object stores;
- vector/search engines;
- workflow engines;
- UI.

Avoid two extremes:

- underspecification: “use best practices”;
- false precision: pinning every implementation detail before evidence.

Use ADRs for choices with material tradeoffs or migration cost.

## 7. Document system

Recommended authority:

1. explicit user decisions with source and revision;
2. `PROGRESS.md` for operational state;
3. validated stage handoff;
4. contracts/security for their subjects;
5. active task and its context package;
6. architecture and roadmap;
7. historical conversation.

A new user request does not silently overwrite a validated plan. Classify it through change control and record its source.

Recommended files:

- ../PROGRESS.md;
- ../SOURCE-REGISTER.md;
- ../CONTEXT-INDEX.md;
- ../GLOSSARY.md;
- 00-MASTER.md;
- PRODUCT-SCOPE.md;
- ANALYSIS.md;
- USER-JOURNEYS.md;
- BUSINESS-RULES.md;
- ARCHITECTURE.md;
- DOMAIN-DATA.md;
- API-CONTRACTS.md;
- SECURITY.md;
- OPERATIONS.md;
- QUALITY-EVALUATION.md;
- ROADMAP.md;
- TRACEABILITY.md;
- DECISIONS-RISKS.md;
- REFERENCES.md;
- HISTORY.md;
- phases/PHASE-ID.md;
- task-context/TASK-ID.md for critical or extensive tasks;
- ../handoffs/PLAN-TO-ROUTING.md.

Use links rather than duplicating the same rule in many files. Duplicate only critical safety constraints and keep them mechanically auditable.

## 8. Task decomposition

A good task has:

- one dominant objective;
- one owner/executor;
- bounded file/component scope;
- known dependencies;
- a testable end state;
- rollback or failure semantics when needed.

It also records requirement and decision IDs, reviewer placeholder, priority/risk, mandatory reading, bounded write scope and non-scope, security/privacy, required evidence and escalation triggers. During planning the executor remains `UNASSIGNED`; routing owns assignment.

Split when:

- design and mechanical implementation require different capabilities;
- more than one public contract changes independently;
- a migration and a feature can be verified separately;
- security review is hidden inside generic wiring;
- the task cannot be checkpointed safely.

Do not split when:

- tests and implementation form one behavior;
- migration/model/repository must change atomically;
- pieces would have no independent acceptance.

Task wording pattern:

~~~text
TASK-ID — Verb + observable result
Objective:
Dependencies:
Inputs/outputs/errors:
Implementation:
Tests:
Acceptance:
Evidence:
~~~

Use stable IDs. Never recycle an ID for a different behavior.

Preserve brainstorm identity across formalization: `CR-001` becomes a formal `REQ-001` while `TRACEABILITY.md` retains `CR-001` and its `SRC-*` source as origin.

## 9. Acceptance and evaluation

Acceptance must answer “how will another agent prove this?”

Include:

- happy path;
- invalid input;
- boundary;
- authorization/isolation;
- retry/idempotency;
- concurrency if applicable;
- integration with real dependency when critical;
- migration/rollback;
- observability/redaction.

For extraction/AI/retrieval, create versioned fixtures and goldens. Measure precision, recall, abstention, citation and forbidden outcomes. A model confidence value is not a ground truth.

Define release gates before tuning thresholds. Never lower a safety threshold just to make the release pass.

## 10. Continuity protocol

Keep one progress pointer with:

- project state;
- current release/phase/task;
- executor;
- next ready task;
- last complete task;
- next concrete action;
- blockers;
- commands/results;
- timestamp.

At task start:

1. verify dependencies;
2. mark in progress;
3. record planned tests;
4. make a bounded change.

At task completion:

1. run tests/checks;
2. compare with spec;
3. record evidence;
4. mark complete;
5. append history;
6. select next ready task.

At context loss, a fresh agent reads master, progress, active phase and referenced contracts.

## 10.1 Change control

- Small detail with no structural impact: update task and traceability, increment `plan_revision`, and invalidate/revise routing if affected.
- Structural change such as schema, integration, actor or MVP: `REPLAN_REQUIRED`, next skill `create-spec-driven-plan`.
- Change to audience, problem or primary product outcome: `REBRAINSTORM_REQUIRED`, next skill `brainstorm-idea-with-user`.

Always record classification and rationale. Implementation does not silently expand scope.

## 11. Plan auditing

Mechanical checks:

- all local links resolve;
- task IDs are unique;
- task states use the allowed vocabulary;
- every task has dependencies/acceptance;
- executor exists if routed;
- phase and route task sets match;
- master/progress/phase links exist.
- dependencies exist, are not self-referential and form an acyclic graph;
- checkbox and state agree;
- complete tasks contain evidence and blocked tasks contain a blocker;
- every active requirement and task participates in traceability;
- progress pointers name existing, ready tasks;
- revisions match across progress and handoffs;
- no placeholders remain in a validated plan.

Semantic checks:

- all critical requirements map to tests;
- no release depends on future work without a gate;
- no provider/framework leaks into domain;
- no destructive action is implicit;
- no “automatic AI” path bypasses policy;
- first release produces user value;
- future breadth does not block the first slice.

## 12. Anti-patterns

- One universal script.
- Phase named only “backend” or “frontend” with no value.
- Hundreds of formats in MVP.
- Task “implement system”.
- Checkboxes without acceptance.
- Multiple competing progress files.
- Status inferred from code rather than recorded.
- Tests deferred to the final phase.
- AI output trusted without schema/evidence.
- Low-cost agent asked to invent architecture while implementing.
- Expensive model used for formatting/configuration that a cheaper model can execute safely.
