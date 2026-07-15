# Master planning document

## Mission

<PRODUCT_OUTCOME>

## Document authority

`PROGRESS.md` is the sole operational pointer. This document does not store mutable workflow status.

1. explicit user decisions recorded with source and revision;
2. `PROGRESS.md` for current workflow state;
3. validated handoff for stage input;
4. subject contracts (`BUSINESS-RULES`, `API-CONTRACTS`, `DOMAIN-DATA`, `SECURITY`);
5. active phase/task and its mandatory context;
6. architecture, roadmap and historical material.

Conflicts must be recorded in `DECISIONS-RISKS.md`; they must not be silently resolved by recency alone.

## Required reading protocol

1. read `../PROGRESS.md`;
2. read the active artifact and current handoff;
3. read only the contracts and task-context referenced by the current task;
4. verify dependencies before changing task state.

## Product invariants

1. <INVARIANT>
2. <INVARIANT>

## Release sequence

- <RELEASE_AND_MEASURABLE_GATE>

## Definition of Ready

- objective, requirements and dependencies are explicit;
- contracts, write scope and non-scope are explicit;
- acceptance and evidence are testable;
- material decisions are resolved or escalated.

## Definition of Done

- implementation and required tests pass;
- security and compatibility checks pass;
- evidence is recorded in the designated file;
- traceability and `PROGRESS.md` are updated.

## Allowed task states

- PENDING
- IN_PROGRESS
- BLOCKED
- COMPLETE
- CANCELLED

## Change control

- small: update task/traceability and increment plan revision;
- structural: `REPLAN_REQUIRED`;
- product intent: `REBRAINSTORM_REQUIRED`.

## Prohibitions

- do not duplicate operational status here;
- do not bypass dependencies, tests, security gates or review;
- do not infer new scope silently;
- do not implement from historical conversation when a validated specification exists.
