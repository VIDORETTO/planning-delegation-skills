# Model routing

## Tiers

| Model | Tier | Role |
|---|---|---|
| <STRONG_MODEL> | STRONG | architecture, critical reasoning and risk |
| <ECONOMY_MODEL> | ECONOMY | explicit mechanical implementation |

## Rules

1. every task appears exactly once;
2. task Executor field matches this matrix;
3. dependencies control readiness;
4. no queue steals from another;
5. mixed tasks are split before assignment.

## Assignments

| Task ID | Executor | Rationale category |
|---|---|---|
| <TASK-ID> | <MODEL> | <MECHANICAL_OR_HARD_GATE> |

## Switching cadence

| Phase | Sequence |
|---|---|
| <PHASE> | <ECONOMY> → <STRONG> → <ECONOMY> |

## Current readiness

- next <ECONOMY_MODEL> task:
- next <STRONG_MODEL> task:
- blocking dependency:

## Update rule

When adding or splitting a task:

1. update phase spec;
2. assign exactly one executor here;
3. add Executor to the task;
4. update roadmap/traceability/counts;
5. run routing validation.
