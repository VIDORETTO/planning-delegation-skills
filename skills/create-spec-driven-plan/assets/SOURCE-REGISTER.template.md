# Source Register

| ID | Source | Type | Authority | Version/date | Claims used | Validity |
|---|---|---|---|---|---|---|
| SRC-001 | user request | user | maximum | <ISO_DATE> | objective and constraints | permanent until superseded explicitly |
| SRC-002 | repository | repository | high for current state | <COMMIT> | stack and existing behavior | until next inspected commit |
| SRC-003 | official documentation | external | high factual | <VERSION_DATE> | API limits | review by <ISO_DATE> |

## Rules

- Use stable `SRC-*` IDs.
- Record conflicts instead of silently choosing a source.
- Prior assistant suggestions are advisory.
- Label planner additions as `INFERRED` or `PROPOSAL`.
