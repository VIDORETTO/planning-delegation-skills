# Workflow Initialization

Create an empty strict v3 discovery workflow with:

```text
python scripts/init_workflow.py --root <repository-root> --project-id <stable-id> --project-slug <kebab-slug> --profile <compact|standard|critical> --discovery <brainstorm|codebase|ux> [--dry-run] [--timestamp <ISO-8601-UTC>]
```

The command prints one sorted JSON object on stdout. It creates `docs/ai/<slug>/` only after the generated files pass strict initial-state validation. It refuses an existing target with `STV3-E025-SCOPE`, rejects unsafe symlinks or path values, and reports invalid command usage or I/O failures as `STV3-E030-INTERNAL` with exit code 2.

`--dry-run` performs the same validation but leaves no workflow or temporary directory. The optional timestamp is for reproducible output; otherwise it uses current UTC.

The selected discovery mode creates its canonical starting artifact(s), common source/context/glossary files, and `PROGRESS.md`. It intentionally creates no handoff because discovery is not ready.
