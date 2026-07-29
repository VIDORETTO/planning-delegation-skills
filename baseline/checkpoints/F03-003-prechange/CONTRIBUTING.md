# Contributing

## Principles

- One responsibility per skill.
- Portable core first; adapters are optional.
- Deterministic validation with the Python standard library.
- No vendor model hardcoding in skills.
- No duplicate operational state outside `PROGRESS.md` in consumer projects.
- All new artifacts use only `workflow_contract: skill-team/v3`; v2 interpretation belongs only in the migrator and migration fixtures.
- Use canonical paths from `contracts/skill-team-v3.md`; do not add fallback aliases.

## Adding or changing a skill

1. Read `catalog/skills.json` and run overlap detection.
2. Follow `skills/author-repository-skill/SKILL.md`.
3. Keep `SKILL.md` concise; put rubrics in `references/`.
4. Put copyable templates in `assets/` (not `templates/`).
5. Provide `agents/openai.yaml`.
6. Add tests for validators and workflow contracts.
7. Update the catalog and verify README/catalog consistency.
8. Preserve stage boundaries: clarification, `SPEC.md`, checklists, and consistency analysis are planning substeps; routing assigns work but does not edit plan semantics; review does not fix code.

## Validation

```bash
python scripts/validate_repository.py
```

This is the complete required repository gate. It runs schema checks, instantiated templates, strict valid and invalid fixtures, catalog and resource checks, and the complete `unittest` suite. Documentation examples must use canonical paths and commands that this repository supports.

## Migration and rollback

Use `python scripts/migrate_v2_to_v3.py <workflow-root> --dry-run --json` before migration. Do not manually retain v2 aliases such as `next_skill`. The migrator creates a hash-checked backup and supports `--rollback`; see `docs/migration/v3-strict-migration.md`. Do not overwrite a migrated pointer or user artifacts to force a rollback.

## Adapters and attribution

Adapters under `adapters/` are optional installation guidance only. They must not change the portable Markdown, flat-frontmatter, Python-standard-library core or duplicate live workflow state. Specification-quality concepts are inspired by GitHub Spec Kit; do not add it as a dependency or copy its CLI/workflow engine.

## Commits

Prefer small commits by responsibility: contract, catalog, discovery, planning, routing, execution, review/release, UX cleanup, CI, docs, legacy removal.
