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
- `RELEASE_REVIEW_IN_PROGRESS`
- `RELEASE_BLOCKED`
- `RELEASE_READY`
- `RELEASED`
- `POST_RELEASE_REVIEW_REQUIRED`
- `POST_RELEASE_REVIEW_IN_PROGRESS`

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

## Canonical state matrix

`NONE` is the terminal value for `required_skill` and `successor_skill`. A YAML `null` value is valid only for inactive task, batch, model, and writer fields. The statuses below belong to exactly one stage.

| Stage/status | Owner | Required skill | Writer | Handoff at rest |
|---|---|---|---|---|
| `DISCOVERY/BRAINSTORM_IN_PROGRESS` | brainstorm | brainstorm | brainstorm | `NOT_READY` |
| `DISCOVERY/CODEBASE_INVESTIGATION_IN_PROGRESS` | investigate | investigate | investigate | `NOT_READY` |
| `DISCOVERY/UX_AUDIT_IN_PROGRESS` | ux audit | ux audit | ux audit | `NOT_READY` |
| `DISCOVERY/DISCOVERY_READY` | final discovery owner | planner | null | `READY` |
| `DISCOVERY/DISCOVERY_BLOCKED` | discovery owner | discovery owner | null | `NOT_READY` |
| `PLANNING/PLAN_IN_PROGRESS` | planner | planner | planner | `NOT_READY` |
| `PLANNING/PLAN_VALIDATED` | planner | router | null | `READY` |
| `PLANNING/REPLAN_REQUIRED` | planner | planner | null | `NOT_READY` |
| `ROUTING/ROUTING_IN_PROGRESS` | router | router | router | `NOT_READY` |
| `ROUTING/IMPLEMENTATION_READY` | router | executor | null | `READY` |
| `ROUTING/REROUTE_REQUIRED` | router | router | null | `NOT_READY` |
| `IMPLEMENTATION/TASK_IN_PROGRESS` | executor | executor | executor and task | `CONSUMED` |
| `IMPLEMENTATION/TASK_COMPLETE` | executor | executor | null | `NOT_READY` |
| `IMPLEMENTATION/TASK_BLOCKED` | executor | classified owner | null | `NOT_READY` |
| `IMPLEMENTATION/IMPLEMENTATION_COMPLETE` | executor | reviewer or release validator | null | `READY` |
| `REVIEW/REVIEW_REQUIRED` | reviewer | reviewer | null | `READY` |
| `REVIEW/REVIEW_IN_PROGRESS` | reviewer | reviewer | reviewer | `CONSUMED` |
| `REVIEW/CHANGES_REQUIRED` | reviewer | executor | null | `READY` |
| `REVIEW/REVIEW_APPROVED` | reviewer | release validator | null | `READY` |
| `RELEASE/RELEASE_REVIEW_REQUIRED` | release validator | release validator | null | `READY` |
| `RELEASE/RELEASE_REVIEW_IN_PROGRESS` | release validator | release validator | release validator | `CONSUMED` |
| `RELEASE/RELEASE_BLOCKED` | release validator | release validator | null | `NOT_READY` |
| `RELEASE/RELEASE_READY` | release validator | `NONE` | null | `CONSUMED` |
| `RELEASE/RELEASED` | release validator | `NONE` | null | `CONSUMED` |
| `RELEASE/POST_RELEASE_REVIEW_REQUIRED` | release validator | release validator | null | `NOT_READY` |
| `RELEASE/POST_RELEASE_REVIEW_IN_PROGRESS` | release validator | release validator | release validator | `CONSUMED` |

The full owner identifiers are `brainstorm-idea-with-user`, `investigate-existing-codebase`, `product-ux-audit`, `create-spec-driven-plan`, `route-ai-work-by-capability`, `execute-routed-task`, `review-implementation-evidence`, and `validate-release-readiness` in their respective rows.

## Transition and revision rules

Discovery enters at revision 1 and reaches `DISCOVERY_READY` only after its validator passes. Consuming it increments `plan_revision`; a validated plan increments `routing_revision` when routing starts. The first implementation task for a routed pass increments `implementation_revision`; all tasks in that pass retain it. Entering review increments `review_revision`; entering release evaluation increments `release_revision`.

`REPLAN_REQUIRED` returns only to planning, `REROUTE_REQUIRED` only to routing, bounded review corrections only to implementation, technical contradictions only to codebase investigation, and product-intent changes only to brainstorm. A return never resets a downstream revision: stale downstream artifacts remain historical until regenerated. The review-waived path uses `implementation-to-release`; otherwise implementation uses `implementation-to-review`, then `review-to-release` after approval.

Every transition clears `last_validation_result` to `NOT_RUN` on entry and sets it to `PASS` only after the stage validator succeeds. A transition requires the acting `required_skill`, a coherent writer lock, a fresh consumed handoff where applicable, synchronized input/output revisions, and a valid active artifact. `TASK_IN_PROGRESS` additionally requires `writer_task`; every other state requires `writer_task: null`.

Combined discovery is sequential: its final owner inventories prior ready handoffs and emits one aggregate ready handoff at the current discovery revision. Any changed inventoried input makes that aggregate stale.

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
