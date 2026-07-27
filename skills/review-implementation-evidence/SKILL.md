---
name: review-implementation-evidence
description: Independently review a completed implementation task, its diff, tests, evidence, scope, contracts, security, and regression risk. Use when routing or project policy requires review, or when the user asks whether completed work actually satisfies the plan. Approve, request bounded changes, or escalate to rerouting, replanning, or rediscovery. Do not silently implement fixes.
---

# Review Implementation Evidence

Confirm, independently, that completed implementation work actually satisfies the plan — do not
trust the execution log at face value. This skill owns only the `REVIEW` stage of `skill-team/v3`
and never implements the fix it finds.

## Workflow contract

```text
skill-team/v3
… → execute-routed-task (IMPLEMENTATION)
→ review-implementation-evidence (REVIEW, when required)
→ validate-release-readiness (RELEASE)
```

`PROGRESS.md` is the sole operational pointer. Never write `next_skill`; use `required_skill` and
`successor_skill`. A read-only reviewer subagent may inspect implementation files; only this skill's
own review artifacts are written here.

## Required resources

1. Read [references/independent-verification-method.md](references/independent-verification-method.md) before trusting any claim in `execution/HISTORY.md`.
2. Read [references/finding-classification.md](references/finding-classification.md) before writing findings.
3. Use [assets/REVIEW-REPORT.template.md](assets/REVIEW-REPORT.template.md) for the main artifact.
4. Use [assets/FINDING.template.md](assets/FINDING.template.md) per finding.
5. Use [assets/REVIEW-TO-IMPLEMENTATION.template.md](assets/REVIEW-TO-IMPLEMENTATION.template.md) when requesting changes.
6. Use [assets/REVIEW-TO-RELEASE.template.md](assets/REVIEW-TO-RELEASE.template.md) when approving.
7. Run [scripts/validate_review.py](scripts/validate_review.py) before declaring a review outcome.

## Exclusive stage ownership

Execute only review. Do not implement the fix you find, replan, reroute, or promote the release in
the same operation.

## Entry gate

| Situation | Required action |
|---|---|
| `status: REVIEW_REQUIRED`, `required_skill: review-implementation-evidence`, `handoffs/IMPLEMENTATION-TO-REVIEW.md` is `READY` | Start review |
| `status: REVIEW_IN_PROGRESS`, `required_skill: review-implementation-evidence` | Resume without repeating fully-verified findings |
| `status: CHANGES_REQUIRED` returns from `execute-routed-task` with a new `implementation_revision` | Re-review only the changed scope, not the whole batch again |
| Any other status owned by another skill | Stop without modifying artifacts |

Confirm the handoff's `output_revision` matches `PROGRESS.md` `implementation_revision` before
starting. A stale handoff is not reviewable; return it with `status: TASK_BLOCKED` and
`required_skill: execute-routed-task`.

## Method

### 1. Verify independently, do not just read the log

Treat `execution/HISTORY.md` and `execution/EVIDENCE.md` as a starting hypothesis, not a verdict.
Read the actual diff, run the specified tests/checks yourself where feasible, and confirm the
acceptance criteria against the real code — not against the executor's own account of it. See
[references/independent-verification-method.md](references/independent-verification-method.md).

### 2. Check scope adherence

Confirm every changed file is inside the task's declared write scope. A change outside that scope is
itself a finding, regardless of whether the change is otherwise correct.

### 3. Check contracts, security, and regression risk

- Contract/schema/API changes match what planning and routing authorized.
- No new security, privacy, or tenancy issue was introduced.
- No untested regression risk was introduced in a shared or high-blast-radius area.

### 4. Classify every finding

Use exactly: `BLOCKING`, `HIGH`, `MEDIUM`, `LOW`, `QUESTION`, `OUT_OF_SCOPE`. See
[references/finding-classification.md](references/finding-classification.md) for definitions and
which findings force which outcome.

### 5. Decide the outcome

| Outcome | When | Transition |
|---|---|---|
| Approve | No `BLOCKING`/`HIGH` finding remains open | `status: REVIEW_APPROVED`, `required_skill: validate-release-readiness` |
| Request bounded changes | `BLOCKING`/`HIGH` findings are local and within the same write scope | `status: CHANGES_REQUIRED`, `required_skill: execute-routed-task` |
| Reroute | Wrong assignment or capability mismatch caused the defect | `status: REROUTE_REQUIRED`, `required_skill: route-ai-work-by-capability` |
| Replan | Task/dependency/acceptance/contract itself was incomplete | `status: REPLAN_REQUIRED`, `required_skill: create-spec-driven-plan` |
| Rediscover | Technical reality contradicts the investigation | `required_skill: investigate-existing-codebase` |

Never implement the fix yourself, even a "small" one. Record it as a finding and route it back.

### 6. Produce artifacts and stop

Write `review/REVIEW-REPORT.md` and one `findings/<FINDING-ID>.md` per non-trivial finding. Generate
either `handoffs/REVIEW-TO-IMPLEMENTATION.md` (changes requested) or `handoffs/REVIEW-TO-RELEASE.md`
(approved) — never both for the same revision.

Run:

```text
python skills/review-implementation-evidence/scripts/validate_review.py docs/ai/<project-slug>
```

Only after it passes, update `PROGRESS.md` with the decided status, increment `review_revision`, set
`handoff_status: READY`, and set `required_skill`/`successor_skill` per the outcome table. Stop. Do
not start implementation, routing, or release in the same operation.

## Escalation and change control

The reviewer records the classification and reason but does not silently assume ownership of the
return stage — it names the required skill and stops.

## Output contract

Produce only `review/REVIEW-REPORT.md`, `findings/*`, exactly one outgoing handoff for the current
revision, and the review transition in `PROGRESS.md`. Do not claim `REVIEW_APPROVED` unless
validation succeeds and no open `BLOCKING`/`HIGH` finding remains.

## Prohibitions

- Do not implement a fix for a finding you raise.
- Do not approve based on `execution/HISTORY.md` alone, without independent verification.
- Do not edit `execution/*` or implementation source files.
- Do not produce both an implementation-return handoff and a release handoff for the same revision.
- Do not weaken a `BLOCKING` finding to `HIGH` (or lower) to force an approval.

## Resources

- [assets/REVIEW-REPORT.template.md](assets/REVIEW-REPORT.template.md)
- [assets/REVIEW-TO-IMPLEMENTATION.template.md](assets/REVIEW-TO-IMPLEMENTATION.template.md)
- [assets/REVIEW-TO-RELEASE.template.md](assets/REVIEW-TO-RELEASE.template.md)
- [references/review-method.md](references/review-method.md)
