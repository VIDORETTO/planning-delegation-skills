---
name: investigate-existing-codebase
description: Investigate an existing repository to establish current architecture, conventions, root cause, change impact, relevant patterns, and technical evidence before planning a bug fix, feature, refactor, or technical audit. Use when the codebase itself must be inspected to replace assumptions with evidence. Do not implement the change, create the formal plan, route models, or perform a visual UX audit.
---

# Investigate Existing Codebase

Replace assumptions about an existing repository with evidence. This skill owns only the
codebase-investigation branch of the `DISCOVERY` stage in `skill-team/v3`, alongside
`brainstorm-idea-with-user` (new intent) and `product-ux-audit` (rendered visual audit). Pick this
skill when the primary unknown is technical: what the code actually does, why it fails, what it
would cost to change, and what pattern a new change should follow.

## Workflow contract

```text
skill-team/v3
investigate-existing-codebase (DISCOVERY)
→ create-spec-driven-plan (PLANNING)
→ route-ai-work-by-capability (ROUTING)
→ execute-routed-task (IMPLEMENTATION)
→ review-implementation-evidence (REVIEW, when required)
→ validate-release-readiness (RELEASE)
```

Shared workflow root: `docs/ai/<project-slug>/`. `PROGRESS.md` is the sole operational pointer.
`AGENTS.md` is a discovery-only index. Never write `next_skill`; use `required_skill` and
`successor_skill`.

## Required resources

1. Read [references/repository-orientation.md](references/repository-orientation.md) before targeting the problem.
2. Read [references/root-cause-analysis.md](references/root-cause-analysis.md) for bugs and causal claims.
3. Read [references/change-impact.md](references/change-impact.md) before proposing blast radius.
4. Use [assets/INVESTIGATION.template.md](assets/INVESTIGATION.template.md) for the main artifact.
5. Use [assets/EVIDENCE.template.md](assets/EVIDENCE.template.md) for the evidence ledger.
6. Use [assets/CODEBASE-TO-PLAN.template.md](assets/CODEBASE-TO-PLAN.template.md) for the handoff.
7. Run [scripts/validate_investigation.py](scripts/validate_investigation.py) before declaring readiness.

## Exclusive stage ownership

Execute only investigation. Do not implement the fix, write the formal plan, assign models, or run
a rendered UX audit in the same operation. When finished:

1. validate investigation artifacts;
2. generate `handoffs/CODEBASE-TO-PLAN.md`;
3. update `PROGRESS.md`;
4. set `required_skill` and `successor_skill` to `create-spec-driven-plan`;
5. stop.

If the current state belongs to another skill, do not modify its artifacts. Report the
`required_skill` and stop.

## Entry gate

| Situation | Required action |
|---|---|
| No workflow root exists for a technical question | Create it with `status: CODEBASE_INVESTIGATION_IN_PROGRESS` |
| `status: CODEBASE_INVESTIGATION_IN_PROGRESS`, `required_skill: investigate-existing-codebase` | Resume without re-reading already-covered areas |
| `status: DISCOVERY_BLOCKED`, `required_skill: investigate-existing-codebase` | Resume, address the recorded blocker first |
| Return from `review-implementation-evidence` or `validate-release-readiness` citing a contradicted assumption | Accept, record the cause, resume investigation |
| Any other status owned by another skill | Stop without modifying artifacts |

For a new workflow root, initialize `PROGRESS.md` from the template with `discovery_revision: 1` and
`active_artifact` pointing at `discovery/codebase/INVESTIGATION.md`.

## Method

### 1. Orient before targeting the problem

Read the manifest/build files, two levels of directory structure, and naming/testing conventions.
This is always fast and always first — see
[references/repository-orientation.md](references/repository-orientation.md).

### 2. Focus investigation on the stated need

- Bug: trace the call path to the file and line where the incorrect behavior originates, not just
  the symptom. Describe the exact triggering condition.
- Feature: find the closest existing analogous implementation and treat it as the pattern to follow.
- Refactor/technical debt: point at concrete duplication, coupling, and file size with file names and
  counts, never an unsupported quality claim.
- Audit: prioritize shared modules, global shell, auth, and the data layer before isolated screens.

### 3. Map change impact before proposing anything

For every candidate change area, record how many files it touches, whether it is consumed by one
caller or many, and whether tests currently cover it. Absence of coverage raises the risk of any
later task in that area — record it, do not silently compensate for it.

### 4. Hold every claim to the evidence rule

Every statement in `INVESTIGATION.md` must resolve to something actually read: a `path/file.ext:line`
reference, a code excerpt, or a command output recorded in `EVIDENCE.md`. A claim without evidence
belongs in an explicit assumptions section, not in the findings. See
[references/root-cause-analysis.md](references/root-cause-analysis.md) and
[references/change-impact.md](references/change-impact.md).

### 5. Scope depth versus breadth deliberately

A large repository with a narrow, specific problem should get a scoped investigation of the relevant
subtree, confirmed not to be silently imported elsewhere. A general audit request on a large
repository takes longer and should be declared as multi-phase up front rather than rushed.

### 6. Build the artifact set

Under `docs/ai/<project-slug>/discovery/codebase/`:

- `INVESTIGATION.md`: architecture summary, relevant conventions, root cause or pattern to follow,
  impact map, and open technical questions.
- `EVIDENCE.md`: append-only ledger of every file read, command run, and output that backs a claim in
  `INVESTIGATION.md`.

`AGENTS.md` at the project root stays a discovery index only; do not duplicate investigation status
there.

### 7. Evaluate discovery readiness

Investigation may become `DISCOVERY_READY` only when:

- stack, structure, and relevant conventions are recorded;
- for a bug, the root cause is pinpointed with file:line evidence, not only the symptom;
- for a feature, an existing pattern to follow is identified or its absence is explicit;
- impact map (files touched, blast radius, test coverage) is recorded for every candidate area;
- every claim in `INVESTIGATION.md` resolves to an entry in `EVIDENCE.md`;
- no placeholder or unresolved local link remains.

If technical reality contradicts a product assumption from an existing brainstorm, do not silently
resolve it — record the contradiction and let `create-spec-driven-plan` route it back through change
control.

### 8. Produce the handoff and stop

Build `handoffs/CODEBASE-TO-PLAN.md` from its template: identification, summary, artifact inventory,
preserved decisions/assumptions, allowed open questions, blockers, consumer write scope, forbidden
files, commands/results, and the stop instruction.

Run:

```text
python skills/investigate-existing-codebase/scripts/validate_investigation.py docs/ai/<project-slug>
```

Only after it passes, set `status: DISCOVERY_READY`, `handoff_status: READY`,
`required_skill: create-spec-driven-plan`, `successor_skill: create-spec-driven-plan`, and record the
validation command/result in `PROGRESS.md`. Stop. Do not invoke planning in the same operation.

## Escalation and change control

- A genuinely open product decision (not a technical fact) belongs to `brainstorm-idea-with-user`;
  record it as a blocked question, do not decide it.
- A visual/UI rendering question belongs to `product-ux-audit`; do not substitute static code reading
  for a rendered inspection.
- Contradicted technical assumptions from a prior stage are recorded here, then handed to
  `create-spec-driven-plan` for disposition.

## Output contract

Produce only `discovery/codebase/INVESTIGATION.md`, `discovery/codebase/EVIDENCE.md`,
`handoffs/CODEBASE-TO-PLAN.md`, the minimal `AGENTS.md` discovery index, and the discovery transition
in `PROGRESS.md`. Do not claim readiness unless validation succeeds.

## Prohibitions

- Do not implement the fix or feature while investigating.
- Do not write the formal plan, requirements, or task breakdown.
- Do not assign or register models.
- Do not audit rendered UI/UX screens.
- Do not state a claim you cannot trace to `EVIDENCE.md`.
