---
name: brainstorm-idea-with-user
description: >
  Use whenever the user brings a new project or feature idea and the objective is to understand,
  challenge and mature what should be built before formal planning. Conduct short interview rounds,
  preserve the original idea, decisions, rejected suggestions, assumptions, risks and stable IDs,
  maintain the planning-delegation/v2 workflow state, and produce a validated handoff for a later
  invocation of create-spec-driven-plan. Also use to resume BRAINSTORM_IN_PROGRESS or
  REBRAINSTORM_REQUIRED. Never perform planning, routing or implementation in this skill.
---

# Collaborative Product Brainstorm

Transform an initial idea into a mature, traceable product brief. Preserve the user's intent and
decision authority while contributing alternatives and trade-offs. The output is a validated
brainstorm package, not a formal implementation plan.

## Workflow contract

This skill participates in `planning-delegation/v2`:

```text
brainstorm-idea-with-user
→ create-spec-driven-plan
→ route-ai-work-by-capability
→ implementation
```

Use one shared workflow root from the first brainstorm onward:

```text
docs/ai/<project-slug>/
├── PROGRESS.md
├── CONTEXT-INDEX.md
├── SOURCE-REGISTER.md
├── GLOSSARY.md
├── brainstorm/
│   ├── BRAINSTORM.md
│   └── topics/
└── handoffs/
    └── BRAINSTORM-TO-PLAN.md
```

`PROGRESS.md` is the only operational pointer. `AGENTS.md` is only a discovery index.
`BRAINSTORM.md` is the detailed source of truth for this stage.

## Exclusive stage ownership

Execute only the brainstorm stage. Do not invoke, execute or mix the next skill in the same
operation. When the brainstorm is ready:

1. validate the artifacts;
2. generate `handoffs/BRAINSTORM-TO-PLAN.md`;
3. update `PROGRESS.md`;
4. set `next_skill: create-spec-driven-plan`;
5. stop.

If the current state belongs to another skill, do not modify its artifacts. Report the skill named
by `next_skill`. Never plan tasks, route models or implement code here.

## Entry gate

Before asking questions or writing files, discover the project workflow through `AGENTS.md`, then
read `docs/ai/<slug>/PROGRESS.md`. Reading order:

1. `PROGRESS.md`;
2. `active_artifact`;
3. the current-stage handoff, if any;
4. documents linked by those files.

Allowed entry conditions:

| Situation | Required action |
|---|---|
| No workflow exists for a new idea | Create it as `BRAINSTORM_IN_PROGRESS` |
| `status: BRAINSTORM_IN_PROGRESS` and `active_skill: brainstorm-idea-with-user` | Resume without repeating answered questions |
| `status: REBRAINSTORM_REQUIRED` and `next_skill: brainstorm-idea-with-user` | Record the reason and transition to `BRAINSTORM_IN_PROGRESS` |
| Any other status owned by another skill | Stop without modifying artifacts |

For a new workflow initialize:

```yaml
workflow_contract: planning-delegation/v2
stage: BRAINSTORM
status: BRAINSTORM_IN_PROGRESS
active_skill: brainstorm-idea-with-user
next_skill: create-spec-driven-plan
handoff_status: NOT_READY
brainstorm_revision: 1
plan_revision: 0
routing_revision: 0
plan_based_on_brainstorm_revision: null
routing_based_on_plan_revision: null
active_artifact: docs/ai/<slug>/brainstorm/BRAINSTORM.md
```

Use `templates/progress-template.md`. Preserve unknown frontmatter keys owned by the wider workflow.

## Method

### 1. Capture and identify

Store the user's first description as close to verbatim as possible in `## Ideia original`. Never
rewrite that section later. Assign a stable project ID and kebab-case slug. Classify the work as
new product, feature, automation or research.

### 2. Diagnose gaps

Determine what is already answered and what could materially change the solution. Prioritize:

- problem and desired outcome;
- actors, permissions and journeys;
- first usable release and explicit non-goals;
- business rules and data lifecycle;
- critical integrations and structural constraints;
- success metrics, prohibited outcomes and major risks.

Use `references/roteiro-de-entrevista.md` as a question bank, not a fixed questionnaire.

### 3. Interview in short rounds

- Ask at most two or three questions per round.
- Do not repeat answers already present in the active artifacts.
- Prefer concrete alternatives when useful, but allow genuinely open answers.
- Wait for the response before continuing.
- After each material response, update the artifacts before the next round.

### 4. Reflect and suggest

Challenge complexity, hidden assumptions and premature scope. Offer simpler or more robust
alternatives with concise trade-offs. The user retains final decision authority. Once rejected, do
not re-propose an option unless new evidence changes the trade-off; record it under `Sugestões
recusadas`.

### 5. Maintain stable records

Use `templates/brainstorm-state-template.md`. Assign IDs once and never renumber them:

| Entity | Prefix |
|---|---|
| Decision | `DEC-001` |
| Open question | `Q-001` |
| Assumption | `ASM-001` |
| Risk | `RISK-001` |
| Business rule | `BR-001` |
| Journey | `JRN-001` |
| Candidate requirement | `CR-001` |
| Source | `SRC-001` |

Increment `brainstorm_revision` whenever a material decision, scope boundary, assumption, rule,
requirement or handoff changes. Keep the revision in `BRAINSTORM.md`, `PROGRESS.md` and the handoff
synchronized.

Create or maintain:

- `SOURCE-REGISTER.md`: source, type, authority, date/version, claims and validity;
- `GLOSSARY.md`: project-specific meanings;
- `CONTEXT-INDEX.md`: links to active documents, without duplicating status;
- `AGENTS.md`: discovery pointer only, using its template.

### 6. Keep documentation compact

Start with one `brainstorm/BRAINSTORM.md`. Extract a topic only when it exceeds roughly 40–50
lines, has been renegotiated at least three times, or is too technically dense. Put it in
`brainstorm/topics/<topic>.md` and leave a short summary plus link in the main file. Never create a
file per session. See `references/organizacao-de-pasta.md`.

### 7. Evaluate planning readiness

The brainstorm can become ready only when:

- the problem, actors, MVP and non-goals are clear;
- structural constraints and critical integrations are recorded;
- primary success measures are known;
- every structural question is closed or explicitly delegated;
- active assumptions and risks are visible;
- all readiness checkboxes are complete;
- the handoff is generated and passes validation.

Minor questions may remain only when they can be resolved during planning without changing product
intent, MVP, actor model, architecture class, core data model or critical integration.

### 8. Produce the handoff and stop

Build `handoffs/BRAINSTORM-TO-PLAN.md` from its template. Its `Questões estruturais` section must
explicitly say `Nenhuma.` for a ready handoff. Preserve rejected suggestions and all IDs. The next
skill must convert each `CR-*` to a formal requirement without losing origin.

Run:

```bash
python brainstorm-idea-with-user/scripts/validate_brainstorm.py docs/ai/<slug>
```

Only after it passes, set:

```yaml
stage: BRAINSTORM
status: BRAINSTORM_READY
active_skill: brainstorm-idea-with-user
next_skill: create-spec-driven-plan
handoff_status: READY
last_validation:
  command: python brainstorm-idea-with-user/scripts/validate_brainstorm.py docs/ai/<slug>
  result: PASS
```

If validation fails, remain `BRAINSTORM_IN_PROGRESS`, set `handoff_status: NOT_READY`, correct only
brainstorm-owned artifacts and rerun. Do not invoke `create-spec-driven-plan`; tell the user that it
is the next separate invocation.

## Change-control re-entry

- Product intent changed (audience, core problem or primary outcome): accept
  `REBRAINSTORM_REQUIRED`, record the cause and re-open the relevant questions.
- Structural implementation change without product-intent change: ownership remains with
  `create-spec-driven-plan`; do not edit its documents.
- Small implementation detail: do not reopen brainstorm.

## Required references and assets

| File | Use |
|---|---|
| `references/roteiro-de-entrevista.md` | Select the next short interview round |
| `references/organizacao-de-pasta.md` | Decide when to extract topics |
| `templates/brainstorm-state-template.md` | Create `BRAINSTORM.md` |
| `templates/progress-template.md` | Initialize shared workflow state |
| `templates/brainstorm-to-plan-handoff-template.md` | Produce the validated handoff |
| `templates/agents-md-snippet-template.md` | Create the discovery-only project index |
| `templates/source-register-template.md` | Record source authority and validity |
| `templates/context-index-template.md` | Create the non-operational document index |
| `templates/glossary-template.md` | Define project-specific terminology |

## Prohibitions

- Do not invoke another skill in the same operation.
- Do not use `AGENTS.md` as a status source.
- Do not silently decide structural questions for the user; mark delegated decisions explicitly.
- Do not turn rejected suggestions into requirements.
- Do not create chronological session files.
- Do not mark ready with placeholders, missing local links or structural questions open.
