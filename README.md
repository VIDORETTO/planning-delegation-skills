# Agent Skills Collection (`skill-team/v3`)

Portable AI agent skills that work as a coordinated team: discovery → planning → routing →
execution → review → release readiness.

Contract: [`contracts/skill-team-v3.md`](contracts/skill-team-v3.md)  
Catalog: [`catalog/skills.json`](catalog/skills.json)

## Principles

- Specification before implementation
- One operational pointer: `docs/ai/<slug>/PROGRESS.md`
- `required_skill` is unambiguous; no silent stage jumping
- One writer at a time
- Model-agnostic routing via project-local registries
- Deterministic validators using Python stdlib only
- Platform-neutral core; adapters are optional

## Catalog

| Skill | Category | Responsibility |
|---|---|---|
| [`brainstorm-idea-with-user`](skills/brainstorm-idea-with-user/) | discovery | Mature ambiguous product intent |
| [`investigate-existing-codebase`](skills/investigate-existing-codebase/) | discovery | Evidence-based technical investigation |
| [`product-ux-audit`](skills/product-ux-audit/) | product | Audit rendered UI/UX |
| [`create-spec-driven-plan`](skills/create-spec-driven-plan/) | planning | Build executable plans with profiles |
| [`route-ai-work-by-capability`](skills/route-ai-work-by-capability/) | orchestration | Assign models and reviewers |
| [`execute-routed-task`](skills/execute-routed-task/) | execution | Implement authorized tasks |
| [`review-implementation-evidence`](skills/review-implementation-evidence/) | quality | Independent review |
| [`validate-release-readiness`](skills/validate-release-readiness/) | release | Release gate decision |
| [`author-repository-skill`](skills/author-repository-skill/) | maintenance | Maintain this catalog |

`advisor-planner` is absorbed and pending removal. See [`docs/migration/advisor-planner-map.md`](docs/migration/advisor-planner-map.md).

## Main flow

```text
Discovery (brainstorm | investigate | ux-audit)
→ create-spec-driven-plan
→ route-ai-work-by-capability
→ execute-routed-task
→ review-implementation-evidence (when required)
→ validate-release-readiness
```

Skills also work standalone when only one capability is needed.

## Quick start

```bash
git clone https://github.com/VIDORETTO/planning-delegation-skills.git
cd planning-delegation-skills
python scripts/validate_repository.py
```

Install skills into your harness using the adapter notes:

- [Codex](adapters/codex/README.md)
- [OpenCode](adapters/opencode/README.md)
- [Cursor](adapters/cursor/README.md)

## Validation

```bash
python scripts/validate_repository.py
python skills/brainstorm-idea-with-user/scripts/validate_brainstorm.py docs/ai/<slug>
python skills/create-spec-driven-plan/scripts/validate_plan.py docs/ai/<slug>
python skills/route-ai-work-by-capability/scripts/validate_routing.py docs/ai/<slug>
```

## Compatibility

Predecessor contract: `planning-delegation/v2`  
Migrator: `python scripts/migrate_v2_to_v3.py docs/ai/<slug> [--dry-run]`

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and use `author-repository-skill` before adding skills.
Check overlap, prefer extending an existing owner, and keep adapters out of the skill core.

## Security

See [`SECURITY.md`](SECURITY.md). No secrets in fixtures. No global package-break installs.
