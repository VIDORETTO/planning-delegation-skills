---
workflow_contract: skill-team/v3
document_type: review-report
project_id: <PROJECT_ID>
project_slug: <project-slug>
review_revision: <INT>
implementation_revision_reviewed: <INT>
outcome: REVIEW_APPROVED | CHANGES_REQUIRED | REROUTE_REQUIRED | REPLAN_REQUIRED | CODEBASE_INVESTIGATION_IN_PROGRESS | BRAINSTORM_IN_PROGRESS
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

| ID | Gap type | Classification | Location | Requirement(s) | Task | Evidence | Return owner | Summary |
|---|---|---|---|
| No findings | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Independent verification found no gaps. |

## Outcome

`<REVIEW_APPROVED | CHANGES_REQUIRED | REROUTE_REQUIRED | REPLAN_REQUIRED | CODEBASE_INVESTIGATION_IN_PROGRESS | BRAINSTORM_IN_PROGRESS>` — <one-line rationale>

## Next required skill

`<execute-routed-task | route-ai-work-by-capability | create-spec-driven-plan | investigate-existing-codebase | brainstorm-idea-with-user | validate-release-readiness>`
