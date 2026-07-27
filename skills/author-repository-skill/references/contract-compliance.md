# Contract compliance for pipeline skills

Applies to any skill that participates in the `skill-team/v3` pipeline
(`DISCOVERY → PLANNING → ROUTING → IMPLEMENTATION → REVIEW → RELEASE`). This skill itself
(`author-repository-skill`) does not participate in that pipeline and is exempt from these checks.

## Checklist when creating or updating a pipeline skill

- Declares `workflow_contract: skill-team/v3` in every artifact frontmatter it writes.
- Uses `required_skill` (who may act now) and `successor_skill` (who is expected next once validated)
  — never `next_skill`. `next_skill` is legacy vocabulary; it may only appear inside a migrator that
  maps it once into the two new fields.
- Treats `docs/ai/<project-slug>/PROGRESS.md` as the sole operational pointer for that project. No
  other document, including `AGENTS.md`, should duplicate current status, active task, or active
  model.
- Documents `AGENTS.md` as discovery-only: a fixed set of read-first instructions, never a place to
  write current progress.
- States its own exclusive stage ownership and an explicit instruction to stop after that stage — no
  pipeline skill should silently invoke the next one in the same operation.
- Documents how it interacts with `writer_skill` / `writer_task` under the single-writer protocol:
  when it takes the lock, when it releases it, and what it does if the lock is already held by
  another skill or task.
- Documents its entry gate as a table of allowed incoming statuses, and what it does when the current
  state belongs to another skill (report the required skill, do not modify that skill's artifacts).
- Documents its handoff(s) using the contract's generic handoff frontmatter
  (`handoff_type`, `producer_skill`, `consumer_skill`, `input_revision`, `output_revision`,
  `handoff_status`, `validation_command`, `validation_result`, `generated_at`) and body sections
  (identification, summary, artifact inventory, preserved decisions, allowed open questions,
  blockers, consumer write scope, forbidden files, commands/results, stop instruction).
- Uses English for IDs, states, and schema field values. User-facing prose inside a report may be in
  the user's language; the contract vocabulary itself (statuses, finding classifications, task
  states) stays in English so validators and other skills can parse it.

## Handling a skill that predates skill-team/v3

Some skills in this repository (for example the routing and planning skills at the time this skill
was authored) still declare an earlier contract version and use `next_skill`/`active_skill`. Do not
rewrite another skill's contract version as an incidental part of an unrelated change — that is a
dedicated migration task with its own scope, its own validation, and its own review. When asked to
touch such a skill for an unrelated fix, make the smallest change that fixes the actual request and
leave its declared contract version alone unless the user explicitly asked for the migration.

## Validating contract compliance

[scripts/validate_skill.py](../scripts/validate_skill.py) checks, per skill: presence of
`agents/openai.yaml`, frontmatter shape, absence of `next_skill` as a literal field key in the
skill's own reference/asset templates (a skill may still *mention* the word while explaining the
migration), and that local links resolve. It does not simulate a live `docs/ai/<slug>` run; use each
pipeline skill's own `validate_<stage>.py` against a real project directory for that.
