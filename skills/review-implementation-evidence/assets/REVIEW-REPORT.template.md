---
workflow_contract: skill-team/v3
document_type: review-report
project_id: <PROJECT_ID>
project_slug: <project-slug>
review_revision: <INT>
implementation_revision_reviewed: <INT>
outcome: REVIEW_APPROVED | CHANGES_REQUIRED | REROUTE_REQUIRED | REPLAN_REQUIRED
updated_at: <ISO-8601>
---

# Review Report

## Identification

- Project: `<PROJECT_ID>` / `<project-slug>`
- Implementation revision reviewed: `<INT>`
- Source handoff: `../handoffs/IMPLEMENTATION-TO-REVIEW.md`

## Verification performed

- Diff read directly: yes/no, scope
- Tests/checks re-run: <list and results>
- Acceptance criteria confirmed against code: <task IDs>

## Scope adherence

<Files changed vs. declared write scope. Note any drift.>

## Contracts, security, and regression risk

<What was checked and the result.>

## Findings summary

| ID | Classification | Location | Summary |
|---|---|---|---|
| FND-001 | BLOCKING \| HIGH \| MEDIUM \| LOW \| QUESTION \| OUT_OF_SCOPE | `path:line` | <summary> |

## Outcome

`<REVIEW_APPROVED | CHANGES_REQUIRED | REROUTE_REQUIRED | REPLAN_REQUIRED>` — <one-line rationale>

## Next required skill

`<execute-routed-task | route-ai-work-by-capability | create-spec-driven-plan | investigate-existing-codebase | validate-release-readiness>`
