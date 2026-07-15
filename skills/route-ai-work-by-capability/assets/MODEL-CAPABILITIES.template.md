---
workflow_contract: planning-delegation/v2
document_type: model-capabilities
registry_revision: 1
assessed_at: <ISO-8601>
updated_at: <ISO-8601>
---

# Model capabilities

## Registry policy

- Use stable Model IDs in routing and task fields.
- Record the real product/version and assessment date.
- Reassess after a model, tool or policy change.
- Do not infer capability from brand prestige.

| Model ID | Real name/version | Tier | Tools | Max context | Vision | Navigation | Code quality | Architecture quality | Strengths | Limitations | Relative cost | Review policy | Assessed at |
|---|---|---|---|---:|---|---|---|---|---|---|---|---|---|
| MODEL-STRONG | <name/version> | STRONG | repo, terminal, web | <tokens> | YES | YES | HIGH | HIGH | architecture, adversarial reasoning | higher cost | HIGH | critical review | <ISO-8601> |
| MODEL-ECONOMY | <name/version> | ECONOMY | repo, terminal | <tokens> | NO | NO | MEDIUM | LOW | explicit deterministic wiring | ambiguity | LOW | sampled | <ISO-8601> |

## Review boundaries

| Policy | Executor tiers | Required reviewer tier | Review mode |
|---|---|---|---|
| Critical/security | ANY | STRONG | ADVERSARIAL_REVIEW |
| Medium-risk economy | ECONOMY | STRONG | REQUIRED_BEFORE_COMPLETE |
| Deterministic low-risk | ANY | NONE | NONE |
