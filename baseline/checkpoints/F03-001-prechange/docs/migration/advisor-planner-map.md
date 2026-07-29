# Migration map — `advisor-planner` to `skill-team/v3`

`advisor-planner` is a single, monolithic "advisor/planner" skill from `planning-delegation/v2`-era
usage: one strong model investigates, decides, and writes a Master Plan for a cheaper model to
execute. `skill-team/v3` splits that same responsibility across dedicated, contract-governed skills
with explicit stage ownership, evidence ledgers, and validators. This document maps each
`advisor-planner` section to its `skill-team/v3` successor. `skills/advisor-planner/` was removed
from the repository. This map is a historical migration record, not an exception that permits a live
v2 advisor/planner alias outside `scripts/migrate_v2_to_v3.py` and migration fixtures.

## Section-by-section mapping

| `advisor-planner` section | Successor skill | Notes |
|---|---|---|
| Passo 1 — Entrevista (os três modelos, escopo do problema) | `route-ai-work-by-capability` (model registration) + `create-spec-driven-plan` (scope/requirements interview, via `brainstorm-idea-with-user` when intent is undecided) | The three-tier model interview becomes `MODEL-CAPABILITIES.md` registration in routing; problem-scope questions belong to brainstorm/planning, not investigation. |
| Passo 2 — Investigação real do app | `investigate-existing-codebase` | Direct successor. See detailed mapping below. |
| `references/guia-de-investigacao.md` | `investigate-existing-codebase/references/investigation-method.md` and `references/evidence-and-impact-mapping.md` | Rewritten vendor-neutral, in English; split into "how to investigate" and "how to evidence/scope impact." |
| Passo 3 — Escrever o Plano Mestre | `create-spec-driven-plan` (out of scope for this migration pass — already exists) | The Master Plan's phases/tasks/checklist map to `create-spec-driven-plan`'s phases, tasks, and traceability; not re-authored here. |
| `references/guia-de-tarefas.md` (granularidade, autocontenção) | `execute-routed-task/references/task-self-containment.md` (self-containment, stop signals) + `create-spec-driven-plan` (task granularity/classification, out of scope here) | Only the self-containment and stop-signal guidance was absorbed into `execute-routed-task`; granularity/classification rubric belongs to planning, already covered by `create-spec-driven-plan`'s own method. |
| Passo 4 — Handoff (instruções para abrir sessão com modelo econômico) | `route-ai-work-by-capability` (`handoffs/ROUTING-TO-IMPLEMENTATION.md`, out of scope here) + `execute-routed-task` (session start/continue behavior) | The "how to open a session with the cheap model" instructions become the executor's own entry gate and workflow in `execute-routed-task`. |
| `references/execucao-modelo-economico.md` | `execute-routed-task/references/execution-loop.md` | Rewritten vendor-neutral, in English: session loop, never-do list, execution log format, and the note about not trusting the log blindly on a later revisit. |
| Modo revisão (plano parcialmente executado, reclassificar/atualizar/destravar) | `review-implementation-evidence` | Direct successor. See detailed mapping below. |
| Regras inegociáveis (não implementar tarefa difícil "de graça", nunca inventar evidência, nunca agrupar tarefas difíceis independentes, priorização) | Split: evidence rule → `investigate-existing-codebase`; scope/never-implement-what-you-review → `review-implementation-evidence`; batching rule → `route-ai-work-by-capability` (already exists, out of scope here) | These cross-cutting rules did not have one home in the monolithic skill; `skill-team/v3` places each rule with the skill that can actually enforce it via its own validator. |

## Detailed mapping: investigation

| `guia-de-investigacao.md` concept | `investigate-existing-codebase` location |
|---|---|
| Ordem de investigação (orientação geral, foco no problema, raio de impacto) | `references/investigation-method.md` §"Order of investigation" |
| Profundidade vs. amplitude | `references/investigation-method.md` §"Depth versus breadth" |
| Regra de evidência (`caminho/arquivo:linha`) | `references/evidence-and-impact-mapping.md` §"The evidence rule" + `assets/EVIDENCE.template.md` (now a structured, ID-based ledger instead of prose) |
| "Diga isso explicitamente" quando não é possível investigar | `references/evidence-and-impact-mapping.md` §"What belongs in assumptions instead of findings" |

## Detailed mapping: review mode

| `advisor-planner` "Modo revisão" step | `review-implementation-evidence` location |
|---|---|
| "Leia o Plano Mestre inteiro e o log de execução" | Entry gate + Method §1 ("Verify independently, do not just read the log") |
| "Investigue o estado real do código (não confie só no log)" | `references/independent-verification-method.md`, entire file |
| "Reclassifique tarefas cuja complexidade mudou" | Out of scope for review; belongs to `route-ai-work-by-capability` re-routing (`REROUTE_REQUIRED`) |
| "Marque como obsoleta qualquer tarefa... não apague silenciosamente" | `review-implementation-evidence` findings model: findings are recorded with a classification and status, never silently deleted |
| "Feche a resposta com um delta claro" | `assets/REVIEW-REPORT.md` template's "Findings summary" and "Outcome" sections |

## What did not migrate

- The three-tier "fácil/médio/difícil" model interview language is superseded by
  `route-ai-work-by-capability`'s rubric-based classification (hard gates + scored dimensions); it is
  not reproduced in the new skills.
- Portuguese-language method prose was not carried over verbatim; all new reference material is
  rewritten in English and vendor-neutral (no assistant brand names), per `skill-team/v3` vocabulary
  rules. User-facing reports produced by the new skills may still be written in the user's language.
- `advisor-planner`'s single-file "Plano Mestre" format is not reproduced; the new skills use the
  multi-document, per-stage artifact set already defined by `create-spec-driven-plan` and
  `route-ai-work-by-capability`.

## Status

`skills/advisor-planner/` is removed. This document records where its responsibilities live in
`skill-team/v3` for projects migrating from the v2 workflow.

For operational migration and recovery instructions, see [Strict v2 to v3 Migration](v3-strict-migration.md).
