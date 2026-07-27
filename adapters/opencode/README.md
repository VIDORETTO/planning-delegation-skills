# OpenCode adapter

The skill core is harness-agnostic. Use this adapter only to wire discovery paths.

## Install

Follow current OpenCode documentation for skill or instruction directories. Typically:

1. copy `skills/<name>` into the OpenCode skills location used by your setup;
2. ensure `AGENTS.md` or equivalent project instructions are visible to the agent;
3. keep validators runnable with local Python 3.10+.

## Workflow continuity

OpenCode sessions should open `docs/ai/<slug>/PROGRESS.md` and honor `required_skill`.
Do not store live status in platform-specific files.

## Permissions

Restrict write access according to the active skill ownership table in
`contracts/skill-team-v3.md`. Prefer read-only exploration for investigation and review.

## Validation

```bash
python scripts/validate_repository.py
```
