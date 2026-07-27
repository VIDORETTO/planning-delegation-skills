# Independent verification method

The value of this skill depends entirely on not trusting the executor's own account of its work.
Execution history and evidence are a hypothesis to confirm, not a verdict to rubber-stamp.

## Confirm by reading, not by summary

- Read the actual diff (or the actual current state of the touched files), not only the executor's
  description of it.
- Re-run the tests/checks the task specifies where feasible, rather than trusting a reported PASS.
- Compare the real acceptance criteria, one item at a time, against what the code now does — an
  executor can log success while a subtler correctness or edge-case problem remains, especially one
  that required a different level of judgment to notice.

## What independent verification specifically looks for

- **Silent scope creep**: files touched outside the declared write scope, even if the change itself
  looks reasonable.
- **Criteria drift**: an acceptance item reinterpreted more loosely than the plan intended.
- **Untested edge cases**: inputs or states the task's own tests do not exercise but the change
  affects.
- **Regression risk**: whether the change could break a caller or consumer not covered by the task's
  own tests, especially in a shared or high-blast-radius module.
- **Evidence gaps**: a claim in `execution/EVIDENCE.md` that does not actually hold up once checked
  directly.

## When to treat the log as reliable enough to sample rather than fully re-verify

Only when: the task was classified low-risk at routing time, review policy for it is `SAMPLE` rather
than `REQUIRED_BEFORE_COMPLETE`/`REQUIRED_BEFORE_RELEASE`, and the diff is small and isolated. Even
then, spot-check at least the acceptance criteria and the write-scope boundary directly; do not
approve purely from the log summary.

## Adversarial framing

Where review policy is `ADVERSARIAL_REVIEW`, actively look for a way the implementation could be
wrong or exploitable rather than only checking that it does what it claims — try boundary inputs,
concurrent access, and failure paths the task's own tests may not cover.
