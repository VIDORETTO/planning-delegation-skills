---
name: brainstorm-idea-with-user
description: >
  Mature a new or ambiguous product, feature, automation, or research idea before formal
  planning. Use when the user needs questions, alternatives, scope discovery, actors,
  business rules, risks, success criteria, or preservation of decisions and rejected options.
  Resume only when the active workflow requires this skill. Do not use for technical codebase
  diagnosis, formal implementation planning, model routing, or implementation.
---

# Collaborative Product Brainstorm

Transform an initial idea into a mature, traceable product brief. Preserve the user's intent and
decision authority while contributing alternatives and trade-offs. The output is a validated
brainstorm package, not a formal implementation plan.

## Workflow contract

This skill participates in `skill-team/v3`:

```text
brainstorm-idea-with-user
→ create-spec-driven-plan
→ route-ai-work-by-capability
→ execute-routed-task
→ review-implementation-evidence (when required)
→ validate-release-readiness
```

Shared workflow root:

```text
docs/ai/<project-slug>/
├── PROGRESS.md
├── CONTEXT-INDEX.md
├── SOURCE-REGISTER.md
├── GLOSSARY.md
├── discovery/brainstorm/
│   └── BRAINSTORM.md
└── handoffs/
    └── BRAINSTORM-TO-PLAN.md
```

`PROGRESS.md` is the only operational pointer. `AGENTS.md` is discovery-only.
`BRAINSTORM.md` is the detailed source of truth for this stage.

## Exclusive stage ownership

Write only `discovery/brainstorm/`, this skill's handoff, and discovery fields in `PROGRESS.md`.
Do not invoke the next skill in the same operation. When ready:

1. validate artifacts;
2. generate `handoffs/BRAINSTORM-TO-PLAN.md`;
3. update `PROGRESS.md`;
4. set `required_skill: create-spec-driven-plan` and `successor_skill` as needed;
5. stop.

Resume only when `PROGRESS.md` exists and `required_skill` equals `brainstorm-idea-with-user`.
If no workflow exists and "continue" is ambiguous, ask for the path or identify the active
artifact without inventing state.

## Entry gate

Reading order: `PROGRESS.md` → `active_artifact` → current handoff → linked docs.

| Situation | Action |
|---|---|
| No workflow for a new idea | Create as `BRAINSTORM_IN_PROGRESS` |
| `required_skill: brainstorm-idea-with-user` and compatible status | Resume without repeating answered questions |
| Product-intent change requiring rediscovery | Record reason and resume brainstorm |
| Any other required skill | Stop without modifying artifacts |

Initialize new workflows with profile `compact` or `standard` as appropriate:

```yaml
workflow_contract: skill-team/v3
project_id: <project-id>
project_slug: <project-slug>
workflow_profile: standard
stage: DISCOVERY
status: BRAINSTORM_IN_PROGRESS
stage_owner: brainstorm-idea-with-user
required_skill: brainstorm-idea-with-user
successor_skill: create-spec-driven-plan
handoff_status: NOT_READY
discovery_revision: 1
plan_revision: 0
routing_revision: 0
implementation_revision: 0
review_revision: 0
release_revision: 0
active_artifact: docs/ai/<slug>/discovery/brainstorm/BRAINSTORM.md
active_task: null
active_batch: null
active_executor_model: null
active_reviewer_model: null
writer_skill: brainstorm-idea-with-user
writer_task: null
next_action: Answer pending structural questions
blockers: NONE
last_validation_command: NONE
last_validation_result: NOT_RUN
updated_at: <ISO-8601>
```

Use [assets/PROGRESS.template.md](assets/PROGRESS.template.md).

## Method

### 1. Capture and identify

Store the user's first description verbatim under original idea. Assign stable project ID and
kebab-case slug. Classify as new product, feature, automation, or research.

### 2. Diagnose gaps

Prioritize problem/outcome, actors/permissions/journeys, first usable release and non-goals,
business rules and data lifecycle, critical integrations, success metrics, prohibited outcomes,
and major risks. Use [references/interview-strategy.md](references/interview-strategy.md) as a
question bank, not a fixed questionnaire.

### 3. Interview in short rounds

Ask a few focused questions per round. Do not repeat answers already in artifacts. Prefer
concrete alternatives when useful. Update artifacts after each material response. There is no
arbitrary maximum number of rounds — stop when structural gaps are closed.

### 4. Reflect and suggest

Challenge complexity and hidden assumptions. Record rejected options with IDs. Do not re-propose
rejected options unless new evidence changes the trade-off.

### 5. Maintain stable records

Assign IDs once (`ACT-*`, `DEC-*`, `Q-*`, `ASM-*`, `RISK-*`, `BR-*`, `JRN-*`, `CR-*`, `REJ-*`,
`SRC-*`). Never renumber. Increment `discovery_revision` on material changes. Keep revision sync
across `BRAINSTORM.md`, `PROGRESS.md`, and the handoff.

Maintain `SOURCE-REGISTER.md`, optional `GLOSSARY.md`, and `CONTEXT-INDEX.md`. External research
is allowed only when it can change the product; record authority, date, and validity.

### 6. Keep documentation compact

Start with one `BRAINSTORM.md`. Extract topics only when dense. See
[references/scope-and-readiness.md](references/scope-and-readiness.md).

### 7. Evaluate readiness

Ready only when problem, actors, MVP, non-goals, structural constraints, critical integrations,
and primary success measures are clear; structural questions are closed or explicitly delegated;
assumptions/risks are visible; handoff validates.

### 8. Handoff and stop

Build `BRAINSTORM-TO-PLAN.md`. Structural open questions must be `NONE` for a ready handoff.
Run:

```bash
python skills/brainstorm-idea-with-user/scripts/validate_brainstorm.py docs/ai/<slug>
```

On PASS set `status: DISCOVERY_READY`, `required_skill: create-spec-driven-plan`,
`handoff_status: READY`, `writer_skill: null`, and stop.

## Change-control re-entry

- Intent/audience/problem/outcome changed → this skill.
- Structural implementation change without intent change → planning owns it.
- Local implementation detail → do not reopen brainstorm.

## Required resources

| File | Use |
|---|---|
| `references/interview-strategy.md` | Next interview round |
| `references/source-authority.md` | Source authority rules |
| `references/scope-and-readiness.md` | Compact docs and readiness |
| `assets/BRAINSTORM.template.md` | Create `BRAINSTORM.md` |
| `assets/PROGRESS.template.md` | Initialize shared state |
| `assets/BRAINSTORM-TO-PLAN.template.md` | Handoff |
| `assets/AGENTS.template.md` | Discovery-only index |
| `assets/SOURCE-REGISTER.template.md` | Source register |
| `assets/CONTEXT-INDEX.template.md` | Document index |
| `assets/GLOSSARY.template.md` | Glossary |

## Prohibitions

- Do not diagnose code root cause, formalize implementation tasks, choose models, or implement.
- Do not use `AGENTS.md` as status.
- Do not silently decide structural questions.
- Do not turn rejected suggestions into requirements.
- Do not mark ready with placeholders, broken links, or open structural questions.
