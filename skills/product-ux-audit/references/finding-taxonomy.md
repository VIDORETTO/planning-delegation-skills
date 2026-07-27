# Finding taxonomy

## Summary

Use one two-axis taxonomy for every finding.

## Nature

| Nature | Meaning |
|---|---|
| `OBSERVED_DEFECT` | Reproducible problem visible in rendered evidence |
| `EVIDENCE_BASED_RECOMMENDATION` | Improvement grounded in evidence, not yet a product decision |
| `PRODUCT_DECISION_REQUIRED` | Trade-off or intent choice the owner must make |

## Impact

| Impact | Meaning |
|---|---|
| `CRITICAL` | Blocks core task, causes harmful action, or severe accessibility failure |
| `HIGH` | Major friction or consistency failure on primary journeys |
| `MEDIUM` | Noticeable quality issue on common paths |
| `LOW` | Polish or minor inconsistency |

## Effort

| Effort | Meaning |
|---|---|
| `UNKNOWN` | Code not investigated |
| `LOW` / `MEDIUM` / `HIGH` | Estimate with declared confidence |

Never invent effort from vibes alone. If code was not read, use `UNKNOWN`.

## Planning handoff rule

Only user-approved `OBSERVED_DEFECT` and `EVIDENCE_BASED_RECOMMENDATION` items may enter
`UX-AUDIT-TO-PLAN.md`. `PRODUCT_DECISION_REQUIRED` items remain decisions, not tasks.
