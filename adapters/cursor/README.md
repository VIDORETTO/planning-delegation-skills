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
