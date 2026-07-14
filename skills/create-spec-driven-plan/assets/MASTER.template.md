# Master execution document

## Mission

<PRODUCT_OUTCOME>

## Authority and reading order

1. latest user request;
2. repository agent instructions;
3. this master;
4. progress pointer;
5. active phase/task;
6. contracts and references.

## Current state

- State: PLANNING_COMPLETE
- Next task: <TASK_ID>
- Implementation started: no

## Start command

On “start”:

1. read master, progress and active phase;
2. inspect existing work;
3. mark the task IN_PROGRESS;
4. implement the smallest verified batch;
5. update progress/history.

## Continue command

1. resume compatible IN_PROGRESS task;
2. otherwise choose the first ready PENDING task;
3. never skip dependencies;
4. record tests and next action.

## Invariants

1. <INVARIANT>
2. <INVARIANT>

## Definition of Ready

- objective and dependencies are clear;
- inputs/outputs/errors are specified;
- acceptance is testable;
- required decisions have defaults.

## Definition of Done

- implementation and tests pass;
- security/compatibility reviewed;
- documentation updated;
- evidence recorded;
- next task selected.

## Allowed states

- PENDING
- IN_PROGRESS
- BLOCKED
- COMPLETE
- CANCELLED

## Prohibitions

- do not mark incomplete work complete;
- do not overwrite user work;
- do not bypass tests or security gates;
- do not infer new scope silently.
