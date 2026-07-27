---
workflow_contract: skill-team/v3
handoff_type: ux-audit-to-plan
project_id: <project-id>
producer_skill: product-ux-audit
consumer_skill: create-spec-driven-plan
input_revision: 1
output_revision: 1
handoff_status: READY
validation_command: python skills/product-ux-audit/scripts/validate_ux_audit.py docs/ai/<slug>
validation_result: PASS
generated_at: <ISO-8601>
---

# UX audit to plan handoff

## Summary

<approved scope for planning>

## Approved findings for planning

| Finding ID | Nature | Impact | Decision | Notes |
|---|---|---|---|---|
| UX-001 | OBSERVED_DEFECT | HIGH | APPROVED | <note> |

## Explicitly excluded

| Finding ID | Reason |
|---|---|
| UX-002 | Not approved by product owner |

## Artifact inventory

- `discovery/ux/UX-AUDIT.md`
- `discovery/ux/SITEMAP.md`
- `discovery/ux/COVERAGE.md`
- selected screen reports and redacted evidence

## Consumer write scope

- `plan/`
- plan fields in `PROGRESS.md`
- `handoffs/PLAN-TO-ROUTING.md` later

## Forbidden files

- Do not modify `discovery/ux/` except to mark handoff consumption metadata if required by contract.
- Do not create tasks from excluded findings.

## Stop instruction

Validate the plan with `create-spec-driven-plan` in a separate invocation. Do not implement.
