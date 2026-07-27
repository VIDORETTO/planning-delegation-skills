---
workflow_contract: skill-team/v3
document_type: implementation-evidence
project_id: <PROJECT_ID>
project_slug: <project-slug>
implementation_revision: <INT>
updated_at: <ISO-8601>
---

# Implementation Evidence

Append-only. One entry per task attempt.

## <TASK-ID>

- Executor model: `<MODEL-ID>`
- Attempt: <n>
- Files changed: <list>
- Commands run:

```text
<command>
<relevant output excerpt>
```

- Acceptance criteria check:

| Criterion | Result |
|---|---|
| <criterion> | PASS \| FAIL |

- Result: `COMPLETE` \| `BLOCKED` \| `ESCALATED`
