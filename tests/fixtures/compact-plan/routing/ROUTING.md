---
workflow_contract: skill-team/v3
document_type: routing
plan_revision: 1
routing_revision: 1
routing_based_on_plan_revision: 1
status: VALIDATED
updated_at: 2026-07-27T12:00:00-03:00
---

# Model routing

| Task | Executor | Tier | Hard gate | Score | Confidence | Reviewer | Review mode | Batch | Locks | Parallel eligible | Parallel rationale | Isolation strategy | Rationale |
|---|---|---|---:|---:|---|---|---|---|---|---|---|---|---|
| F01-001 | MODEL-STRONG | STRONG | NONE | 2 | HIGH | MODEL-REVIEW | REQUIRED_BEFORE_RELEASE | STRONG-B01 | file:src/example.ts | FALSE | Single bounded write remains sequential. | NOT_APPLICABLE | Defined malformed-payload guard needs independent release review. |

| Task | Ambiguity | Coupling | Irreversibility | State/concurrency | Data correctness | Verification difficulty | External variability | Specification incompleteness | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F01-001 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |

### Batch STRONG-B01

- Executor: MODEL-STRONG
- Entry dependencies: NONE
- Tasks: F01-001
- Locks: file:src/example.ts
- Execution: SEQUENTIAL
- Isolation and merge strategy: NOT_APPLICABLE
- Validation command: pytest -k parser
