# skill-team/v3

Operational contract for the coordinated skill team in this repository.

Supersedes `planning-delegation/v2`. Do not extend v2 rules inside new skills.
Use `scripts/migrate_v2_to_v3.py` for legacy project migration.

## Goals

- Portable across Codex CLI, OpenCode, Cursor CLI, and other harnesses that read `SKILL.md`, `AGENTS.md`, Markdown, and local scripts.
- One operational pointer: `docs/ai/<project-slug>/PROGRESS.md`.
- One writer at a time.
- Explicit stage ownership, handoffs, revisions, and deterministic validators.
- Model-agnostic routing via project-local `MODEL-CAPABILITIES.md`.
- Discovery modes that do not compete: brainstorm, codebase investigation, UX audit.

## Pipeline

```text
Discovery (brainstorm | investigate | ux-audit)
→ create-spec-driven-plan
→ route-ai-work-by-capability
→ execute-routed-task
→ review-implementation-evidence (when required)
→ validate-release-readiness
```

No skill silently executes the next stage in the same invocation. Each skill:

1. completes its own stage;
2. validates artifacts;
3. updates the operational pointer;
4. sets `required_skill` / `successor_skill`;
5. stops.

## Canonical PROGRESS.md fields

Flat YAML frontmatter only (stdlib-parseable). Body is a short human view regenerated from frontmatter.

| Field | Meaning |
|---|---|
| `workflow_contract` | Must be `skill-team/v3` |
| `project_id` | Stable project ID |
| `project_slug` | Directory slug under `docs/ai/` |
| `workflow_profile` | `compact` \| `standard` \| `critical` |
| `stage` | Logical stage |
| `status` | Precise stage condition |
| `stage_owner` | Skill that owns stage artifacts |
| `required_skill` | Only skill that may run now |
| `successor_skill` | Expected skill after validated completion |
| `handoff_status` | `NOT_READY` \| `READY` \| `CONSUMED` |
| `*_revision` | Monotonic integers per stage family |
| `active_artifact` | First document the next session must read |
| `active_task` | Current task ID or `null` |
| `active_batch` | Current batch ID or `null` |
| `active_executor_model` | Registered Model ID or `null` |
| `active_reviewer_model` | Registered Model ID or `null` |
| `writer_skill` | Skill currently authorized to write |
| `writer_task` | Task ID with write lock or `null` |
| `next_action` | Short human instruction |
| `blockers` | `NONE` or concise blocker text |
| `last_validation_command` | Last validator command |
| `last_validation_result` | `PASS` \| `FAIL` \| `NOT_RUN` |
| `updated_at` | ISO-8601 timestamp |

`required_skill` replaces ambiguous `next_skill`.

`next_skill` is forbidden in new artifacts. Migrators may map it once into `required_skill` and `successor_skill`.

## Stages

| Stage | Owners |
|---|---|
| `DISCOVERY` | `brainstorm-idea-with-user`, `investigate-existing-codebase`, `product-ux-audit` |
| `PLANNING` | `create-spec-driven-plan` |
| `ROUTING` | `route-ai-work-by-capability` |
| `IMPLEMENTATION` | `execute-routed-task` |
| `REVIEW` | `review-implementation-evidence` |
| `RELEASE` | `validate-release-readiness` |

## Allowed statuses

### Discovery

- `BRAINSTORM_IN_PROGRESS`
- `CODEBASE_INVESTIGATION_IN_PROGRESS`
- `UX_AUDIT_IN_PROGRESS`
- `DISCOVERY_READY`
- `DISCOVERY_BLOCKED`

### Planning

- `PLAN_IN_PROGRESS`
- `PLAN_VALIDATED`
- `REPLAN_REQUIRED`

### Routing

- `ROUTING_IN_PROGRESS`
- `IMPLEMENTATION_READY`
- `REROUTE_REQUIRED`

### Implementation

- `TASK_IN_PROGRESS`
- `TASK_BLOCKED`
- `TASK_COMPLETE`
- `IMPLEMENTATION_COMPLETE`

### Review

- `REVIEW_REQUIRED`
- `REVIEW_IN_PROGRESS`
- `CHANGES_REQUIRED`
- `REVIEW_APPROVED`

### Release

- `RELEASE_REVIEW_REQUIRED`
- `RELEASE_BLOCKED`
- `RELEASE_READY`
- `RELEASED`
- `POST_RELEASE_REVIEW_REQUIRED`

## Transition rules

Every transition must verify:

1. allowed entry status;
2. matching `required_skill`;
3. handoff revision freshness;
4. previous-stage validation `PASS` when consuming a READY handoff;
5. no conflicting writer (`writer_skill` / `writer_task`);
6. `active_artifact` exists;
7. local links resolve;
8. no placeholders in documents marked ready.

## Profiles

| Profile | Use | Artifact density |
|---|---|---|
| `compact` | Bounded bug or small change | Minimum set |
| `standard` | Medium feature/project | Intermediate set |
| `critical` | Security, data, migration, architecture, regulated | Full controls |

Profiles never weaken security gates. They omit irrelevant documents only.

## Handoff contract

Every handoff frontmatter:

```yaml
workflow_contract: skill-team/v3
handoff_type: <producer-to-consumer>
project_id: <ID>
producer_skill: <name>
consumer_skill: <name>
input_revision: <int>
output_revision: <int>
handoff_status: READY
validation_command: <command>
validation_result: PASS
generated_at: <ISO-8601>
```

Body must include: identification, summary, artifact inventory, preserved decisions, allowed open questions, blockers, consumer write scope, forbidden files, commands/results, stop instruction.

A `READY` handoff is immutable for its revision. Material change creates a new revision.

## Change control

| Finding | Return |
|---|---|
| Local detail inside contract | Keep execution; update evidence |
| Bad assignment/capability/batch | `REROUTE_REQUIRED` |
| Incomplete task/dependency/acceptance/contract | `REPLAN_REQUIRED` |
| Technical reality contradicts investigation | `investigate-existing-codebase` |
| Intent/audience/problem/outcome changed | `brainstorm-idea-with-user` |
| UX finding needs undecided product choice | Product decision; no task yet |

The finder records the reason but does not silently assume ownership of the return stage.

## Single-writer protocol

Only one skill may hold operational write authorization at a time (`writer_skill`).

- Default: no two executors writing concurrently.
- Read-only subagents are allowed.
- Parallel tests are allowed if they do not mutate artifacts.
- Isolated worktrees require a documented strategy and sequential merge review.
- Abandoned writers are recovered by checkpoint inspection, not by assuming a clean tree.

## Vocabulary

English-only for IDs, states, schema fields, and contracts:

- Task states: `PENDING`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`, `CANCELLED`
- Handoff: `NOT_READY`, `READY`, `CONSUMED`
- Review findings: `BLOCKING`, `HIGH`, `MEDIUM`, `LOW`, `QUESTION`, `OUT_OF_SCOPE`
- UX nature: `OBSERVED_DEFECT`, `EVIDENCE_BASED_RECOMMENDATION`, `PRODUCT_DECISION_REQUIRED`
- UX impact: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`

Legacy Portuguese aliases belong only in the migrator.

## AGENTS.md policy

Root and project `AGENTS.md` are discovery indexes only. They must not store current task, progress percent, active model, queue state, or duplicated status.

## Compatibility

- Predecessor: `planning-delegation/v2`
- Migration tool: `scripts/migrate_v2_to_v3.py`
- Catalog: `catalog/skills.json`, `catalog/categories.json`, `catalog/compatibility.json`
