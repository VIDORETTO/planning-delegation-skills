# Source authority

## Summary

Record every material claim with a source ID. Prefer primary, dated, and project-owned sources.

## Source types

| Type | Examples | Typical authority |
|---|---|---|
| `USER` | Direct user statements | Binding for intent unless later revised |
| `REPO` | Code, configs, tests, commits | Binding for technical reality |
| `DOCS` | Official docs with version/date | Binding for external contracts |
| `RESEARCH` | Articles, benchmarks, competitor notes | Advisory unless adopted |
| `INFERENCE` | Agent conclusions | Never binding without evidence |

## Required fields per `SRC-*`

- ID
- type
- authority (`BINDING` / `ADVISORY` / `UNVERIFIED`)
- date or version
- claim summary
- validity window or `CURRENT`
- link or location

## Rules

1. Do not invent sources.
2. External research is allowed only when it can change product decisions.
3. Mark expired or superseded sources instead of deleting them silently.
4. When user statement conflicts with repo evidence, record both and escalate to the user.
5. Handoffs must cite the `SRC-*` IDs that justify preserved decisions.
