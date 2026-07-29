# Requirements Quality Checklist: <DOMAIN>

- Workflow profile: <compact|standard|critical>
- Applicable: true
- Applicability rationale: <why this domain applies to the written specification>
- Specification revision: <PLAN_REVISION>
- Re-evaluation state: CURRENT

This checklist evaluates written requirements only. It must not instruct an executor to run, test, or verify implementation behavior.

## Items

- [x] CHK-001 - Is the requirement complete enough to state the actor, outcome, boundary, and observable result? [REQ-001]
  - Severity: CRITICAL
  - State: PASS
  - Traceability: REQ-001

- [ ] CHK-002 - Is the missing retention period explicitly recorded? [Gap]
  - Severity: ADVISORY
  - State: OPEN
  - Traceability: GAP-001 / ASM-001

## Re-evaluation

When a material specification change increments the plan revision, update every applicable checklist's
`Specification revision`, reassess each item, and set `Re-evaluation state: CURRENT` only after the reassessment.
Unchecked `CRITICAL` items block `PLAN_VALIDATED`; unchecked `ADVISORY` items remain visible but do not block.
