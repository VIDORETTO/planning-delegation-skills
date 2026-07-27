# Overlap and boundaries

## Why boundaries matter more than coverage

Two skills that can both plausibly answer the same request are worse than one skill that covers
slightly less — the agent choosing between them has no reliable signal, and the user gets
inconsistent behavior depending on which one happened to match. Every skill's `description` should
make its boundary, not just its coverage, legible.

## Checking for overlap before creating a new skill

1. Read every existing `SKILL.md` `description` under `skills/`.
2. For the new capability, ask: does an existing skill's trigger already cover this, even partially?
3. If yes, prefer extending that skill's method/references over adding a second skill. A new skill is
   justified when the responsibility is genuinely distinct — different inputs, different artifacts,
   different stop condition — not merely "this could also live here."

## Known boundaries in this catalog (do not blur these)

| Skill | Owns | Explicitly excludes |
|---|---|---|
| `brainstorm-idea-with-user` | New product/feature intent, undecided product questions | Formal planning, codebase reading as the primary evidence source, implementation |
| `investigate-existing-codebase` | Technical evidence: architecture, root cause, change impact | Product-intent decisions, the formal plan, model routing, rendered UX audit |
| `product-ux-audit` | Rendered visual/UI/UX inspection of a live product | Backend logic, performance, data correctness, static code reading as a substitute for a rendered screen |
| `create-spec-driven-plan` | Formal requirements, contracts, phases, tasks, traceability | Routing to models, implementation |
| `route-ai-work-by-capability` | Model assignment, batching, switch checkpoints | Planning, implementation |
| `execute-routed-task` | Implementing one routed task/batch | Planning, routing, reviewing its own work, release |
| `review-implementation-evidence` | Independent verification of completed work | Implementing the fix it finds, release decision |
| `validate-release-readiness` | Evidence-backed release decision | Deploying, implementing missing work |
| `author-repository-skill` | Maintaining the skill catalog itself | Product requirements, product implementation |

## Signs of drift to catch during an audit

- Two skills whose descriptions both claim a phrase like "use when the user asks to investigate…"
  without a distinguishing clause.
- A skill's method section quietly grows to include a step that belongs to a neighbor (for example,
  an execution skill starting to write acceptance criteria that belong to planning).
- A new reference file duplicating guidance already owned by another skill's reference, rather than
  linking to it or, if genuinely shared, promoting it to a place both can reference.

## Merging versus keeping separate

Merge when both skills would need to load the same context to do their job and the split adds
handoff overhead without adding a real trigger distinction. Keep separate when the inputs, artifacts,
or stop conditions genuinely differ, even if the skills are invoked back-to-back in the same
pipeline — the pipeline stages in `skill-team/v3` are separate skills precisely because each has its
own exclusive ownership and stop condition.
