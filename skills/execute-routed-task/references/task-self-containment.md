# Task self-containment and stop signals

A validated, routed task should be executable by reading only that task. This reference is about
what to do when it is not, and how to recognize a task that was never actually ready to execute.

## What a self-contained task must include

- Every file path, code excerpt, or convention needed to execute it, repeated inline rather than
  referenced as "see the phase document" — the executor may not have that document loaded this
  session.
- An acceptance criterion that does not depend on knowledge established only in another task, without
  restating the essential part here.
- A real example (an actual "before" snippet and the expected "after," or an observed concrete use
  case) rather than an abstract instruction like "improve error handling."

An exception is allowed for ordering: "depends on F02-002 being complete" may be referenced without
repeating its content — but the content needed to execute the current task may not be.

## Signs a task was not actually ready

- The acceptance criteria contain a subjective, unverifiable item ("cleaner," "better UX") with no
  observable check behind it.
- The "what to do" implies more steps than a small, predictable diff should need, or depends on "what
  we find" during execution.
- The task mixes two different domains (for example, UI and business logic, or frontend and a
  database migration) that should have been split with an explicit dependency between them.
- A file the task needs to touch is not inside its declared write scope.

Any of these is a stop signal: escalate with `status: REPLAN_REQUIRED` rather than silently
resolving the ambiguity in the direction that seems most convenient to implement.

## Escalating instead of guessing

When a task is ambiguous or incomplete, the safest default is to do less, not more: implement only
the part that is unambiguous and verifiable, record exactly what remains undecided, and stop. Never
extend the write scope, invent a missing contract, or assume a product decision that the plan did not
actually make.
