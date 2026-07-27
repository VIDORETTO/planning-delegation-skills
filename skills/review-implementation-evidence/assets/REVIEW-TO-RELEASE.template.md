---
workflow_contract: skill-team/v3
handoff_type: review-to-release
project_id: <PROJECT_ID>
producer_skill: review-implementation-evidence
consumer_skill: validate-release-readiness
input_revision: <IMPLEMENTATION_REVISION>
output_revision: <REVIEW_REVISION>
handoff_status: NOT_READY
validation_command: python skills/review-implementation-evidence/scripts/validate_review.py docs/ai/<project-slug>
validation_result: NOT_RUN
generated_at: <ISO-8601>
---

# Handoff — Review to Release

## Identification

- Project: `<PROJECT_ID>` / `<project-slug>`
- Review revision: `<INT>`
- Implementation revision approved: `<INT>`
- Review report: `../review/REVIEW-REPORT.md`

## Summary

<What was approved and at what confidence, including any accepted MEDIUM/LOW findings.>

## Artifact inventory

- `review/REVIEW-REPORT.md`
- `findings/*.md` (including accepted, non-blocking items)

## Preserved decisions

<Decisions confirmed correct during review, with task IDs.>

## Allowed open questions

<Non-blocking questions release validation may consider but not required to resolve. State `None.`
if empty.>

## Blockers

`None.` — no open `BLOCKING`/`HIGH` finding remains.

## Consumer write scope

`validate-release-readiness` may create/update `release/*`. It must not edit `review/*`,
`findings/*`, or implementation source files.

## Forbidden files

- `review/REVIEW-REPORT.md`
- `findings/*.md`

## Commands and results

| Command | Result |
|---|---|
| `python skills/review-implementation-evidence/scripts/validate_review.py docs/ai/<project-slug>` | PASS |

## Stop instruction

`validate-release-readiness` evaluates release gates from this approval; it does not re-review the
implementation itself.
