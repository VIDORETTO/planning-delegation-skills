# Codex CLI adapter

Portable skills live under `skills/`. This adapter only explains how to expose them to Codex.

## Install skills

Copy or symlink desired skill folders into the Codex skills directory:

```bash
cp -R skills/brainstorm-idea-with-user "${CODEX_HOME:-$HOME/.codex}/skills/"
```

PowerShell:

```powershell
$skillsHome = if ($env:CODEX_HOME) { "$env:CODEX_HOME\skills" } else { "$env:USERPROFILE\.codex\skills" }
Copy-Item .\skills\* $skillsHome -Recurse -Force
```

Confirm the current Codex documentation for the exact skills discovery path before installing.

## AGENTS.md

Point the project `AGENTS.md` at the consumer workflow root and instruct agents to read
`docs/ai/<slug>/PROGRESS.md` first. Do not duplicate queues or status into `AGENTS.md`.

## Models

Register real Model IDs in each project's `routing/MODEL-CAPABILITIES.md`. Do not hardcode
brand names in the skill core.

## Validation

```bash
python scripts/validate_repository.py
python skills/create-spec-driven-plan/scripts/validate_plan.py docs/ai/<slug>
python skills/route-ai-work-by-capability/scripts/validate_routing.py docs/ai/<slug>
```

## Continue a workflow

Ask the agent to read `PROGRESS.md` and execute only `required_skill`.
