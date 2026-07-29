# Independent verification method

The value of this skill depends entirely on not trusting the executor's own account of its work.
Execution history and evidence are a hypothesis to confirm, not a verdict to rubber-stamp.

Before verification, confirm the canonical `IMPLEMENTATION-TO-REVIEW.md` is READY with PASS
validation and its output revision equals the active implementation revision. A stale handoff cannot
be reviewed or approved.

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

## Finding record and return rule

For every actionable finding, record one severity and one gap type: `missing`, `partial`,
`contradicts`, or `unrequested`. Cite the task and requirement IDs, then point `evidence_path` at an
existing relative reviewed file or command-evidence artifact and describe the actual observed fact.
Do not cite a planned change as evidence.

- Return a local implementation defect within the authorized write scope to `execute-routed-task`.
- Return an assignment, capability, batch, or lock defect to `route-ai-work-by-capability`.
- Return a missing task, requirement, dependency, acceptance, contract, or governance obligation to
  `create-spec-driven-plan`.
- Return a contradiction with current technical evidence to `investigate-existing-codebase`.
- Return changed audience, problem, outcome, or MVP intent to `brainstorm-idea-with-user`.

The reviewer records the selected owner and stops. It never edits source, task lists, plans, routing,
or execution evidence to make a finding disappear.

## When to treat the log as reliable enough to sample rather than fully re-verify

Only when: the task was classified low-risk at routing time, review policy for it is `SAMPLE` rather
than `REQUIRED_BEFORE_COMPLETE`/`REQUIRED_BEFORE_RELEASE`, and the diff is small and isolated. Even
then, spot-check at least the acceptance criteria and the write-scope boundary directly; do not
approve purely from the log summary.

## Adversarial framing

Where review policy is `ADVERSARIAL_REVIEW`, actively look for a way the implementation could be
wrong or exploitable rather than only checking that it does what it claims — try boundary inputs,
concurrent access, and failure paths the task's own tests may not cover.
