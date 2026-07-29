---
name: validate-release-readiness
description: Evaluate whether a planned release is ready using completed tasks, approved reviews, tests, security and privacy gates, migration and rollback readiness, observability, operational documentation, and accepted risks. Produce an evidence-backed release decision and blockers. Do not deploy, implement missing work, or weaken gates to approve the release.
---

# Validate Release Readiness

Decide whether a release is ready from evidence already produced by earlier stages — this skill
audits and decides, it does not do the remaining work itself. It owns only the `RELEASE` stage of
`skill-team/v3`.

## Workflow contract

```text
skill-team/v3
… → review-implementation-evidence (REVIEW, when required)
→ validate-release-readiness (RELEASE)
```

`PROGRESS.md` is the sole operational pointer. Never write `next_skill`; use `required_skill` and
`successor_skill`.

## Required resources

1. Read [references/release-gate-checklist.md](references/release-gate-checklist.md) before evaluating any release.
2. Read [references/decision-and-blockers.md](references/decision-and-blockers.md) before writing the decision.
3. Use [assets/RELEASE-READINESS.template.md](assets/RELEASE-READINESS.template.md) for the decision artifact.
4. Use [assets/POST-RELEASE.template.md](assets/POST-RELEASE.template.md) after a release ships.
5. Run [scripts/validate_release.py](scripts/validate_release.py) before declaring a release decision.

## Exclusive stage ownership

Execute only release evaluation and, when applicable, the recorded release/post-release transition.
Do not implement missing work, do not deploy, and do not weaken a gate to force an approval.

## Entry gate

| Situation | Required action |
|---|---|
| `status: RELEASE_REVIEW_REQUIRED`, `required_skill: validate-release-readiness`, `handoffs/REVIEW-TO-RELEASE.md` `READY` | Evaluate gates |
| Review was explicitly waived for the whole batch and `handoffs/IMPLEMENTATION-TO-RELEASE.md` names `validate-release-readiness` as consumer | Evaluate gates using that handoff instead |
| `status: RELEASE_BLOCKED`, blockers resolved by an upstream stage | Re-evaluate only the previously blocking gates |
| `status: RELEASED` and observed outcomes are due | Move to post-release review |
| Any other status owned by another skill | Stop without modifying artifacts |

Confirm the consumed handoff's input and output revisions match the corresponding revisions in
`PROGRESS.md` before evaluating. A stale handoff is not evaluable; report which upstream skill must
refresh it.

## Method

### 1. Assemble the evidence set

Collect: completed task list and their evidence, the review outcome (or the recorded waiver),
test/build results, and the project's `workflow_profile` (`compact` / `standard` / `critical`), which
determines which gates below are mandatory versus not applicable.

### 2. Evaluate every applicable gate

Work through [references/release-gate-checklist.md](references/release-gate-checklist.md): tests,
security/privacy, migration and rollback readiness, observability, operational documentation, and the
accepted-risk register. Profiles only omit irrelevant documents; they never weaken a security,
privacy, or data-loss gate.

### 3. Write an evidence-backed decision

Every gate result must cite the artifact or command it came from — a gate marked `PASS` without a
citation is not a valid pass. See
[references/decision-and-blockers.md](references/decision-and-blockers.md).

### 4. Decide

| Decision | When |
|---|---|
| `RELEASE_READY` | Every mandatory gate for this `workflow_profile` passes or has an explicitly accepted risk with an owner |
| `RELEASE_BLOCKED` | Any mandatory gate fails without an accepted-risk justification |

Never mark a failing security, privacy, or migration/rollback gate as passed to reach `RELEASE_READY`.
An accepted risk requires an explicit owner and rationale in `RELEASE-READINESS.md`, not silence.

### 5. Record blockers precisely

For `RELEASE_BLOCKED`, list each blocking gate, why it fails, and which upstream skill must resolve
it (`execute-routed-task` for missing implementation, `review-implementation-evidence` for missing
approval, `create-spec-driven-plan` for a missing/incomplete requirement, or a human decision for an
unaccepted risk).

### 6. Validate and stop

Run:

```text
python skills/validate-release-readiness/scripts/validate_release.py docs/ai/<project-slug>
```

Only after it passes, update `PROGRESS.md`, increment `release_revision`, and set status/
`required_skill` per the decision. Stop. Do not deploy and do not start implementing a missing gate
yourself.

### 7. Post-release review

Once a human or an external deployment process has actually shipped the release and set
`status: RELEASED`, this skill may later be invoked again to produce `release/POST-RELEASE.md`:
compare observed outcomes against the release decision's expectations, record any regression or
follow-up, and set `status: POST_RELEASE_REVIEW_REQUIRED` with the appropriate `required_skill`
(`investigate-existing-codebase` for an unexpected technical issue, `brainstorm-idea-with-user` for an
unexpected product outcome, or `NONE` if the release fully matched expectations).

## Output contract

Produce only `release/RELEASE-READINESS.md`, `release/POST-RELEASE.md` when applicable, and the
release transition in `PROGRESS.md`. Do not claim `RELEASE_READY` unless validation succeeds and
every mandatory gate is evidenced.

## Prohibitions

- Do not deploy or trigger a release process.
- Do not implement missing work to make a gate pass.
- Do not weaken, skip, or silently reclassify a security, privacy, or migration/rollback gate.
- Do not mark a gate `PASS` without a citation to the artifact or command that proves it.
- Do not accept a risk without an explicit owner and rationale recorded in the decision artifact.

## Resources

- [assets/RELEASE-READINESS.template.md](assets/RELEASE-READINESS.template.md)
- [assets/POST-RELEASE.template.md](assets/POST-RELEASE.template.md)
- [references/release-gates.md](references/release-gates.md)
