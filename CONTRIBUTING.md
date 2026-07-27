# Contributing

## Principles

- One responsibility per skill.
- Portable core first; adapters are optional.
- Deterministic validation with the Python standard library.
- No vendor model hardcoding in skills.
- No duplicate operational state outside `PROGRESS.md` in consumer projects.

## Adding or changing a skill

1. Read `catalog/skills.json` and run overlap detection.
2. Follow `skills/author-repository-skill/SKILL.md`.
3. Keep `SKILL.md` concise; put rubrics in `references/`.
4. Put copyable templates in `assets/` (not `templates/`).
5. Provide `agents/openai.yaml`.
6. Add tests for validators and workflow contracts.
7. Update the catalog and verify README/catalog consistency.

## Validation

```bash
python scripts/validate_repository.py
```

## Commits

Prefer small commits by responsibility: contract, catalog, discovery, planning, routing, execution, review/release, UX cleanup, CI, docs, legacy removal.
