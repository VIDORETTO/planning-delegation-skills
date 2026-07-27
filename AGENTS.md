# Agent discovery index

This repository is a portable collection of AI agent skills under `skill-team/v3`.

## Read first

1. `catalog/skills.json` — active skill catalog
2. `contracts/skill-team-v3.md` — operational contract
3. `PROGRESS.md` inside a consumer project at `docs/ai/<slug>/` — sole operational pointer when a workflow exists

## Safety

- Do not invent workflow state.
- Do not ignore `required_skill` in `PROGRESS.md`.
- Only one writer skill at a time (`writer_skill`).
- Never store secrets, passwords, or real personal data in fixtures or examples.

## Maintaining this catalog

When creating or changing skills in this repository:

1. use `author-repository-skill`;
2. check overlap before adding a skill;
3. prefer extending an existing owner when responsibilities match;
4. edit only the skill in scope unless contracts require a coordinated update;
5. keep the portable core in `SKILL.md` / references / assets / scripts;
6. add or update validators and tests;
7. run `python scripts/validate_repository.py`;
8. do not add skill-local README files or unnecessary helpers.

## Platform adapters

Optional harness notes live under `adapters/`. Behavior must remain correct without them.
