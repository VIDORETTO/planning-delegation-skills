---
name: execute-routed-task
description: Execute the current dependency-ready task or authorized batch from a validated and routed plan. Use when the active model owns the work, revisions match, write scope is explicit, and no other writer is active. Implement the smallest verified change, run required checks, record evidence, and stop on contract, architecture, security, scope, ownership, or revision problems.
---

# Execute Routed Task

Implement exactly one dependency-ready task, or one authorized batch, from a validated routing
handoff. This skill owns only the `IMPLEMENTATION` stage of `skill-team/v3`. It never plans,
routes, or reviews itself.

## Workflow contract

```text
skill-team/v3
… → route-ai-work-by-capability (ROUTING)
→ execute-routed-task (IMPLEMENTATION)
→ review-implementation-evidence (REVIEW, when required)
→ validate-release-readiness (RELEASE)
```

`PROGRESS.md` is the sole operational pointer. Never write `next_skill`; use `required_skill` and
`successor_skill`. Only one skill holds `writer_skill` at a time.

## Required resources

1. Read [references/execution-loop.md](references/execution-loop.md) before starting or resuming a task.
2. Read [references/task-self-containment.md](references/task-self-containment.md) when a task's own
   text seems incomplete, to decide between inferring locally and escalating.
3. Use [assets/EVIDENCE.template.md](assets/EVIDENCE.template.md) and
   [assets/HISTORY.template.md](assets/HISTORY.template.md) to record what happened.
4. Use [assets/BLOCKER.template.md](assets/BLOCKER.template.md) when stopping mid-task.
5. Use [assets/IMPLEMENTATION-TO-REVIEW.template.md](assets/IMPLEMENTATION-TO-REVIEW.template.md) at stage completion.
6. Run [scripts/validate_execution.py](scripts/validate_execution.py) before claiming a task or the stage is complete.

## Exclusive stage ownership

Execute only implementation. Do not plan, route, review your own work, or promote a release in the
same operation.

## Entry gate

Start a task only when all of the following hold in `PROGRESS.md`:

```yaml
workflow_contract: skill-team/v3
stage: IMPLEMENTATION
required_skill: execute-routed-task
handoff_status: READY
writer_skill: null | execute-routed-task
```

Additionally require:

- `handoffs/ROUTING-TO-IMPLEMENTATION.md` (or equivalent routing handoff) exists and is `READY`;
- its `input_revision`/`output_revision` match the plan and routing revisions in `PROGRESS.md`;
- the target task has a stable ID, one registered executor model, explicit write scope, tests, and
  non-empty acceptance criteria;
- `active_executor_model` in `PROGRESS.md` matches the task's registered executor;
- `writer_skill` is unset or already `execute-routed-task` — never start while another skill or task
  holds the write lock.

If any condition fails, do not repair the plan or routing. Record the precise failure, set
`status: REROUTE_REQUIRED` or `REPLAN_REQUIRED` as appropriate, `required_skill` to the owning skill,
and stop.

## Workflow

### 1. Take the write lock

Set `writer_skill: execute-routed-task` and `writer_task: <TASK-ID>` before touching files. If
`writer_skill` already names a different skill or task, stop and report the conflict instead of
overriding it.

### 2. Load only what the task needs

Read the task's own specification fully; read shared context only if the task references it. Check
`execution/EVIDENCE.md` and `execution/HISTORY.md` for prior attempts on this task before starting —
do not repeat known failures blind.

### 3. Identify the next task in order

Resume a compatible `IN_PROGRESS` task first. Otherwise take the first dependency-ready task assigned
to the active executor model, respecting phase and batch order. Never take another model's task and
never skip an incomplete phase to reach an easier later task.

### 4. Implement the smallest verified change

Touch only files inside the task's declared write scope. Do not expand the diff to files outside that
list without escalating first. Do not implement future tasks "while already in there."

### 5. Run required checks

Run the task's specified tests/build/lint commands. Validate against the acceptance criteria item by
item; do not mark complete if any item fails, even if the rest works.

### 6. Record evidence and stop cleanly

Append to `execution/EVIDENCE.md` (commands run, outputs, diff summary) and add one line to
`execution/HISTORY.md` per attempt, per
[references/execution-loop.md](references/execution-loop.md#execution-log-format). Update the task
state (`COMPLETE`, `BLOCKED`, or leave `IN_PROGRESS` only if the turn is ending mid-task for a
reason other than a stop signal).

### 7. Recognize stop signals

Stop immediately, do not improvise a resolution, and record `blockers/<TASK-ID>.md` from
[assets/BLOCKER.template.md](assets/BLOCKER.template.md) when you find:

- a missing or contradictory contract, schema, or security decision;
- an undecided product question the acceptance criteria do not cover;
- a required file outside the declared write scope;
- a hard task with no model registered for it;
- a critical oracle (test/check) that cannot be made to pass without a scope change.

See [references/execution-loop.md](references/execution-loop.md) for the full stop-signal list and
what the executor must never do.

### 8. Close the stage and hand off

When every task in the authorized batch reaches `COMPLETE` (or the plan's implementation scope is
otherwise exhausted), run:

```text
python skills/execute-routed-task/scripts/validate_execution.py docs/ai/<project-slug>
```

On success, increment `implementation_revision`, generate
`handoffs/IMPLEMENTATION-TO-REVIEW.md`, release the write lock (`writer_skill: null`,
`writer_task: null`), set `status: IMPLEMENTATION_COMPLETE`, and set `required_skill` /
`successor_skill` to `review-implementation-evidence` when routing marked any task's review mode
other than `NONE`, or to `validate-release-readiness` when routing explicitly waived review for the
whole batch. Do not decide to skip review yourself; only reflect what routing already recorded.

## Escalation and change control

| Finding | Return |
|---|---|
| Local implementation detail inside contract | Keep executing; update evidence |
| Bad assignment, capability mismatch, or batch conflict | `status: REROUTE_REQUIRED`, `required_skill: route-ai-work-by-capability` |
| Incomplete task, dependency, acceptance criteria, or contract | `status: REPLAN_REQUIRED`, `required_skill: create-spec-driven-plan` |
| Technical reality contradicts the investigation | `required_skill: investigate-existing-codebase` |
| Product intent, audience, or outcome changed | `required_skill: brainstorm-idea-with-user` |

Record the reason. Never silently choose the next stage yourself.

## Output contract

Produce only `execution/EVIDENCE.md`, `execution/HISTORY.md`, `blockers/<TASK-ID>.md` as needed,
`handoffs/IMPLEMENTATION-TO-REVIEW.md`, task-state updates inside existing plan documents where
authorized, and the implementation transition in `PROGRESS.md`. Do not claim `IMPLEMENTATION_COMPLETE`
unless validation succeeds.

## Prohibitions

- Do not start a task while another skill or task holds `writer_skill`.
- Do not touch files outside the declared write scope without escalating first.
- Do not mark a task `COMPLETE` with any failing acceptance item.
- Do not batch independent hard tasks together without routing's explicit authorization.
- Do not review your own diff and call it approved; that is `review-implementation-evidence`'s job.
- Do not promote a release.

## Resources

- [assets/EVIDENCE.template.md](assets/EVIDENCE.template.md)
- [assets/HISTORY.template.md](assets/HISTORY.template.md)
- [assets/IMPLEMENTATION-TO-REVIEW.template.md](assets/IMPLEMENTATION-TO-REVIEW.template.md)
- [references/stop-signals.md](references/stop-signals.md)
- [references/execution-loop.md](references/execution-loop.md)
