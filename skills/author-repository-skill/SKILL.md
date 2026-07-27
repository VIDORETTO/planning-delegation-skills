---
name: author-repository-skill
description: Create, update, merge, split, or audit a skill in this repository while preserving its catalog, trigger boundaries, contracts, progressive disclosure, agents metadata, validation, tests, and platform-neutral core. Use for maintenance of this skill collection. Check for overlap before creating a new skill and prefer extending an existing owner when responsibilities match.
---

# Author Repository Skill

Maintain this repository's own skill collection: create a new skill, update an existing one, merge
overlapping skills, split an overgrown one, or audit the catalog for drift. This skill operates on
`skills/` itself, not on a product's `docs/ai/<slug>` workflow — it has no project stage, no
`PROGRESS.md`, and no place in the `skill-team/v3` pipeline diagram.

## Required resources

1. Read [references/skill-anatomy.md](references/skill-anatomy.md) before creating or restructuring a skill.
2. Read [references/overlap-and-boundaries.md](references/overlap-and-boundaries.md) before adding a new skill.
3. Read [references/contract-compliance.md](references/contract-compliance.md) before touching any skill that participates in `skill-team/v3`.
4. Use [assets/SKILL.template.md](assets/SKILL.template.md) for a new skill's frontmatter and body shape.
5. Use [assets/agents-openai.template.yaml](assets/agents-openai.template.yaml) for `agents/openai.yaml`.
6. Run [scripts/validate_skill.py](scripts/validate_skill.py) after every change, on every touched skill.

## When to use this skill

- Creating a brand-new skill for a capability not covered by an existing one.
- Updating an existing skill's method, references, assets, or contract fields.
- Merging two skills whose trigger boundaries have drifted into real overlap.
- Splitting one skill whose scope has grown into two or more distinct responsibilities.
- Auditing the catalog for stale `next_skill` references, missing agents metadata, broken local
  links, or hardcoded vendor names.

This skill does not decide product requirements or implement product code. It edits the skill
library that other skills, and other agents, read.

## Workflow

### 1. Check for overlap before creating anything new

Read every existing `SKILL.md` `description` field under `skills/`. A new skill is justified only
when no existing skill's trigger boundary already covers the need. When responsibilities partially
match, prefer extending the existing owner's method and references over adding a second skill that
competes for the same trigger. See
[references/overlap-and-boundaries.md](references/overlap-and-boundaries.md).

### 2. Respect the standard skill anatomy

Every skill under `skills/<skill-name>/` needs:

- `SKILL.md` with YAML frontmatter containing only `name` and `description` (kebab-case name matches
  the directory), 100–220 lines preferred, 500 lines maximum;
- `agents/openai.yaml` with `display_name`, `short_description`, and a `default_prompt` that names
  the skill and its stop condition;
- `references/` for material read conditionally, in English, with vendor-neutral file names and
  content (no hardcoded assistant brand names);
- `assets/` for templates the skill instantiates (`assets/` is the current convention for new
  skills; a few earlier skills still use `templates/` — do not rename those without an explicit
  migration task, since other documents may link to the old path);
- `scripts/validate_*.py`, stdlib only, exiting 0 on PASS and non-zero on FAIL, when the skill
  produces structured artifacts that benefit from automated validation.

See [references/skill-anatomy.md](references/skill-anatomy.md) for the full checklist and rationale.

### 3. Preserve contract compliance for pipeline skills

For a skill that participates in `skill-team/v3` (anything in the `DISCOVERY` → `PLANNING` →
`ROUTING` → `IMPLEMENTATION` → `REVIEW` → `RELEASE` pipeline), verify:

- it declares `workflow_contract: skill-team/v3` in the artifacts it writes;
- it uses `required_skill` / `successor_skill`, never `next_skill`;
- it treats `PROGRESS.md` as the sole operational pointer and `AGENTS.md` as discovery-only;
- it names its own exclusive stage ownership and states that it stops after that stage;
- it documents the single-writer protocol where it takes or releases `writer_skill`.

See [references/contract-compliance.md](references/contract-compliance.md) for the full list and for
how to handle a skill that intentionally predates `skill-team/v3` (do not silently rewrite another
skill's contract version as a side effect of an unrelated change).

### 4. Creating a new skill

1. Confirm no overlap (step 1).
2. Create the directory and the standard anatomy (step 2).
3. Write a `description` that states what to use it for and, in the same sentence or the next, what
   it explicitly does not do — this is what keeps trigger boundaries from drifting later.
4. Write the method body around evidence and verifiable stop conditions, not vague guidance.
5. Validate with [scripts/validate_skill.py](scripts/validate_skill.py).
6. Report the new skill's boundary against its nearest neighbors so the user can confirm no overlap
   was missed.

### 5. Updating an existing skill

Change the smallest section that fixes the actual problem. Do not rewrite an entire `SKILL.md` for a
localized fix. Re-run the validator afterward. If the update changes the skill's trigger boundary,
check every neighbor skill's `description` for now-stale exclusions or now-missing cross-references.

### 6. Merging two skills

Only when their actual responsibilities — not just their names — overlap. Preserve the more complete
reference material from both, keep whichever artifact contract already has downstream consumers, and
explicitly deprecate the removed skill's directory rather than silently deleting history the user may
still need (leave a short pointer file unless the user asks for a clean removal).

### 7. Splitting an overgrown skill

Split when a skill's `SKILL.md` has grown past the line budget because it is doing two genuinely
different jobs, not because it is thorough. Give each resulting skill its own trigger boundary and
its own exclusion list so they do not immediately re-overlap.

### 8. Auditing the catalog

Run [scripts/validate_skill.py](scripts/validate_skill.py) with `--all` across `skills/` and report:
skills missing `agents/openai.yaml`, skills still containing `next_skill` in new-style artifacts,
skills with broken local links, and skills whose `description` overlaps closely with another's.

## Output contract

Produce or update only the files of the skill(s) explicitly in scope for this operation. Report which
files were created or changed, the validator command and result for each touched skill, and any
overlap or boundary risk found along the way.

## Prohibitions

- Do not create a new skill that duplicates an existing trigger boundary without merging instead.
- Do not hardcode a specific assistant brand name into shared method text; keep skills portable
  across harnesses that read `SKILL.md`, `AGENTS.md`, and local scripts.
- Do not silently migrate another skill's contract version as a side effect of an unrelated request.
- Do not delete a skill's history without either explicit user instruction or a clear deprecation
  pointer.
- Do not implement product code as a side effect of skill maintenance.

## Additional local resources

- [references/skill-authoring-rules.md](references/skill-authoring-rules.md)
- [assets/SKILL-SCAFFOLD.template.md](assets/SKILL-SCAFFOLD.template.md)
- [scripts/validate_skill_authoring.py](scripts/validate_skill_authoring.py)
