# AGENTS.md — <PROJECT>

These instructions apply to the repository.

## Initial context

Read first:

1. <MASTER_PATH>
2. <PROGRESS_PATH>
3. <ROUTING_PATH>
4. active phase/task;
5. referenced contracts.

Do not implement from historical conversation when specs exist.

## Executor selection

- User says “<STRONG_PHRASE>”: set executor <STRONG_MODEL>.
- User says “<ECONOMY_PHRASE>”: set executor <ECONOMY_MODEL>.
- Persist selection in progress.
- Do not infer or switch executor without the user.
- After implementation starts, an executor announcement may also mean “continue”.

## Ownership

<STRONG_MODEL> executes only tasks routed to <STRONG_MODEL>.

<ECONOMY_MODEL> executes only tasks routed to <ECONOMY_MODEL>.

The economy model must record STRONG_REVIEW_REQUIRED and stop if it encounters architecture, schema, security, concurrency, destructive migration or critical algorithm ambiguity.

## Task selection

1. Resume compatible IN_PROGRESS work.
2. Otherwise select the first ready PENDING task in the active queue.
3. Never skip dependencies.
4. Never assume another queue’s task.
5. If none is ready, set AGUARDANDO_EXECUTOR and name the required model/task.

## Completion

1. mark IN_PROGRESS;
2. implement smallest verified batch;
3. run specified checks;
4. record evidence;
5. mark COMPLETE only when acceptance passes;
6. update history and next ready task/executor.

## Essential rules

- preserve existing work;
- obey master invariants;
- do not expose secrets/private data;
- do not bypass tests/security;
- do not silently broaden scope.
