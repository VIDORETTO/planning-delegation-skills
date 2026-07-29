# Cursor CLI / IDE adapter

## Install

Copy skill folders into your Cursor skills location, or open this repository and reference
`skills/` directly. Confirm the current Cursor docs for user/project skill paths.

Example:

```powershell
Copy-Item .\skills\* "$env:USERPROFILE\.cursor\skills" -Recurse -Force
```

## Project instructions

Use root `AGENTS.md` as a discovery index. For product repos, keep a project `AGENTS.md` that
points to `docs/ai/<slug>/PROGRESS.md` without duplicating status.
Use the canonical `discovery/`, `plan/`, `routing/`, `execution/`, `review/`, `release/`, `blockers/`, `findings/`, and `handoffs/` paths below that root. `next_skill` and live v2 aliases are invalid.

## Models

Choose models in the Cursor UI or CLI flags. Routing decisions belong in
`routing/MODEL-CAPABILITIES.md` for the consumer project, not in skill source.

## Browser / UX audits

Prefer already available browser MCP tools. Do not install packages with
`--break-system-packages`.

## Validation

```bash
python scripts/validate_repository.py
```

## Core boundary

Cursor selection and browser tools do not change Skill Team's v3 behavior. Clarification, compact specification, checklists, and analysis remain planning substeps; review does not implement fixes; release requires recorded gate evidence. Migrate legacy projects with the portable dry run and hash-safe rollback rather than Cursor-specific files.
