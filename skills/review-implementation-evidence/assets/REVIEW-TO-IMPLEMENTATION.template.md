---
workflow_contract: skill-team/v3
handoff_type: review-to-implementation
project_id: <PROJECT_ID>
producer_skill: review-implementation-evidence
consumer_skill: execute-routed-task
input_revision: <IMPLEMENTATION_REVISION>
output_revision: <REVIEW_REVISION>
handoff_status: NOT_READY
validation_command: python skills/review-implementation-evidence/scripts/validate_review.py docs/ai/<project-slug>
validation_result: NOT_RUN
generated_at: <ISO-8601>
---

# Handoff — Review to Implementation

## Identification

- Project: `<PROJECT_ID>` / `<project-slug>`
- Review revision: `<INT>`
- Implementation revision reviewed: `<INT>`
- Review report: `../review/REVIEW-REPORT.md`

## Summary

<Why changes are requested rather than approval.>

## Artifact inventory

- `review/REVIEW-REPORT.md`
- `findings/*.md` (open items only)

## Preserved decisions

<Anything from the implementation that remains correct and must not be re-litigated.>

## Allowed open questions

<Non-blocking questions the executor may resolve locally. State `None.` if empty.>

## Blockers

<Open BLOCKING/HIGH findings that must be fixed before the next review pass.>

## Consumer write scope

`execute-routed-task` may modify only the files named in the open findings, within their original
declared write scope. It must not edit `review/*` or `findings/*`.

## Forbidden files

- `review/REVIEW-REPORT.md`
- `findings/*.md`

## Commands and results

| Command | Result |
|---|---|
| `python skills/review-implementation-evidence/scripts/validate_review.py docs/ai/<project-slug>` | PASS \| FAIL |

## Stop instruction

`execute-routed-task` fixes only the open findings and returns for another review pass. It does not
reopen closed findings or expand scope beyond what is listed here.
