# Agent discovery index

This repository is a portable collection of AI agent skills under `skill-team/v3`.

## Read first

1. `catalog/skills.json` — active skill catalog
2. `contracts/skill-team-v3.md` — operational contract
3. `PROGRESS.md` inside a consumer project at `docs/ai/<slug>/` — sole operational pointer when a workflow exists

Entry modes are raw/ambiguous intent (`brainstorm-idea-with-user`), existing-code change (`investigate-existing-codebase`), controlled UI audit (`product-ux-audit`), or a validated compact brief/discovery handoff (`create-spec-driven-plan`). Initialize a new discovery workflow with `scripts/init_workflow.py`; do not invent a ready handoff.

## Safety

- Do not invent workflow state.
- Do not ignore `required_skill` in `PROGRESS.md`.
- Only one writer skill at a time (`writer_skill`).
- Use only canonical paths under `docs/ai/<slug>/`; do not follow or create live v2 aliases.
- A ready handoff is immutable for its revision. Record consumption in `PROGRESS.md`; material changes require a new revision.
- Never store secrets, passwords, or real personal data in fixtures or examples.

## Maintaining this catalog

When creating or changing skills in this repository:

1. use `author-repository-skill`;
2. check overlap before adding a skill;
3. prefer extending an existing owner when responsibilities match;
4. edit only the skill in scope unless contracts require a coordinated update;
5. keep the portable core in `SKILL.md` / references / assets / scripts;
6. add or update validators and tests;
7. run `python scripts/validate_repository.py`; it validates catalog canonical paths, schema shape, instantiated handoff templates, strict workflow fixtures, and the full test suite;
8. do not add skill-local README files or unnecessary helpers.

Planning owns `plan/SPEC.md`, clarification records, requirement-quality checklists, and `plan/CONSISTENCY-REPORT.md`. Structural analysis failures block routing. Review classifies findings and returns work to the canonical owner without implementing a fix. Release readiness requires evidence for every passing or accepted-risk gate; a waived review requires explicit routing policy and `IMPLEMENTATION-TO-RELEASE.md`.

For legacy projects, run the dry-runnable migrator and use its hash-safe rollback rather than manually editing v2 state: `docs/migration/v3-strict-migration.md`.

## Platform adapters

Optional harness notes live under `adapters/`. Behavior must remain correct without them.
They are not sources of workflow truth and must not introduce platform-specific core behavior.
