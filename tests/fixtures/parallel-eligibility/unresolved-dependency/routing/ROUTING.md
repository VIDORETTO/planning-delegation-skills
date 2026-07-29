| Task | Executor | Tier | Hard gate | Score | Confidence | Reviewer | Review mode | Batch | Locks | Parallel eligible | Parallel rationale | Isolation strategy | Rationale |
|---|---|---|---|---:|---|---|---|---|---|---|---|---|---|
| PAR-001 | MODEL-A | ECONOMY | NONE | 0 | HIGH | NONE | NONE | ECONOMY-B01 | NONE | false | Prerequisite is sequential. | NOT_APPLICABLE | Explicit scope. |
| PAR-002 | MODEL-A | ECONOMY | NONE | 0 | HIGH | NONE | NONE | ECONOMY-B01 | NONE | true | Scope is disjoint after prerequisite. | ISOLATED_WORKTREE_SEQUENTIAL_MERGE_REVIEW | Explicit scope. |
