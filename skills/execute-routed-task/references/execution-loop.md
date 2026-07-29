# Execution loop

This reference describes how one execution session should behave from start to stop, and what an
executor must never do — regardless of which model is running this skill.

## Loop for one execution session

1. Read the task's own specification (or, at minimum: shared context the task explicitly references,
   plus the specific task to execute).
2. Check `execution/HISTORY.md` for what already happened — do not trust only a checklist; the log
   holds the real result of every prior attempt on this task.
3. Identify the next incomplete task, respecting phase and batch order. Never skip an incomplete
   phase to reach a task that looks easier in a later phase, even if dependencies technically allow
   it.
4. Execute only that task. Do not advance future tasks "while already in there."
5. Validate against the acceptance criteria item by item.
6. Update the task's state, append one line to `execution/HISTORY.md`, and record supporting detail
   in `execution/EVIDENCE.md`.
7. If any stop signal appears mid-task, stop immediately. Revert partial changes if they are left
   inconsistent, and record `ESCALATED: <TASK-ID> — <reason>` in the log instead of trying to resolve
    it unilaterally.

Before starting, consume only `handoffs/ROUTING-TO-IMPLEMENTATION.md` whose plan and routing
revisions match `PROGRESS.md`; no alternate or legacy handoff path is valid.

## What an executor must never do

- Never decide an open product question alone — if the acceptance criteria do not cover a case, that
  is a stop signal, not an invitation to pick the interpretation that seems most reasonable.
- Never expand the diff to files outside the declared write scope without escalating first.
- Never mark a task complete if any acceptance item fails, even if the rest works.
- Never rewrite an entire module when the task asked for a localized adjustment.
- Never take a task requiring a capability tier that has no model registered for it — that stays
  pending for routing or human decision.
- Never take another executor's in-progress task without a recorded reassignment from routing.

## Execution log format

Each line must let someone (the user, or a reviewer in a later session) understand what happened
without reconstructing the whole session:

```text
| 2026-07-27 | F02-003 | MODEL-B | Complete — acceptance verified, 3 files changed |
| 2026-07-28 | F02-005 | MODEL-B | Escalated — diff expanded into the auth module, outside scope |
```

Use registered Model IDs (from `MODEL-CAPABILITIES.md`), not informal model names, so the log stays
auditable across sessions.

## When a review session or a later session revisits this work

Treat `execution/HISTORY.md` as the primary record of what was attempted, but do not assume it is
complete or correct without independently checking the current state of the code — an execution
session can log success even when the result has a subtler problem that required a different level
of judgment to notice. That independent confirmation is exactly what
`review-implementation-evidence` exists to do.
