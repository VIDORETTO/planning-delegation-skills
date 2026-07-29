---
document_type: sdd-improvement-plan
target_repository: skill-team-main
baseline_contract: skill-team/v3
status: PROPOSED
implementation_state: NOT_STARTED
workflow_profile: critical
planner_role: specification-and-planning-only
executor_role: lower-capability-operational-ai
created_at: 2026-07-29
---

# Skill Team Improvement Program

## Spec-Driven Development plan for a strict, coherent, and product-ready `skill-team/v3`

## 1. Document purpose

This document is the authoritative implementation plan for improving Skill Team after comparing its
specification workflow with GitHub Spec Kit. It is intentionally more explicit than a normal engineering
plan because the implementation is expected to be performed by an AI with lower reasoning capability than
the planner.

The executor MUST follow this document literally. It MUST NOT redesign the workflow, invent compatibility
behavior, change the contract version, add adjacent product features, or silently reinterpret ambiguous
instructions. When this document does not provide enough information for a structural decision, the executor
MUST stop and escalate instead of guessing.

The program has two ordered goals:

1. Make the existing `skill-team/v3` methodology mechanically coherent from discovery through release.
2. Add selected Spec Kit-inspired capabilities that improve specification quality and user experience without
   weakening Skill Team's stronger provenance, evidence, routing, review, and release controls.

The target is not merely more documentation. The target is an executable decision system in which:

- every stage has one owner;
- every transition has explicit entry and exit conditions;
- every ready artifact can be consumed by the next stage without manual repair;
- every requirement maps to tasks, tests, and evidence;
- repository validation proves both valid and invalid workflow behavior;
- a fresh agent can continue from files without reconstructing the original conversation.

## 2. Executive summary

Skill Team already has stronger methodology than Spec Kit in several areas: collaborative discovery,
preservation of user authority, source provenance, brownfield investigation, risk-based planning, model
routing, single-writer operation, independent review, and evidence-backed release decisions.

Spec Kit is stronger in a narrower but important area: it provides a simple and recognizable specification
artifact, an explicit clarification experience, requirements-quality checklists, cross-artifact analysis,
post-implementation convergence, installation tooling, and a lower-friction user journey.

The current Skill Team limitation is not absence of ideas. The primary limitation is that parts of the
contract, templates, validators, catalog, fixtures, and stage transitions disagree. Repository validation
passes, but it does not currently prove that the output of one stage is accepted by the next stage.

Therefore:

- Phase 1 repairs `skill-team/v3` and is a mandatory gate.
- Phase 2 adds specification-quality capabilities inspired by Spec Kit.
- Phase 3 hardens migration, adoption, and documentation.
- No Phase 2 implementation may begin until the Phase 1 gate is green.

## 3. Source authority and references

### 3.1 Authority order

When implementation sources conflict, use this order:

1. This plan's explicit decisions and requirements for the improvement program.
2. `contracts/skill-team-v3.md` after it is repaired by Phase 1.
3. Canonical JSON schemas and shared contract validators after Phase 1.
4. Active skill `SKILL.md` files.
5. Skill references and templates.
6. Catalog and README descriptions.
7. Tests and fixtures as evidence of intended behavior, not as authority when they preserve a known defect.
8. Spec Kit sources as design inspiration only.

An older file MUST NOT override a newer authoritative contract merely because it contains more detail.

### 3.2 Skill Team references

- `README.md`
- `AGENTS.md`
- `contracts/skill-team-v3.md`
- `contracts/progress-schema.json`
- `contracts/handoff-schema.json`
- `contracts/task-schema.json`
- `contracts/routing-schema.json`
- `scripts/progress_contract.py`
- `scripts/validate_repository.py`
- `scripts/migrate_v2_to_v3.py`
- `catalog/skills.json`
- `catalog/compatibility.json`
- `docs/migration/advisor-planner-map.md`
- `skills/brainstorm-idea-with-user/SKILL.md`
- `skills/brainstorm-idea-with-user/references/interview-strategy.md`
- `skills/create-spec-driven-plan/SKILL.md`
- `skills/create-spec-driven-plan/references/planning-method.md`
- `skills/create-spec-driven-plan/assets/PHASE.template.md`
- `skills/create-spec-driven-plan/assets/TRACEABILITY.template.md`
- all `skills/*/assets/*.template.md`
- all `skills/*/scripts/validate_*.py`
- `tests/integration/test_flow_fixtures.py`
- `tests/integration/test_workflow_pointers.py`

### 3.3 Spec Kit references

The following local snapshot files are references for concepts, not dependencies:

- `../spec-kit-main/README.md`
- `../spec-kit-main/spec-driven.md`
- `../spec-kit-main/templates/spec-template.md`
- `../spec-kit-main/templates/plan-template.md`
- `../spec-kit-main/templates/tasks-template.md`
- `../spec-kit-main/templates/constitution-template.md`
- `../spec-kit-main/templates/commands/specify.md`
- `../spec-kit-main/templates/commands/clarify.md`
- `../spec-kit-main/templates/commands/checklist.md`
- `../spec-kit-main/templates/commands/analyze.md`
- `../spec-kit-main/templates/commands/converge.md`
- `../spec-kit-main/workflows/speckit/workflow.yml`
- `../spec-kit-main/workflows/ARCHITECTURE.md`

Relevant upstream project: <https://github.com/github/spec-kit>.

Skill Team MUST remain independently portable, standard-library based, and governed by `skill-team/v3`.
No Spec Kit package, CLI, runtime, template resolver, or workflow engine becomes a dependency of Skill Team.

## 4. Baseline evidence

At planning time, these commands pass in the repository:

```text
python scripts/validate_repository.py
python -m unittest discover -s tests
```

Observed baseline:

- repository validation reports `REPOSITORY VALID`;
- 34 tests pass;
- validation covers catalog shape, links, Python compilation, skill references, trigger overlap, orphan
  resources, and unit test discovery;
- validation does not yet prove complete state transitions, canonical template compatibility, semantic
  traceability, or producer-to-consumer stage interoperability.

This distinction is mandatory:

```text
structurally green repository != proven end-to-end workflow
```

The executor MUST preserve baseline command outputs before changing behavior so regressions and expected
strictness changes can be distinguished.

## 5. Scope

### 5.1 In scope

- Repair the canonical v3 state machine.
- Align contracts, schemas, templates, validators, catalog, documentation, and fixtures.
- Remove live v2 compatibility aliases outside the migrator.
- Support every discovery input advertised by planning.
- Strengthen semantic validation and end-to-end tests.
- Add a compact canonical product specification view.
- Add bounded, incremental clarification behavior.
- Add requirements-quality checklists.
- Add persistent cross-artifact consistency analysis.
- Add project governance principles.
- Add controlled post-implementation convergence through review findings and return transitions.
- Improve migration safety and adoption documentation.

### 5.2 Explicit non-goals

- Do not rename the contract to `skill-team/v4`.
- Do not implement a generic workflow engine.
- Do not clone Spec Kit's CLI.
- Do not add hooks, presets, extensions, bundles, branch creation, or issue generation in this program.
- Do not add third-party Python dependencies.
- Do not permit concurrent writers by default.
- Do not collapse discovery, planning, routing, implementation, review, and release into one skill.
- Do not replace detailed discovery artifacts with a shallow `SPEC.md`.
- Do not make AI semantic judgment the only blocking validator.
- Do not deploy or publish a release as part of this plan.
- Do not preserve backward compatibility unless the v2 migrator proves a concrete need.

## 6. Personas and user journeys

### ACT-001 - Product user

Provides an idea, answers structural questions, retains authority over product intent, and approves major
product decisions.

### ACT-002 - Planner agent

Transforms validated discovery into requirements, contracts, phases, tasks, tests, and traceability. It does
not route models or implement code.

### ACT-003 - Operational executor agent

Performs one bounded task exactly as specified. It is assumed to have limited architectural judgment and
therefore requires exact files, commands, acceptance criteria, and escalation rules.

### ACT-004 - Independent reviewer agent

Verifies actual code and evidence without silently implementing fixes.

### ACT-005 - Maintainer

Maintains Skill Team's contracts, schemas, templates, catalog, adapters, validators, and release process.

### JRN-001 - New product idea to validated plan

1. The user provides an ambiguous idea.
2. Brainstorm preserves the original text and asks focused structural questions.
3. Planning consumes the ready discovery handoff and enters `PLAN_IN_PROGRESS`.
4. Planning produces a draft compact product specification view from validated discovery.
5. The discovery owner answers product-intent returns; the planner asks only plan-level clarification questions.
6. Clarification closes material gaps one question at a time while planning remains `PLAN_IN_PROGRESS`.
7. Requirements-quality checklists evaluate the written specification.
8. Planning creates contracts, tasks, oracles, and traceability.
9. Cross-artifact analysis blocks unresolved critical gaps before `PLAN_VALIDATED`.

### JRN-002 - Existing code change to validated plan

1. Investigation inspects repository evidence.
2. The codebase handoff identifies actual patterns, impact, and unresolved assumptions.
3. Planning consumes investigation without requiring a brainstorm handoff.
4. Product questions return to brainstorm only if intent is actually missing.

### JRN-003 - Implementation with constrained agent

1. Routing assigns an executor and optional reviewer.
2. The executor reads only the required context package.
3. The executor acquires one writer lock.
4. It changes only allowed paths and runs specified checks.
5. It records evidence or a blocker.
6. It does not invent missing product or architecture decisions.

### JRN-004 - Review and convergence

1. Review inspects the actual implementation.
2. Gaps are classified as missing, partial, contradictory, or unrequested.
3. Bounded implementation defects return to execution.
4. Assignment defects return to routing.
5. Contract or acceptance gaps return to planning.
6. Changed product intent returns to discovery.
7. Approval proceeds to release readiness.

## 7. Current defect register

The IDs below are stable for this improvement program. Do not renumber them.

| ID | Severity | Defect | Evidence |
|---|---|---|---|
| DEF-001 | CRITICAL | Planning's progress template uses obsolete fields and stage vocabulary. | `skills/create-spec-driven-plan/assets/PROGRESS.template.md`, compared with `contracts/skill-team-v3.md` |
| DEF-002 | CRITICAL | Planning validation still accepts v2 contracts and aliases forbidden by v3. | `skills/create-spec-driven-plan/scripts/validate_plan.py` |
| DEF-003 | CRITICAL | Brainstorm validation accepts statuses not defined by the canonical v3 status set. | `skills/brainstorm-idea-with-user/scripts/validate_brainstorm.py` |
| DEF-004 | CRITICAL | Routing validation accepts legacy stages, skills, paths, and aliases. | `skills/route-ai-work-by-capability/scripts/validate_routing.py` |
| DEF-005 | CRITICAL | Planning advertises multiple discovery inputs but mechanically assumes brainstorm input. | `skills/create-spec-driven-plan/SKILL.md`, `validate_plan.py` |
| DEF-006 | CRITICAL | Several handoff templates do not satisfy the canonical handoff contract. | handoff assets under `skills/*/assets/`, `contracts/handoff-schema.json` |
| DEF-007 | HIGH | Routing artifact paths disagree between skills, templates, and catalog. | routing skill, routing assets, `catalog/skills.json` |
| DEF-008 | HIGH | Catalog paths, maturity states, and notes are stale. | `catalog/skills.json` |
| DEF-009 | HIGH | Advisor migration documentation and compatibility records disagree about removal and successor resources. | `docs/migration/advisor-planner-map.md`, `catalog/compatibility.json` |
| DEF-010 | HIGH | Progress schema does not require every canonical active/write field and does not constrain statuses by stage. | `contracts/progress-schema.json` |
| DEF-011 | HIGH | Shared progress validation checks only a subset of transition and writer invariants. | `scripts/progress_contract.py`, `contracts/skill-team-v3.md` |
| DEF-012 | HIGH | Stage validators duplicate incompatible parsing and validation behavior. | `skills/*/scripts/validate_*.py` |
| DEF-013 | HIGH | Integration tests often assert text instead of executing real producer-consumer transitions. | `tests/integration/` |
| DEF-014 | HIGH | Repository validation does not validate schemas, canonical template instances, or all stage validators. | `scripts/validate_repository.py` |
| DEF-015 | HIGH | `REBRAINSTORM_REQUIRED` is used in guidance but absent from the contract. | planning references and v3 status table |
| DEF-016 | HIGH | The no-review path from implementation to release is not fully specified. | implementation handoff, release entry contract, handoff schema |
| DEF-017 | MEDIUM | Handoff immutability and `CONSUMED` recording semantics are incomplete. | `contracts/skill-team-v3.md` |
| DEF-018 | MEDIUM | Revision behavior is incomplete for combined discovery and return loops. | v3 contract revision and change-control sections |
| DEF-019 | MEDIUM | Repository validation retains an obsolete legacy skill exception. | `scripts/validate_repository.py` |
| DEF-020 | MEDIUM | JSON schemas are not demonstrably applied to generated Markdown records. | `contracts/*.json`, repository validation pipeline |

## 8. Target workflow

```text
DISCOVERY
  brainstorm | codebase investigation | UX audit
  optional approved combination; one writer at a time
        |
        v
PLANNING
  draft SPEC view from validated discovery
  clarify one material question at a time and persist each answer
  governance check, contracts, vertical slices, tasks, oracles, traceability
        |
        v
CONSISTENCY ANALYSIS
  structural blockers + advisory semantic findings
        |
        v
ROUTING
  executor, reviewer, locks, batches, model capability evidence
        |
        v
IMPLEMENTATION
  bounded task, one writer, tests, evidence, blocker classification
        |
        +------> REVIEW REQUIRED
        |          |
        |          +--> bounded correction -> IMPLEMENTATION
        |          +--> assignment issue -> ROUTING
        |          +--> contract gap -> PLANNING
        |          +--> intent change -> DISCOVERY
        |          +--> approval -> RELEASE
        |
        +------> REVIEW WAIVED BY ROUTING POLICY -> RELEASE
                   |
                   v
              RELEASE READINESS
                   |
                   v
              EXTERNAL HUMAN DEPLOYMENT
                   |
                   v
              POST-RELEASE EVIDENCE
```

## 9. Normative requirements

### Contract and state

- **REQ-001:** Every live artifact and validator MUST accept only `workflow_contract: skill-team/v3`.
  V2 interpretation MUST exist only in `scripts/migrate_v2_to_v3.py` and migration fixtures.
- **REQ-002:** `PROGRESS.md` MUST use one exact canonical field set and MUST reject `next_skill`,
  `active_skill`, `current_task`, nested validation records, and stage aliases.
- **REQ-003:** Every status MUST belong to its declared stage.
- **REQ-004:** Every allowed stage transition MUST have explicit entry guards and output field updates.
- **REQ-005:** `required_skill`, `stage_owner`, `writer_skill`, and `writer_task` MUST be coherent for every
  allowed state.
- **REQ-006:** Revisions MUST be monotonic, synchronized at handoff boundaries, and never reused for materially
  different content.

### Handoffs and paths

- **REQ-007:** Every ready handoff MUST satisfy one canonical frontmatter and body contract.
- **REQ-008:** Handoff producer, consumer, input revision, output revision, validation result, and status MUST
  match `PROGRESS.md`.
- **REQ-009:** A ready handoff file MUST remain immutable for its revision.
- **REQ-010:** Handoff consumption MUST be represented in `PROGRESS.md`; changing handoff content MUST create
  a new revision.
- **REQ-011:** Every artifact type MUST have one canonical path with no live fallback alias.
- **REQ-012:** Planning MUST accept brainstorm, investigation, UX audit, an approved combination, or a validated
  compact brief without requiring an unrelated handoff.

### Specification and planning

- **REQ-013:** Detailed discovery MUST remain authoritative for product decisions and provenance.
- **REQ-014:** Planning MUST generate a compact `plan/SPEC.md` view for stakeholders and downstream agents.
- **REQ-015:** `SPEC.md` MUST include problem, outcomes, actors, prioritized stories, acceptance scenarios,
  requirements, success criteria, non-goals, assumptions, and unresolved decisions.
- **REQ-016:** Every active requirement MUST have a stable `REQ-*` ID, origin, priority, release, oracle, and state.
- **REQ-017:** Every active requirement MUST map to at least one task; every task MUST map to at least one active
  requirement.
- **REQ-018:** Material uncertainty MUST be resolved, explicitly delegated, or explicitly deferred before
  `PLAN_VALIDATED`; structural uncertainty cannot be deferred.
- **REQ-045:** `plan/SPEC.md`, planning-owned clarification records, checklists, and consistency analysis are
  substeps of `PLAN_IN_PROGRESS`; they do not introduce new top-level stages. A question about product intent
  MUST return to the applicable discovery owner before planning resumes on a new discovery revision.
- **REQ-019:** Project governance principles MUST be versioned and cited by planning checks.
- **REQ-020:** Governance MUST NOT silently override explicit user decisions, applicable law, or stronger security
  controls; conflicts require escalation.

### Requirements quality and analysis

- **REQ-021:** Requirements-quality checklists MUST evaluate completeness, clarity, consistency, measurability,
  scenario coverage, edge cases, dependencies, and assumptions.
- **REQ-022:** Checklist items MUST test the written requirement, not implementation behavior.
- **REQ-023:** Every checklist item MUST have a stable `CHK-*` ID and a requirement reference or an explicit
  `[Gap]`, `[Ambiguity]`, `[Conflict]`, or `[Assumption]` marker.
- **REQ-024:** Cross-artifact analysis MUST detect uncovered requirements, orphan tasks, stale revisions, invalid
  paths, dependency cycles, contradictions, terminology drift, and governance violations.
- **REQ-025:** Deterministic structural failures MUST block plan validation. AI semantic findings MAY be advisory
  until confirmed by an explicit decision or deterministic rule.
- **REQ-026:** Analysis results MUST be persisted in `plan/CONSISTENCY-REPORT.md`, not only returned in chat.

### Tasks, routing, execution, and review

- **REQ-027:** Every task MUST include stable ID, requirement origins, dependencies, exact write scope, forbidden
  scope, objective, inputs, outputs, errors, invariants, security, implementation steps, tests, acceptance,
  rollback, evidence, and escalation.
- **REQ-028:** During planning, executor MUST remain `UNASSIGNED`; routing owns model assignment.
- **REQ-029:** Parallel eligibility MUST require disjoint write scopes, satisfied dependencies, and an explicit
  isolation and merge strategy. Default operation remains one writer.
- **REQ-030:** Task completion MUST require acceptance evidence; blocked state MUST require a blocker artifact.
- **REQ-031:** Review MUST inspect actual code and evidence independently from the executor.
- **REQ-032:** Review gaps MUST be classified as `missing`, `partial`, `contradicts`, or `unrequested`, in addition
  to severity.
- **REQ-033:** Review MUST return local corrections to implementation, assignment problems to routing, contract
  gaps to planning, technical contradictions to investigation, and intent changes to brainstorm.
- **REQ-034:** Review MUST NOT silently append plan tasks or implement fixes.
- **REQ-035:** A review-waived path MUST be explicitly declared by routing and use a canonical
  `IMPLEMENTATION-TO-RELEASE.md` handoff.

### Validation, migration, and release

- **REQ-036:** Repository validation MUST instantiate and validate canonical templates.
- **REQ-037:** Repository validation MUST execute valid and invalid end-to-end workflow fixtures.
- **REQ-038:** Every forbidden transition MUST fail for a deterministic, asserted reason.
- **REQ-039:** Catalog, contracts, schemas, templates, validators, tests, README, and migration docs MUST agree.
- **REQ-040:** Migration MUST support dry run, be idempotent, preserve user changes, and validate output strictly.
- **REQ-041:** Every implementation phase MUST define a rollback point.
- **REQ-042:** No capability phase may start until strict v3 consistency passes.
- **REQ-043:** Release readiness MUST cite evidence for every passing or accepted-risk gate.
- **REQ-044:** Accepted risk MUST include owner, rationale, expiration or review condition, and non-waivable gate
  confirmation.

## 10. Architecture decisions

- **DEC-001:** Keep the contract identifier `skill-team/v3`; this is a repair and capability program, not v4.
- **DEC-002:** Canonical routing paths are `routing/ROUTING.md` and `routing/MODEL-CAPABILITIES.md`.
- **DEC-003:** Canonical investigation paths are `discovery/codebase/INVESTIGATION.md` and
  `discovery/codebase/EVIDENCE.md`.
- **DEC-004:** Canonical review report path is `review/REVIEW-REPORT.md`; detailed findings remain
  `findings/<FINDING-ID>.md`.
- **DEC-005:** Canonical execution paths are `execution/EVIDENCE.md`, `execution/HISTORY.md`, and
  `blockers/<TASK-ID>.md`.
- **DEC-006:** Remove `BRAINSTORM_READY` and `REBRAINSTORM_REQUIRED`. Use canonical discovery statuses plus
  `required_skill: brainstorm-idea-with-user` when rediscovery is required.
- **DEC-007:** A review may be skipped only when routing explicitly records that no independent review is required.
- **DEC-008:** A review-waived implementation uses `handoffs/IMPLEMENTATION-TO-RELEASE.md`.
- **DEC-009:** Ready handoff files remain immutable. Consumption changes the pointer's `handoff_status`.
- **DEC-010:** Add one shared standard-library contract validator used by all stage validators.
- **DEC-011:** Extend existing skill owners for governance, clarification, checklists, analysis, and convergence;
  do not create overlapping skills in the first implementation.
- **DEC-012:** Add `plan/SPEC.md` as a compact derived view. It does not replace brainstorm, investigation, UX,
  contracts, or traceability artifacts.
- **DEC-013:** Mechanical analysis blocks. AI-authored semantic analysis is advisory unless confirmed and recorded.
- **DEC-014:** Use explicit `parallel_eligible: true|false` metadata rather than copying Spec Kit's `[P]` marker.
- **DEC-015:** Do not add a workflow engine or package manager in this program.

## 11. System invariants

- **INV-001:** Exactly one `PROGRESS.md` is authoritative per workflow root.
- **INV-002:** At most one non-null `writer_skill` exists at a time.
- **INV-003:** `writer_task` is non-null only while an implementation task holds the lock.
- **INV-004:** A skill never executes its successor stage in the same invocation.
- **INV-005:** Revisions never decrease and are never recycled.
- **INV-006:** `READY` requires validator `PASS`, synchronized revisions, no placeholders, and valid local links.
- **INV-007:** `COMPLETE` requires evidence; `BLOCKED` requires a blocker.
- **INV-008:** Routing cannot alter requirements, decisions, dependencies, contracts, or acceptance semantics.
- **INV-009:** Review and release cannot modify implementation files.
- **INV-010:** No task may write outside its declared scope.
- **INV-011:** Security gates are not weakened by `compact`, `standard`, or `critical` profiles.
- **INV-012:** Legacy aliases exist only in migration code and migration fixtures.
- **INV-013:** A repository-wide pass means valid canonical fixtures pass and invalid fixtures fail as expected.
- **INV-014:** A lower-capability executor never resolves structural ambiguity during implementation.

## 12. Canonical state transitions

| From condition | To condition | Acting skill | Required evidence and updates |
|---|---|---|---|
| No workflow | Discovery `*_IN_PROGRESS` | Selected discovery skill | Initialize canonical pointer, revision 1, writer lock for discovery |
| Discovery in progress | `DISCOVERY_READY` | Discovery owner | Ready handoff, matching revision, validator PASS, release writer |
| `DISCOVERY_READY` | `PLAN_IN_PROGRESS` | `create-spec-driven-plan` | Consume approved input, set planning owner and writer |
| `PLAN_IN_PROGRESS` | `PLAN_VALIDATED` | Planner | Plan artifacts, checklists, consistency report, validator PASS |
| `REPLAN_REQUIRED` | `PLAN_IN_PROGRESS` | Planner | Record return reason, increment revision for material change |
| `PLAN_VALIDATED` | `ROUTING_IN_PROGRESS` | Router | Consume fresh plan handoff, set routing writer |
| `ROUTING_IN_PROGRESS` | `IMPLEMENTATION_READY` | Router | Assignments, reviewer policy, locks, validator PASS |
| `REROUTE_REQUIRED` | `ROUTING_IN_PROGRESS` | Router | Preserve plan semantics, revise assignments only |
| `IMPLEMENTATION_READY` | `TASK_IN_PROGRESS` | Executor | Dependencies complete, active model matches, acquire task lock |
| `TASK_IN_PROGRESS` | `TASK_COMPLETE` | Executor | Tests and acceptance pass, evidence appended, release task lock |
| `TASK_IN_PROGRESS` | `TASK_BLOCKED` | Executor | Blocker artifact, return classification, release task lock |
| Final task complete | `IMPLEMENTATION_COMPLETE` | Executor | Execution validator PASS and outgoing handoff ready |
| Implementation complete, review required | `REVIEW_REQUIRED` | Reviewer | Consume implementation-to-review handoff |
| Implementation complete, review waived | `RELEASE_REVIEW_REQUIRED` | Release validator | Consume implementation-to-release handoff |
| `REVIEW_REQUIRED` | `REVIEW_IN_PROGRESS` | Reviewer | Independent reviewer matches routing policy |
| `REVIEW_IN_PROGRESS` | `REVIEW_APPROVED` | Reviewer | No open blocking/high findings; review evidence PASS |
| `REVIEW_IN_PROGRESS` | `CHANGES_REQUIRED` | Reviewer | Bounded finding set and implementation return handoff |
| Review finding changes assignment | `REROUTE_REQUIRED` | Router | Finding identifies capability, batch, or lock defect |
| Review finding changes contract | `REPLAN_REQUIRED` | Planner | Finding identifies requirement, task, dependency, or acceptance gap |
| Review finding contradicts current codebase evidence | `CODEBASE_INVESTIGATION_IN_PROGRESS` | `investigate-existing-codebase` | Record finding and fresh investigation revision; planning artifacts become stale |
| Review finding changes intent | Discovery in progress | Discovery owner | Finding identifies audience, problem, outcome, or MVP change |
| Approved or waived implementation | `RELEASE_READY` | Release validator | All applicable gates pass with evidence |
| Approved or waived implementation | `RELEASE_BLOCKED` | Release validator | At least one non-waived gate fails; blockers recorded |
| External deployment recorded | `RELEASED` | External human/process | Release record references approved readiness revision |
| `RELEASED` with unexpected technical behavior | `CODEBASE_INVESTIGATION_IN_PROGRESS` | `investigate-existing-codebase` | `POST-RELEASE.md` evidence, new discovery revision, no mutation of released evidence |
| `RELEASED` with changed audience/problem/outcome | `BRAINSTORM_IN_PROGRESS` | `brainstorm-idea-with-user` | `POST-RELEASE.md` evidence, new discovery revision, released artifacts retained as history |

Every transition implementation MUST have at least one positive and one negative test.

### 12.1 Canonical status ownership matrix

`NONE` is the literal terminal value for `required_skill` and `successor_skill`; YAML null remains reserved for
inactive task/model fields. `writer_skill` is non-null only while the named skill is actively writing.

| Stage/status | Stage owner | Required skill | Writer while active | Handoff status at rest |
|---|---|---|---|---|
| `DISCOVERY/BRAINSTORM_IN_PROGRESS` | `brainstorm-idea-with-user` | same | same | `NOT_READY` |
| `DISCOVERY/CODEBASE_INVESTIGATION_IN_PROGRESS` | `investigate-existing-codebase` | same | same | `NOT_READY` |
| `DISCOVERY/UX_AUDIT_IN_PROGRESS` | `product-ux-audit` | same | same | `NOT_READY` |
| `DISCOVERY/DISCOVERY_READY` | final discovery producer | `create-spec-driven-plan` | null | `READY` |
| `DISCOVERY/DISCOVERY_BLOCKED` | active discovery owner | active discovery owner | null until resumed | `NOT_READY` |
| `PLANNING/PLAN_IN_PROGRESS` | `create-spec-driven-plan` | same | same | `NOT_READY` |
| `PLANNING/PLAN_VALIDATED` | `create-spec-driven-plan` | `route-ai-work-by-capability` | null | `READY` |
| `PLANNING/REPLAN_REQUIRED` | `create-spec-driven-plan` | same | null until resumed | `NOT_READY` |
| `ROUTING/ROUTING_IN_PROGRESS` | `route-ai-work-by-capability` | same | same | `NOT_READY` |
| `ROUTING/IMPLEMENTATION_READY` | `route-ai-work-by-capability` | `execute-routed-task` | null | `READY` |
| `ROUTING/REROUTE_REQUIRED` | `route-ai-work-by-capability` | same | null until resumed | `NOT_READY` |
| `IMPLEMENTATION/TASK_IN_PROGRESS` | `execute-routed-task` | same | same, with `writer_task` | `CONSUMED` |
| `IMPLEMENTATION/TASK_COMPLETE` | `execute-routed-task` | same when tasks remain | null | `NOT_READY` |
| `IMPLEMENTATION/TASK_BLOCKED` | `execute-routed-task` | owner selected by blocker classification | null | `NOT_READY` |
| `IMPLEMENTATION/IMPLEMENTATION_COMPLETE` | `execute-routed-task` | reviewer when required, otherwise release validator | null | `READY` |
| `REVIEW/REVIEW_REQUIRED` | `review-implementation-evidence` | same | null | `READY` |
| `REVIEW/REVIEW_IN_PROGRESS` | `review-implementation-evidence` | same | same | `CONSUMED` |
| `REVIEW/CHANGES_REQUIRED` | `review-implementation-evidence` | `execute-routed-task` | null | `READY` |
| `REVIEW/REVIEW_APPROVED` | `review-implementation-evidence` | `validate-release-readiness` | null | `READY` |
| `RELEASE/RELEASE_REVIEW_REQUIRED` | `validate-release-readiness` | same | null | `READY` |
| `RELEASE/RELEASE_REVIEW_IN_PROGRESS` | `validate-release-readiness` | same | same | `CONSUMED` |
| `RELEASE/RELEASE_BLOCKED` | `validate-release-readiness` | same | null until reevaluation | `NOT_READY` |
| `RELEASE/RELEASE_READY` | `validate-release-readiness` | `NONE` | null | `CONSUMED` |
| `RELEASE/RELEASED` | `validate-release-readiness` | `NONE` | null | `CONSUMED` |
| `RELEASE/POST_RELEASE_REVIEW_REQUIRED` | `validate-release-readiness` | same | null until review starts | `NOT_READY` |
| `RELEASE/POST_RELEASE_REVIEW_IN_PROGRESS` | `validate-release-readiness` | same | same | `CONSUMED` |

### 12.2 Revision algorithm

1. Revision fields never decrease and start at `0` before their stage family has produced material work.
2. Entering a new material discovery pass increments `discovery_revision` by one before writing. The same value
   remains through its ready handoff.
3. Entering `PLAN_IN_PROGRESS` from discovery or `REPLAN_REQUIRED` increments `plan_revision` by one. Clarification,
   checklists, and analysis within that pass keep the same revision; a material rewrite after validation starts a
   new pass and increments again.
4. Entering `ROUTING_IN_PROGRESS` from plan or `REROUTE_REQUIRED` increments `routing_revision` by one.
5. Entering the first `TASK_IN_PROGRESS` of an initial implementation or correction pass increments
   `implementation_revision` by one. Additional tasks in the same routed pass keep that value.
6. Entering `REVIEW_IN_PROGRESS` increments `review_revision` by one. Re-review after corrections increments again.
7. Entering release evaluation from approved or waived implementation increments `release_revision` by one.
   Reevaluation after a blocked release increments again.
8. Return transitions never reset downstream revisions. Downstream artifacts remain historical but stale until
   regenerated against the newer upstream revision.
9. Handoff `input_revision` is the consumed upstream family's current revision; `output_revision` is the
   producer family's current revision.
10. Combined discovery is sequential. The final discovery owner reads prior ready discovery handoffs and emits
    its own canonical handoff with the current `discovery_revision`, hashes and inventories all prior inputs, and
    preserves their decisions. Planning consumes this final aggregate handoff only. If any inventoried input hash
    changes, the aggregate handoff is stale.

### 12.3 Exact transition mutation rules

All fields not named in a row are preserved. Every row clears `last_validation_result` to `NOT_RUN` on entry to
active work and sets it to `PASS` only after the named validator succeeds.

| ID | Guard | Required field mutations |
|---|---|---|
| TR-001 | No workflow, raw idea | Initialize all canonical fields; discovery rev `1`; all later revs `0`; brainstorm in progress; active artifact `discovery/brainstorm/BRAINSTORM.md`; writer brainstorm |
| TR-002 | No workflow, existing-code change | Same initialization, but codebase investigation in progress and active artifact `discovery/codebase/INVESTIGATION.md` |
| TR-003 | No workflow, controlled UX audit | Same initialization, but UX audit in progress and active artifact `discovery/ux/UX-AUDIT.md` |
| TR-003A | Active discovery cannot proceed | Keep `DISCOVERY`; set `DISCOVERY_BLOCKED`; preserve active discovery owner and required skill; writer null; handoff `NOT_READY`; active artifact blocker; blockers non-`NONE`. Resume by restoring that owner's matching in-progress status and writer. Increment discovery revision only if blocker resolution causes material discovery writing. |
| TR-004 | Discovery validator PASS and structural questions `NONE` | `DISCOVERY_READY`; required planner; successor router; handoff `READY`; writer null; active artifact final discovery handoff |
| TR-005 | Fresh discovery handoff and no writer | Increment plan rev; `PLANNING/PLAN_IN_PROGRESS`; owner/required/writer planner; successor router; handoff `CONSUMED`; active artifact `plan/00-MASTER.md` |
| TR-006 | Plan/checklist/analysis validators PASS | `PLAN_VALIDATED`; required router; successor executor; handoff `READY`; writer null; active artifact `handoffs/PLAN-TO-ROUTING.md` |
| TR-007 | Fresh plan handoff and no writer | Increment routing rev; `ROUTING_IN_PROGRESS`; owner/required/writer router; successor executor; handoff `CONSUMED`; active artifact `routing/ROUTING.md` |
| TR-008 | Routing validator PASS and every active task assigned | `IMPLEMENTATION_READY`; required executor; successor reviewer or release per policy; handoff `READY`; writer null; active artifact routing handoff |
| TR-009 | Ready routing, dependencies PASS, active model matches | On first task in pass increment implementation rev; `IMPLEMENTATION/TASK_IN_PROGRESS`; owner/required/writer executor; writer task and active task set; handoff `CONSUMED`; active artifact task phase/context |
| TR-010 | Task acceptance and evidence PASS, more tasks remain | `TASK_COMPLETE`; writer fields null; required executor; active task next dependency-ready task; handoff `NOT_READY` |
| TR-011 | Task cannot proceed | `TASK_BLOCKED`; writer fields null; active artifact blocker; blockers non-`NONE`; required skill from change-control classification |
| TR-012 | All release-scope tasks complete and execution validator PASS | `IMPLEMENTATION_COMPLETE`; writer fields null; active task/batch null; handoff `READY`; active artifact implementation-to-review or implementation-to-release; required skill matches route policy |
| TR-013 | Fresh implementation-to-review handoff | `REVIEW/REVIEW_REQUIRED`; owner/required reviewer; writer null; handoff `READY`; active artifact implementation-to-review handoff |
| TR-013A | `REVIEW_REQUIRED`, reviewer matches routing, no writer | Increment review rev; `REVIEW_IN_PROGRESS`; owner/required/writer reviewer; handoff `CONSUMED`; active artifact review report |
| TR-014 | Review finds bounded local defects | `CHANGES_REQUIRED`; writer null; required executor; handoff `READY`; active artifact review-to-implementation handoff |
| TR-014A | Fresh review-to-implementation handoff, correction task/scope explicit | Increment implementation rev; `IMPLEMENTATION/TASK_IN_PROGRESS`; owner/required/writer executor; writer task and active task set; handoff `CONSUMED`; active artifact correction task context |
| TR-015 | Review finds assignment defect | `ROUTING/REROUTE_REQUIRED`; stage owner/required skill router; writer null; handoff `NOT_READY`; active artifact finding |
| TR-016 | Review finds requirement/task/contract defect | `PLANNING/REPLAN_REQUIRED`; stage owner/required skill planner; writer null; handoff `NOT_READY`; active artifact finding |
| TR-017 | Review finds technical evidence contradiction | Increment discovery rev; codebase investigation in progress; owner/required/writer investigator; handoff `NOT_READY`; active artifact investigation |
| TR-018 | Review finds intent/audience/outcome change | Increment discovery rev; brainstorm in progress; owner/required/writer brainstorm; handoff `NOT_READY`; active artifact brainstorm |
| TR-019 | Review validator PASS with no blocking/high findings | `REVIEW_APPROVED`; writer null; required release validator; handoff `READY`; active artifact review-to-release handoff |
| TR-020 | Fresh review-to-release or implementation-to-release handoff | `RELEASE/RELEASE_REVIEW_REQUIRED`; owner/required release validator; writer null; handoff `READY`; active artifact incoming release handoff |
| TR-020A | `RELEASE_REVIEW_REQUIRED`, no writer, fresh incoming handoff | Increment release rev; `RELEASE_REVIEW_IN_PROGRESS`; owner/required/writer release validator; handoff `CONSUMED`; active artifact release readiness report |
| TR-021 | All applicable release gates PASS or valid accepted risk | `RELEASE_READY`; required/successor `NONE`; writer null; blockers `NONE`; validation PASS |
| TR-022 | Any non-waived release gate FAIL | `RELEASE_BLOCKED`; required release validator; writer null; blockers cite failed gates; validation FAIL |
| TR-023 | External deployment evidence references ready revision | `RELEASED`; required/successor `NONE`; writer null; active artifact deployment record or readiness report |
| TR-024 | Post-release deviation is reported | Set `RELEASE/POST_RELEASE_REVIEW_REQUIRED`, stage owner/required skill release validator, writer null, handoff `NOT_READY`, active artifact post-release report |
| TR-024A | `POST_RELEASE_REVIEW_REQUIRED`, report exists, no writer | Set `POST_RELEASE_REVIEW_IN_PROGRESS`; owner/required/writer release validator; classify evidence without changing discovery revision |
| TR-025 | Post-release classification is technical | From `POST_RELEASE_REVIEW_IN_PROGRESS`, release writer records classification and releases lock, then apply TR-017, whose single increment starts the codebase discovery pass |
| TR-025A | Post-release classification changes product intent | From `POST_RELEASE_REVIEW_IN_PROGRESS`, release writer records classification and releases lock, then apply TR-018, whose single increment starts the brainstorm pass |
| TR-026 | Resume from `REPLAN_REQUIRED` or `REROUTE_REQUIRED` | Acquire only owning writer, increment that stage-family revision, set its canonical in-progress status, clear blocker only after its cause is addressed |
| TR-026A | Resume from `RELEASE_BLOCKED` | Keep release owner/required skill; increment release revision; set `RELEASE_REVIEW_IN_PROGRESS`; acquire release writer; handoff `CONSUMED`; clear each blocker only after its failed gate is reevaluated |

## 13. Canonical artifacts

| Artifact | Canonical path | Required content |
|---|---|---|
| Operational pointer | `docs/ai/<slug>/PROGRESS.md` | Exact canonical frontmatter and short derived human view |
| Governance | `docs/ai/<slug>/GOVERNANCE.md` | Version, principles, authority, rationale, amendments, exceptions |
| Source register | `docs/ai/<slug>/SOURCE-REGISTER.md` | Stable source ID, authority, date, validity, scope |
| Context index | `docs/ai/<slug>/CONTEXT-INDEX.md` | Links and purpose only; no duplicated status |
| Glossary | `docs/ai/<slug>/GLOSSARY.md` | Canonical terms, aliases, deprecated terms |
| Brainstorm | `discovery/brainstorm/BRAINSTORM.md` | Original idea, decisions, assumptions, risks, rejected options |
| Investigation | `discovery/codebase/INVESTIGATION.md` | Evidence-backed current state, root cause/pattern, impact, gaps |
| Investigation evidence | `discovery/codebase/EVIDENCE.md` | Append-only `EV-*` records with file/line or command output |
| UX audit | `discovery/ux/UX-AUDIT.md` | Findings, evidence, approval state, product decisions |
| Compact specification | `plan/SPEC.md` | Product-readable WHAT/WHY and testable requirements |
| Plan manifest | `plan/PLAN-MANIFEST.md` | Profile, applicability, artifact inventory and revisions |
| Master plan | `plan/00-MASTER.md` | Authority, releases, phases, gates, document map |
| Governance check | `plan/GOVERNANCE-CHECK.md` | Principle-by-principle result and exceptions |
| Requirements checklist | `plan/checklists/<domain>.md` | Stable checklist IDs and requirement-quality questions |
| Consistency report | `plan/CONSISTENCY-REPORT.md` | Structural and semantic findings plus coverage metrics |
| Phase | `plan/phases/<PHASE-ID>.md` | Objective, entry, exit, non-scope, complete task contracts |
| Traceability | `plan/TRACEABILITY.md` | Source to requirement to task to oracle to evidence |
| Routing | `routing/ROUTING.md` | Assignment, reviewer, batch, locks, capability rationale |
| Model capabilities | `routing/MODEL-CAPABILITIES.md` | Stable model IDs, dated capabilities, constraints and cost |
| Execution evidence | `execution/EVIDENCE.md` | Commands, outputs, changed paths, acceptance by task |
| Execution history | `execution/HISTORY.md` | Append-only attempt and state history |
| Blocker | `blockers/<TASK-ID>.md` | Cause, evidence, owner, return stage, unblocking condition |
| Review report | `review/REVIEW-REPORT.md` | Scope, method, rerun checks, findings, outcome |
| Finding | `findings/<FINDING-ID>.md` | Severity, gap type, evidence, owner, disposition |
| Release readiness | `release/RELEASE-READINESS.md` | Gate-by-gate evidence and decision |
| Post-release evidence | `release/POST-RELEASE.md` | Expected/actual comparison, incidents, metrics, return classification |

### 13.1 Canonical handoff inventory

No handoff name outside this table is valid in `skill-team/v3` unless the contract and this plan are revised
first.

| Handoff type | Canonical path | Producer | Consumer |
|---|---|---|---|
| `brainstorm-to-plan` | `handoffs/BRAINSTORM-TO-PLAN.md` | `brainstorm-idea-with-user` | `create-spec-driven-plan` |
| `codebase-to-plan` | `handoffs/CODEBASE-TO-PLAN.md` | `investigate-existing-codebase` | `create-spec-driven-plan` |
| `ux-audit-to-plan` | `handoffs/UX-AUDIT-TO-PLAN.md` | `product-ux-audit` | `create-spec-driven-plan` |
| `plan-to-routing` | `handoffs/PLAN-TO-ROUTING.md` | `create-spec-driven-plan` | `route-ai-work-by-capability` |
| `routing-to-implementation` | `handoffs/ROUTING-TO-IMPLEMENTATION.md` | `route-ai-work-by-capability` | `execute-routed-task` |
| `implementation-to-review` | `handoffs/IMPLEMENTATION-TO-REVIEW.md` | `execute-routed-task` | `review-implementation-evidence` |
| `implementation-to-release` | `handoffs/IMPLEMENTATION-TO-RELEASE.md` | `execute-routed-task` | `validate-release-readiness` |
| `review-to-implementation` | `handoffs/REVIEW-TO-IMPLEMENTATION.md` | `review-implementation-evidence` | `execute-routed-task` |
| `review-to-release` | `handoffs/REVIEW-TO-RELEASE.md` | `review-implementation-evidence` | `validate-release-readiness` |

Return to routing, planning, investigation, or brainstorm is represented by the applicable finding or blocker,
the updated `PROGRESS.md`, and a new revision of the normal forward handoff after the owner repairs its stage.
Do not create ad hoc `REVIEW-TO-PLAN`, `REVIEW-TO-ROUTING`, or similar handoff types.

## 14. Compact `SPEC.md` contract

`plan/SPEC.md` MUST use this logical structure:

```markdown
# Product Specification: <name>

## Identification
## Problem and intended outcome
## Actors and authority
## Scope of the first usable release
## Non-goals
## Prioritized user journeys
### US-001 - <journey> (P1)
#### Why this priority
#### Independent value
#### Acceptance scenarios
1. Given ... When ... Then ...
## Functional requirements
- REQ-001: ...
## Quality requirements
## Key entities and lifecycle
## Edge, failure, and recovery cases
## Success criteria
## Assumptions
## Rejected and deferred options
## Open decisions
## Source and revision references
```

Rules:

- It is derived from validated discovery and planning records.
- It MUST preserve IDs and source origins.
- It MUST NOT contain implementation stack choices unless they are explicit product constraints.
- It MUST NOT silently replace detailed discovery artifacts.
- Every user journey MUST deliver independently observable value.
- Every acceptance scenario MUST be testable.
- Every vague term such as “fast”, “secure”, “intuitive”, or “robust” MUST be quantified or identified as
  unresolved.

## 15. Clarification protocol

Before planning, clarification belongs to the active discovery owner. After the planner enters
`PLAN_IN_PROGRESS`, the planner may ask only plan-level questions. A planning question that reveals missing
product intent MUST create a controlled return to the relevant discovery owner; planning resumes only after a
new validated discovery revision. Clarification never creates a separate top-level stage.

1. Build an internal coverage map: scope, actors, permissions, data, lifecycle, UX states, failures,
   integrations, quality attributes, compliance, terminology, and completion signals.
2. Rank unresolved questions by impact multiplied by uncertainty.
3. Ask exactly one question at a time.
4. Explain in one sentence why the answer changes acceptance, architecture, risk, or release.
5. Offer two to five mutually exclusive options when meaningful.
6. Present a recommended option and rationale without treating it as accepted.
7. Accept a custom answer.
8. Persist each accepted answer immediately with source, authority, and revision.
9. Remove or supersede contradictory previous text.
10. Recompute readiness after every answer.
11. Stop when structural gaps are closed, the user explicitly stops, or further questions are non-material.

Unlike Spec Kit, five questions are a soft interaction checkpoint, not a completeness rule. After five accepted
questions, the agent SHOULD summarize remaining gaps and ask whether to continue. It MUST continue when a
structural question prevents safe planning and the user agrees.

## 16. Requirements-quality checklist contract

Checklist items are “unit tests for requirements writing.”

Correct:

```text
CHK-001 - Are authorization requirements defined for every protected operation? [Gap, REQ-014]
CHK-002 - Is “fast” quantified for the P1 journey? [Ambiguity, SC-002]
```

Incorrect:

```text
CHK-001 - Test that login returns HTTP 200.
CHK-002 - Verify the button works.
```

Required checklist domains for `standard` and `critical` profiles when applicable:

- requirements completeness;
- requirement clarity;
- internal consistency;
- acceptance measurability;
- primary, alternate, error, recovery, and non-functional scenarios;
- authorization and isolation;
- data retention and deletion;
- integration failure and retry;
- migration and rollback;
- observability and redaction;
- assumptions and dependencies.

## 17. Validation strategy

### 17.1 Mechanical blocking validation

- exact fields and enums;
- stage/status/skill matrix;
- writer lock coherence;
- existing paths and links;
- no placeholders in ready artifacts;
- revision synchronization;
- handoff producer/consumer agreement;
- unique stable IDs;
- valid and acyclic dependencies;
- requirement-to-task and task-to-requirement coverage;
- complete task contract sections;
- evidence for complete tasks;
- blockers for blocked tasks;
- catalog-to-skill path agreement.

### 17.2 Semantic analysis

- ambiguous language;
- contradictory requirements;
- duplicate requirements;
- untestable acceptance;
- missing failure/recovery behavior;
- terminology drift;
- weak success metrics;
- governance conflicts;
- implementation details leaking into product requirements.

Semantic findings generated by an AI are advisory until one of these conditions applies:

- a deterministic validator confirms the issue;
- a human or authorized planner confirms the finding;
- the finding directly cites an explicit contradictory statement.

### 17.3 Canonical validator error contract

Validator success exits `0`. A validated contract or artifact failure exits `1`. Invalid CLI usage, unreadable
input, or an internal validator failure exits `2`. Validation errors are written to stderr in this exact form:

```text
<ERROR_CODE> <relative-path-or-field>: <human-readable detail>
```

Multiple validation failures are sorted by path, field, and error code so unchanged input produces stable output.
The first token is a public test oracle and MUST NOT be changed without a contract revision.

| Error code | Blocking condition |
|---|---|
| `STV3-E001-CONTRACT` | `workflow_contract` is absent or not `skill-team/v3` |
| `STV3-E002-FIELD-MISSING` | Required canonical field or section is absent |
| `STV3-E003-FIELD-UNKNOWN` | Forbidden or unknown field appears where additional fields are disallowed |
| `STV3-E004-TYPE` | Field has the wrong scalar, list, object, integer, or null type |
| `STV3-E005-ENUM` | Value is outside its canonical vocabulary |
| `STV3-E006-STAGE-STATUS` | Stage and status do not match Section 12.1 |
| `STV3-E007-OWNER` | `stage_owner` does not own the stage/status |
| `STV3-E008-REQUIRED-SKILL` | `required_skill` or `successor_skill` contradicts the state |
| `STV3-E009-WRITER-LOCK` | Writer skill/task is missing, stale, or conflicts with another writer |
| `STV3-E010-REVISION` | Revision is negative, decreases, increments incorrectly, or mismatches an artifact |
| `STV3-E011-HANDOFF-STALE` | Handoff revision/hash is not fresh for its inputs |
| `STV3-E012-HANDOFF-CONTRACT` | Handoff type, producer, consumer, status, or validation metadata is invalid |
| `STV3-E013-HANDOFF-BODY` | Canonical handoff body section is absent or incomplete |
| `STV3-E014-ARTIFACT-MISSING` | Referenced active or required artifact does not exist |
| `STV3-E015-LINK` | Required local Markdown link does not resolve |
| `STV3-E016-PLACEHOLDER` | Ready artifact contains a placeholder or unresolved structural marker |
| `STV3-E017-ID-DUPLICATE` | Stable requirement, task, decision, finding, checklist, or source ID is reused |
| `STV3-E018-DEPENDENCY-MISSING` | Task dependency does not resolve to an active task |
| `STV3-E019-DEPENDENCY-CYCLE` | Task dependency graph contains a cycle or self-reference |
| `STV3-E020-TRACE-REQ` | Active requirement lacks task or oracle coverage |
| `STV3-E021-TRACE-TASK` | Active task lacks requirement origin |
| `STV3-E022-EVIDENCE` | Complete task or passing gate lacks required evidence |
| `STV3-E023-BLOCKER` | Blocked state lacks blocker, owner, or unblocking condition |
| `STV3-E024-MODEL` | Assigned/active executor or reviewer is not registered or mismatches routing |
| `STV3-E025-SCOPE` | Task scopes overlap unsafely, path escapes root, or a changed path is unauthorized |
| `STV3-E026-REVIEW` | Approval conflicts with open blocking/high findings or missing independent review |
| `STV3-E027-RELEASE-EVIDENCE` | Release gate lacks resolving evidence or contains a non-waivable failure |
| `STV3-E028-ACCEPTED-RISK` | Accepted risk lacks owner, rationale, review condition, or authority |
| `STV3-E029-PATH-TRAVERSAL` | Input attempts absolute escape, `..` traversal, or symlink escape outside root |
| `STV3-E030-INTERNAL` | Validator cannot complete due to invalid invocation, unreadable input, or internal error; exit `2` |

## 18. Executor operating protocol

The lower-capability operational AI MUST use this sequence for every task:

1. Read this document's task entry completely.
2. Read every file listed under mandatory reading.
3. Verify dependencies are complete using evidence, not assumption.
4. Inspect the current worktree without reverting unrelated changes.
5. Confirm allowed and forbidden write scopes.
6. Run the task's baseline tests before editing when feasible.
7. Make the smallest change that satisfies the task.
8. Run the exact required tests.
9. Compare results against every acceptance criterion.
10. Record commands, outputs, and changed paths.
11. Stop if an escalation condition occurs.
12. Do not start the next task in the same invocation unless explicitly authorized.

The executor MUST NOT:

- invent a missing schema field;
- choose a different canonical path;
- add compatibility aliases;
- weaken a test to make it pass;
- modify files outside scope;
- combine tasks because they look similar;
- mark a task complete with failing acceptance;
- reinterpret a planner proposal as a user requirement;
- silently fix an unrelated defect.

### 18.1 Mandatory inherited task envelope

Every `Fxx-xxx` task in Section 19 inherits this envelope. The executor MUST combine this envelope with the
task-specific fields; omission from a task subsection does not make a field optional. Every task additionally
declares `REQ-041` because it must create and cite its recoverable pre-change checkpoint.

**Inputs:** this plan at its routed revision; files in the exact write-scope manifest; mandatory reading named
by the task; completed dependency evidence; current repository validation output.

**Outputs:** only files in the exact write-scope manifest; a task evidence record at
`baseline/validator-runs/<TASK-ID>.md`; updated tests explicitly assigned to the task; no unrelated formatting.

**Error behavior:** return nonzero from new validators on contract failure; preserve deterministic error text;
stop without partial state promotion when a command fails; record a blocker rather than guessing.

**Invariants:** preserve `skill-team/v3`; standard library only; one writer; no v2 live aliases; no weakening of
security profiles; no modification outside exact scope; no completed state without evidence.

**Security and privacy:** do not add secrets or real personal data to fixtures; treat Markdown and frontmatter as
untrusted input; do not execute commands parsed from artifacts; reject path traversal and writes outside the
repository root; preserve redaction requirements in logs and evidence.

**Required evidence format:** task ID, plan revision, executor model ID, start/end timestamp, dependency evidence,
baseline commands, changed files, test commands, exit codes, relevant stdout/stderr, acceptance result, rollback
checkpoint, and unresolved risks. Expected successful test exit code is `0`; expected-invalid fixture commands
must return nonzero and include the asserted invariant or error identifier.

**Common final commands:**

```text
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Both commands MUST exit `0` before a task is complete unless the task explicitly creates a failing baseline in
F00. Task-specific tests run before these common commands.

**Rollback rule:** before the first edit, record hashes of every allowed existing file in the evidence record.
Before a task is accepted, local unaccepted edits may be reverted only within that task's exact scope. After a
task is accepted into an F01 checkpoint, F01 files are rolled back only as the coordinated F01 set described in
Section 25.

**Escalation:** stop for an absent contract, unlisted file requirement, new public schema decision, contract
version change, third-party dependency, scope expansion, contradictory requirement, concurrent writer, or test
whose correct expected behavior cannot be derived from this plan.

### 18.2 Exact write-scope manifest

Paths marked `NEW` are authorized creations. A `/**` suffix authorizes files only below that named fixture
directory. Every task is additionally authorized to create exactly
`baseline/validator-runs/<TASK-ID>.md` and `baseline/checkpoints/<TASK-ID>-prechange/**`. The checkpoint stores
copies of allowed pre-change files at their relative paths plus `MANIFEST.sha256`; these exceptions authorize no
other baseline files.
No other file may be changed unless planning is revised first. If a task subsection uses descriptive wording
such as “affected tests” or “corresponding references,” the exact manifest below takes precedence and is the
only write authorization.

| Task | Exact allowed paths |
|---|---|
| F00-001 | `baseline/validator-runs/F00-001.md` (NEW); `baseline/checkpoints/F01-prechange/**` (NEW); `tests/integration/test_known_contract_gaps.py` (NEW); `tests/fixtures/known-contract-gaps/**` (NEW) |
| F01-001 | `contracts/skill-team-v3.md`; `contracts/progress-schema.json`; `contracts/handoff-schema.json`; `contracts/task-schema.json`; `contracts/routing-schema.json`; `tests/unit/test_contract_schemas.py` (NEW); `tests/unit/test_state_transitions.py` (NEW) |
| F01-002 | `scripts/progress_contract.py`; `scripts/workflow_contract.py` (NEW); `tests/unit/test_progress_contract.py`; `tests/unit/test_workflow_contract.py` (NEW) |
| F01-003 | `skills/brainstorm-idea-with-user/assets/PROGRESS.template.md`; `skills/brainstorm-idea-with-user/assets/BRAINSTORM-TO-PLAN.template.md`; `skills/investigate-existing-codebase/assets/INVESTIGATION.template.md`; `skills/investigate-existing-codebase/assets/EVIDENCE.template.md`; `skills/investigate-existing-codebase/assets/CODEBASE-TO-PLAN.template.md`; `skills/product-ux-audit/assets/UX-AUDIT-TO-PLAN.template.md`; `skills/create-spec-driven-plan/assets/PROGRESS.template.md`; `skills/create-spec-driven-plan/assets/PLAN-MANIFEST.template.md`; `skills/create-spec-driven-plan/assets/PHASE.template.md`; `skills/create-spec-driven-plan/assets/PLAN-TO-ROUTING.template.md`; `skills/route-ai-work-by-capability/assets/ROUTING.template.md`; `skills/route-ai-work-by-capability/assets/MODEL-CAPABILITIES.template.md`; `skills/route-ai-work-by-capability/assets/ROUTING-TO-IMPLEMENTATION.template.md`; `skills/execute-routed-task/assets/IMPLEMENTATION-TO-REVIEW.template.md`; `skills/execute-routed-task/assets/IMPLEMENTATION-TO-RELEASE.template.md` (NEW); `skills/review-implementation-evidence/assets/REVIEW-TO-IMPLEMENTATION.template.md`; `skills/review-implementation-evidence/assets/REVIEW-TO-RELEASE.template.md`; `skills/validate-release-readiness/assets/POST-RELEASE.template.md`; `tests/unit/test_canonical_templates.py` (NEW); `tests/fixtures/canonical-templates/**` (NEW) |
| F01-004 | `skills/brainstorm-idea-with-user/scripts/validate_brainstorm.py`; `skills/investigate-existing-codebase/scripts/validate_investigation.py`; `skills/product-ux-audit/scripts/validate_ux_audit.py`; `skills/create-spec-driven-plan/scripts/validate_plan.py`; `skills/brainstorm-idea-with-user/SKILL.md`; `skills/investigate-existing-codebase/SKILL.md`; `skills/product-ux-audit/SKILL.md`; `skills/create-spec-driven-plan/SKILL.md`; `skills/brainstorm-idea-with-user/references/interview-strategy.md`; `skills/create-spec-driven-plan/references/planning-method.md`; `tests/integration/test_discovery_to_plan_matrix.py` (NEW); `tests/fixtures/discovery-input-matrix/**` (NEW) |
| F01-005 | `skills/route-ai-work-by-capability/scripts/validate_routing.py`; `skills/execute-routed-task/scripts/validate_execution.py`; `skills/review-implementation-evidence/scripts/validate_review.py`; `skills/validate-release-readiness/scripts/validate_release.py`; `skills/route-ai-work-by-capability/SKILL.md`; `skills/execute-routed-task/SKILL.md`; `skills/review-implementation-evidence/SKILL.md`; `skills/validate-release-readiness/SKILL.md`; `skills/route-ai-work-by-capability/references/classification-rubric.md`; `skills/execute-routed-task/references/execution-loop.md`; `skills/review-implementation-evidence/references/independent-verification-method.md`; `skills/validate-release-readiness/references/release-gate-checklist.md`; `tests/integration/test_post_plan_transitions.py` (NEW); `tests/fixtures/post-plan-transitions/**` (NEW) |
| F01-006 | `catalog/skills.json`; `catalog/compatibility.json`; `docs/migration/advisor-planner-map.md`; `scripts/validate_repository.py`; `scripts/validate_catalog.py`; `README.md`; `AGENTS.md`; `tests/integration/test_flow_fixtures.py`; `tests/integration/test_workflow_pointers.py`; `tests/integration/test_repository_contract_gate.py` (NEW); `tests/fixtures/greenfield-product/**`; `tests/fixtures/existing-code-bug/**`; `tests/fixtures/ux-audit-to-plan/**`; `tests/fixtures/compact-plan/**`; `tests/fixtures/invalid-workflows/**`; `baseline/validator-runs/F01-CHECKPOINT.md` (NEW) |
| F02-001 | `skills/create-spec-driven-plan/assets/GOVERNANCE.template.md` (NEW); `skills/create-spec-driven-plan/assets/GOVERNANCE-CHECK.template.md` (NEW); `skills/brainstorm-idea-with-user/SKILL.md`; `skills/create-spec-driven-plan/SKILL.md`; `skills/create-spec-driven-plan/references/planning-method.md`; `skills/create-spec-driven-plan/scripts/validate_plan.py`; `tests/integration/test_governance_gate.py` (NEW); `tests/fixtures/governance/**` (NEW) |
| F02-002 | `skills/create-spec-driven-plan/assets/SPEC.template.md` (NEW); `skills/create-spec-driven-plan/assets/TRACEABILITY.template.md`; `skills/create-spec-driven-plan/SKILL.md`; `skills/create-spec-driven-plan/references/planning-method.md`; `skills/create-spec-driven-plan/scripts/validate_plan.py`; `tests/integration/test_compact_spec.py` (NEW); `tests/fixtures/compact-spec/**` (NEW) |
| F02-003 | `skills/brainstorm-idea-with-user/SKILL.md`; `skills/brainstorm-idea-with-user/references/interview-strategy.md`; `skills/brainstorm-idea-with-user/assets/BRAINSTORM.template.md`; `skills/create-spec-driven-plan/SKILL.md`; `skills/create-spec-driven-plan/references/planning-method.md`; `skills/create-spec-driven-plan/assets/SPEC.template.md`; `skills/brainstorm-idea-with-user/scripts/validate_brainstorm.py`; `skills/create-spec-driven-plan/scripts/validate_plan.py`; `tests/integration/test_incremental_clarification.py` (NEW); `tests/fixtures/clarification/**` (NEW) |
| F02-004 | `skills/create-spec-driven-plan/assets/REQUIREMENTS-CHECKLIST.template.md` (NEW); `skills/create-spec-driven-plan/SKILL.md`; `skills/create-spec-driven-plan/references/planning-method.md`; `skills/create-spec-driven-plan/scripts/validate_plan.py`; `tests/integration/test_requirements_checklists.py` (NEW); `tests/fixtures/requirements-checklists/**` (NEW) |
| F02-005 | `skills/create-spec-driven-plan/assets/CONSISTENCY-REPORT.template.md` (NEW); `skills/create-spec-driven-plan/scripts/analyze_plan.py` (NEW); `skills/create-spec-driven-plan/scripts/validate_plan.py`; `skills/create-spec-driven-plan/SKILL.md`; `skills/create-spec-driven-plan/references/planning-method.md`; `tests/unit/test_plan_analysis.py` (NEW); `tests/fixtures/plan-analysis/**` (NEW) |
| F02-006 | `skills/create-spec-driven-plan/assets/PHASE.template.md`; `skills/create-spec-driven-plan/assets/TRACEABILITY.template.md`; `skills/create-spec-driven-plan/references/planning-method.md`; `skills/route-ai-work-by-capability/assets/ROUTING.template.md`; `skills/route-ai-work-by-capability/references/classification-rubric.md`; `skills/route-ai-work-by-capability/scripts/validate_routing.py`; `tests/unit/test_parallel_eligibility.py` (NEW); `tests/fixtures/parallel-eligibility/**` (NEW) |
| F02-007 | `skills/review-implementation-evidence/SKILL.md`; `skills/review-implementation-evidence/references/independent-verification-method.md`; `skills/review-implementation-evidence/assets/REVIEW-REPORT.template.md`; `skills/review-implementation-evidence/assets/FINDING.template.md`; `skills/review-implementation-evidence/scripts/validate_review.py`; `tests/integration/test_review_convergence.py` (NEW); `tests/fixtures/review-convergence/**` (NEW) |
| F03-001 | `scripts/migrate_v2_to_v3.py`; `docs/migration/advisor-planner-map.md`; `docs/migration/v3-strict-migration.md` (NEW); `tests/unit/test_v3_migration.py` (NEW); `tests/fixtures/migration/**` (NEW) |
| F03-002 | `scripts/init_workflow.py` (NEW); `docs/workflow-initialization.md` (NEW); `tests/unit/test_init_workflow.py` (NEW); `tests/fixtures/workflow-init/**` (NEW) |
| F03-003 | `README.md`; `CONTRIBUTING.md`; `AGENTS.md`; `SECURITY.md`; `catalog/skills.json`; `catalog/compatibility.json`; `adapters/codex/README.md`; `adapters/opencode/README.md`; `adapters/cursor/README.md`; `.github/workflows/validate-skills.yml`; `baseline/validator-runs/F03-003.md` (NEW) |
| F03-004 | `tests/integration/test_rollout_qualification.py` (NEW); `tests/fixtures/rollout-sample/**` (NEW); `baseline/rollout/**` (NEW); `baseline/validator-runs/F03-004.md` (NEW) |

### 18.2.1 Task objective matrix

Each sentence below is the task-level observable objective required by REQ-027.

| Task | Observable objective |
|---|---|
| F00-001 | Produce a reproducible baseline that demonstrates current passes and at least three contract defects not caught by the repository gate. |
| F01-001 | Make the prose contract and schemas define one complete, non-contradictory v3 state machine. |
| F01-002 | Provide one reusable strict validator that rejects every forbidden v3 state relation deterministically. |
| F01-003 | Make every canonical template instantiate into an artifact accepted by the strict shared validator. |
| F01-004 | Make every advertised discovery input reach a valid plan without requiring an unrelated handoff. |
| F01-005 | Make routing through release execute all normal and return paths with strict revisions, locks, evidence, and review policy. |
| F01-006 | Make one repository command prove contracts, templates, catalog, and valid/invalid end-to-end fixtures. |
| F02-001 | Make versioned governance principles mechanically visible and blocking where a confirmed MUST is violated. |
| F02-002 | Generate a concise, traceable, stakeholder-readable product specification from validated discovery. |
| F02-003 | Persist material clarification one question at a time without losing ownership or decisions. |
| F02-004 | Validate the quality of written requirements with traceable domain checklists. |
| F02-005 | Persist deterministic coverage and consistency findings before routing. |
| F02-006 | Prove vertical slices and parallel eligibility without weakening the single-writer invariant. |
| F02-007 | Classify implementation gaps and return each gap to its correct owner without silent edits. |
| F03-001 | Migrate known legacy artifacts to strict v3 through a dry-runnable, idempotent, rollback-safe process. |
| F03-002 | Initialize a valid workflow deterministically without overwriting existing artifacts. |
| F03-003 | Make all public documentation, catalogs, adapters, CI, and final evidence describe and verify the shipped behavior. |
| F03-004 | Execute rollout waves W1-W5 against one controlled sample and persist an independently reviewed promotion decision for every wave. |

### 18.2.2 Mandatory reading matrix

The task-specific mandatory reading below supplements this plan and the inherited envelope.

| Task | Mandatory reading before editing |
|---|---|
| F00-001 | `scripts/validate_repository.py`; every `skills/*/scripts/validate_*.py`; `tests/integration/test_flow_fixtures.py`; `tests/integration/test_workflow_pointers.py` |
| F01-001 | `contracts/skill-team-v3.md`; all four JSON schemas in `contracts/`; defect register DEF-003, DEF-006, DEF-010, DEF-015 through DEF-018 |
| F01-002 | completed F01-001 evidence; `scripts/progress_contract.py`; every stage validator's frontmatter parsing and entry checks |
| F01-003 | completed F01-001 and F01-002 evidence; all assets in its exact scope; canonical artifact and handoff inventories in Sections 13 and 13.1 |
| F01-004 | completed F01-002 and F01-003 evidence; four discovery/planning `SKILL.md` files; `create-spec-driven-plan/references/planning-method.md` |
| F01-005 | completed F01-002 and F01-003 evidence; four post-plan `SKILL.md` files; routing rubric; execution, review, and release methods |
| F01-006 | all F01 evidence; `catalog/skills.json`; `catalog/compatibility.json`; `scripts/validate_catalog.py`; repository validator; all current integration tests |
| F02-001 | F01 checkpoint; governance requirements REQ-019/020; Spec Kit constitution template and constitution command as inspiration only |
| F02-002 | F01 checkpoint; validated discovery and planning templates; Section 14; Spec Kit spec template as inspiration only |
| F02-003 | F02-002 evidence; Section 15; brainstorm interview strategy; Spec Kit clarify command as inspiration only |
| F02-004 | F02-002 evidence; Section 16; Spec Kit checklist command as inspiration only |
| F02-005 | F02-004 evidence; Section 17; Spec Kit analyze command as inspiration only |
| F02-006 | F02-005 evidence; current phase/traceability templates; routing rubric; single-writer contract |
| F02-007 | F02-005 and F02-006 evidence; independent review method; finding classification; Spec Kit converge command as inspiration only |
| F03-001 | all F02 evidence; current migrator; migration map; compatibility catalog; Section 24 |
| F03-002 | F03-001 evidence; canonical initial state; repaired progress/handoff templates; adapter path conventions |
| F03-003 | all prior evidence; all public documentation and adapter guides; CI workflow; release gates G1-G6 |
| F03-004 | F03-003 evidence; Section 25.1; strict validators; migrator and initializer docs; controlled sample fixtures |

### 18.3 Task-specific test and evidence matrix

| Task | Required task-specific command | Expected evidence |
|---|---|---|
| F00-001 | `python -m unittest tests.integration.test_known_contract_gaps -v` | Tests reproduce documented false-green behavior; failures are described, not hidden |
| F01-001 | `python -m unittest tests.unit.test_contract_schemas tests.unit.test_state_transitions -v` | All allowed rows pass; forbidden rows fail with asserted reason |
| F01-002 | `python -m unittest tests.unit.test_progress_contract tests.unit.test_workflow_contract -v` | Exact field, type, relation, lock, revision, and handoff checks pass |
| F01-003 | `python -m unittest tests.unit.test_canonical_templates -v` | Every instantiated template validates; expected exit `0` |
| F01-004 | `python -m unittest tests.integration.test_discovery_to_plan_matrix -v` | Five valid input modes pass; unsafe variants fail as asserted |
| F01-005 | `python -m unittest tests.integration.test_post_plan_transitions -v` | Review/no-review and every return loop pass; invalid locks/revisions fail |
| F01-006 | `python -m unittest tests.integration.test_repository_contract_gate -v` | Repository gate detects each representative defect class |
| F02-001 | `python -m unittest tests.integration.test_governance_gate -v` | MUST conflict blocks; authorized exception is traceable |
| F02-002 | `python -m unittest tests.integration.test_compact_spec -v` | Required sections, IDs, origins, and scenario oracles validate |
| F02-003 | `python -m unittest tests.integration.test_incremental_clarification -v` | One-at-a-time persistence, no repetition, revision update, and return ownership pass |
| F02-004 | `python -m unittest tests.integration.test_requirements_checklists -v` | Checklist semantics, IDs, traceability, and blocking policy pass |
| F02-005 | `python -m unittest tests.unit.test_plan_analysis -v` | Deterministic findings and metrics match golden fixtures |
| F02-006 | `python -m unittest tests.unit.test_parallel_eligibility -v` | Disjoint case eligible; overlap, dependency, and global-state cases rejected |
| F02-007 | `python -m unittest tests.integration.test_review_convergence -v` | Four gap types and every owner return are proven |
| F03-001 | `python -m unittest tests.unit.test_v3_migration -v` | Dry run, idempotence, collision, interruption, and hash-safe rollback pass |
| F03-002 | `python -m unittest tests.unit.test_init_workflow -v` | Clean init passes; collision refuses; Windows/POSIX paths pass |
| F03-003 | `python scripts/validate_repository.py` | Clean final pass and adapter/document examples verified |
| F03-004 | `python -m unittest tests.integration.test_rollout_qualification -v` | W1-W5 metrics and promotion artifacts match expected results |

Subjective acceptance statements are never sufficient alone. For example, stakeholder readability in F02-002
requires all mandatory sections, no unexplained technical terms, no unresolved structural questions, and a
review record by a non-author agent or human.

### 18.4 Phase rollback checkpoints

| Phase | Checkpoint | Rollback verification |
|---|---|---|
| F00 | `baseline/checkpoints/F01-prechange/` contains complete copies of every existing F01-allowed file plus `MANIFEST.sha256` before contract edits | Restored copies match manifest; baseline commands reproduce original result |
| F01 | `baseline/validator-runs/F01-CHECKPOINT.md` contains hashes for every accepted F01 file after G1-G3 pass; recovery source remains `baseline/checkpoints/F01-prechange/` | Restore the complete coordinated pre-change set only; remove files marked NEW; run baseline and strict tests |
| F02 | `baseline/checkpoints/<TASK-ID>-prechange/` contains complete copies and manifest | Roll back only in reverse dependency order; restore a task after all dependents are removed; remove its NEW files; F01 gate remains green |
| F03 | Pre-migration complete copies, source-hash manifest, and final documentation checkpoint | Migrator no-op/idempotence and repository validation pass after restore |

REQ-041 is satisfied only when the applicable checkpoint exists and is referenced by task evidence.

### 18.5 Bootstrap authorization while v3 is under repair

This improvement program repairs the workflow contract itself. It MUST NOT create a synthetic `PROGRESS.md` that
jumps directly to routing, because that would violate the state machine being repaired. F00 through F03 are
therefore executed as serial repository-maintenance tasks under this authoritative plan, outside a consumer
`skill-team/v3` workflow. They validate and improve v3 but do not pretend to be a v3 consumer run.

Before each task, the human operator or primary maintenance agent provides one assignment message containing:

```text
Plan: docs/SKILL-TEAM-SDD-IMPROVEMENT-PLAN.md
Plan SHA-256: <hash>
Authorized task: <one Fxx-xxx ID>
Executor model ID: <ID>
Independent reviewer model ID: <ID>
Allowed paths: Section 18.2 row for the task plus inherited evidence/checkpoint paths
Dependency evidence: <paths>
Stop condition: stop after this task's evidence is complete
```

The executor copies this authorization verbatim into the beginning of
`baseline/validator-runs/<TASK-ID>.md` before editing. An assignment with more than one task, an unmatched plan
hash, absent reviewer, or incomplete dependency evidence is invalid and the executor MUST stop.

`F00-001` is the only valid first assignment. Tasks proceed in Section 20 dependency order. No workflow root,
routing artifact, model-capability file, or handoff is fabricated for program bootstrap. Once the program ships,
normal consumer workflows use the repaired canonical state machine and the initializer specified by F03-002.

## 19. Implementation phases

### Phase F00 - Reproducible baseline

#### Objective

Capture the current false-green boundary so strictness improvements can be proven.

#### Entry conditions

- Repository is available.
- No contract files are being changed concurrently.

#### Exit gate

- Baseline command outputs are recorded.
- Representative currently undetected contract defects have failing or false-green reproductions.

#### F00-001 - Capture repository and validator baseline

Requirement IDs: REQ-036, REQ-037, REQ-039, REQ-042

Defect IDs: DEF-013, DEF-014, DEF-020

Dependencies: NONE

Priority: CRITICAL

Risk: LOW

Mandatory reading:

- `scripts/validate_repository.py`
- `tests/integration/test_flow_fixtures.py`
- all stage validator command usage sections

Write scope:

- `baseline/validator-runs/`
- tests added only to reproduce known failures

Forbidden scope:

- `contracts/`
- skill templates
- validator production logic

Expected implementation:

1. Record Python version and operating system.
2. Run repository validation and unit tests.
3. Run each stage validator against at least one current fixture.
4. Record exit code and complete output.
5. Add reproductions for at least transition mismatch, legacy alias acceptance, and template-validator mismatch.

Tests and commands:

```text
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

Acceptance:

- [ ] Baseline results are timestamped and reproducible.
- [ ] Existing passing tests remain unchanged in expectation.
- [ ] At least three false-green scenarios are demonstrated.
- [ ] No production contract behavior is changed.

Required evidence:

- command transcripts;
- exit codes;
- fixture paths;
- explanation of why repository validation did not catch each scenario.

Rollback:

- Remove only baseline fixtures and records added by this task.

Escalation:

- Stop if the repository differs materially from the defect register.

### Phase F01 - Canonical `skill-team/v3` repair

#### Objective

Make every producer output directly consumable by the next stage and make repository validation prove it.

#### Mandatory gate

No F02 task may start until every F01 task passes.

#### F01-001 - Formalize the complete v3 state machine

Requirement IDs: REQ-001 through REQ-011, REQ-035

Defect IDs: DEF-003, DEF-006, DEF-010, DEF-015, DEF-016, DEF-017, DEF-018, DEF-020

Dependencies: F00-001

Priority: CRITICAL

Risk: HIGH

Write scope:

- `contracts/skill-team-v3.md`
- `contracts/progress-schema.json`
- `contracts/handoff-schema.json`
- `contracts/task-schema.json`
- `contracts/routing-schema.json`
- contract-focused tests

Expected implementation:

1. Add an explicit transition table equivalent to Section 12.
2. Define all stage/status/owner/required-skill combinations.
3. Define nullability and writer lock rules.
4. Define revision increments for normal progression and every return loop.
5. Define combined discovery revision behavior.
6. Define immutable ready handoff and pointer-based consumption semantics.
7. Add `implementation-to-release` to the canonical handoff types.
8. Remove undefined status vocabulary.
9. Expand task schema requirements to match the documented task contract.

Acceptance:

- [ ] Every canonical status belongs to exactly one stage.
- [ ] Every transition has one acting skill and explicit guards.
- [ ] Review-required and review-waived paths are both complete.
- [ ] Schemas reject omitted canonical fields and unknown fields where appropriate.
- [ ] Contract identifier remains `skill-team/v3`.

Rollback:

- Revert all coordinated contract and schema changes together; never leave mixed versions.

Escalation:

- Stop if a required fix cannot be expressed without introducing `skill-team/v4`.

#### F01-002 - Implement one strict shared contract validator

Requirement IDs: REQ-001 through REQ-010, REQ-036, REQ-038

Defect IDs: DEF-002, DEF-004, DEF-010, DEF-011, DEF-012, DEF-017, DEF-018, DEF-020

Dependencies: F01-001

Priority: CRITICAL

Risk: HIGH

Write scope:

- `scripts/progress_contract.py`
- new `scripts/workflow_contract.py`, which owns state-transition, handoff, revision, and cross-record validation;
  keep `scripts/progress_contract.py` responsible for flat frontmatter parsing and single-pointer field validation
- `tests/unit/test_progress_contract.py`
- new `tests/unit/test_workflow_contract.py`

Expected implementation:

1. Keep parsing standard-library only.
2. Parse flat YAML frontmatter deterministically.
3. Validate exact required fields, types, enums, nulls, slugs, and ISO timestamps.
4. Validate stage/status/owner/required-skill relations.
5. Validate writer lock coherence.
6. Validate monotonic and synchronized revisions when previous state is provided.
7. Validate canonical handoff frontmatter and body sections.
8. Emit stable, testable error codes or message prefixes.
9. Expose reusable functions imported by stage validators.

Acceptance:

- [ ] Every allowed state has a positive test.
- [ ] Every forbidden state relation has a negative test.
- [ ] `next_skill`, v2 contract, legacy stages, and nested records are rejected.
- [ ] Error output identifies the violated field or invariant.
- [ ] No third-party dependency is added.

Rollback:

- Revert validator and its tests as one unit.

Escalation:

- Stop before adding PyYAML, jsonschema, or another dependency.

#### F01-003 - Repair canonical templates and artifact paths

Requirement IDs: REQ-002, REQ-007 through REQ-015, REQ-027

Defect IDs: DEF-001, DEF-006, DEF-007

Dependencies: F01-001, F01-002

Priority: CRITICAL

Risk: MEDIUM

Write scope:

- `skills/create-spec-driven-plan/assets/PROGRESS.template.md`
- all handoff templates under `skills/*/assets/`
- routing artifact templates
- investigation artifact templates
- review and execution templates affected by canonical paths
- template instantiation tests

Expected implementation:

1. Replace legacy fields and stages with canonical values.
2. Ensure template frontmatter satisfies schemas after placeholders are replaced.
3. Ensure every handoff body contains identification, summary, artifact inventory, preserved decisions,
   allowed open questions, blockers, consumer write scope, forbidden files, commands/results, and stop instruction.
4. Set not-yet-ready templates to `NOT_READY` and non-passing validation state.
5. Normalize paths according to DEC-002 through DEC-005.
6. Add the review-waived implementation-to-release template.
7. Instantiate every template in tests and validate the result.

Acceptance:

- [ ] Every canonical template produces a valid artifact after fixture substitution.
- [ ] No live template contains v2 aliases.
- [ ] No two skills claim conflicting canonical paths.
- [ ] All template local links resolve.

Rollback:

- Revert templates and fixture updates together.

Escalation:

- Stop if two active skills require ownership of the same writable artifact.

#### F01-004 - Make discovery and planning inputs strict and complete

Requirement IDs: REQ-001, REQ-003, REQ-012 through REQ-018

Defect IDs: DEF-002, DEF-003, DEF-005, DEF-012, DEF-015

Dependencies: F01-002, F01-003

Priority: CRITICAL

Risk: HIGH

Write scope:

- brainstorm validator and affected templates/references
- investigation validator and affected templates/references
- UX audit validator and affected templates/references
- planning validator and affected templates/references
- discovery/planning fixtures and tests

Expected implementation:

1. Remove all live v2 aliases.
2. Import shared contract validation.
3. Implement an explicit planning input matrix.
4. Support brainstorm-only, investigation-only, UX-only, approved combinations, and compact brief.
5. Validate source-specific revisions without requiring absent unrelated handoffs.
6. Require user approval before converting UX recommendations into requirements.
7. Reject compact briefs containing unresolved structural questions.

Required test matrix:

| Case | Expected |
|---|---|
| Valid brainstorm handoff | PASS |
| Valid investigation handoff without brainstorm | PASS |
| Valid UX handoff with product approval | PASS |
| Valid combined discovery | PASS |
| Valid bounded compact brief | PASS |
| Stale revision | FAIL |
| Missing required approval | FAIL |
| Structural question in compact brief | FAIL |
| V2 alias in new artifact | FAIL |

Acceptance:

- [ ] Every advertised planning entry mode has a passing fixture.
- [ ] Every unsafe variant has a failing fixture with asserted reason.
- [ ] Planning does not silently invent absent product decisions.

Rollback:

- Revert each discovery validator only with its matching fixtures and templates.

Escalation:

- Return to discovery if the fixture demonstrates missing product intent rather than validator behavior.

#### F01-005 - Make routing, execution, review, and release strict

Requirement IDs: REQ-001 through REQ-011, REQ-027 through REQ-035, REQ-043, REQ-044

Defect IDs: DEF-004, DEF-007, DEF-012, DEF-016, DEF-017

Dependencies: F01-002, F01-003

Priority: CRITICAL

Risk: HIGH

Write scope:

- validators and references for routing, execution, review, and release; any template correction must reopen
  F01-003 through change control
- corresponding integration fixtures and tests

Expected implementation:

1. Remove legacy path and state fallbacks.
2. Validate exact task-to-assignment coverage.
3. Validate executor and reviewer against registered model IDs.
4. Validate dependency-ready batches and write locks.
5. Validate actual task completion evidence and blocker requirements.
6. Validate fresh implementation handoff at review entry.
7. Implement review-required and review-waived release paths.
8. Validate release gate evidence and accepted-risk ownership.
9. Validate return transitions for changes, reroute, replan, investigation, and brainstorm.

Required scenario tests:

- normal required-review path;
- explicitly waived review path;
- bounded correction loop;
- reroute loop;
- replan loop;
- task blocker;
- stale revision;
- active wrong model;
- two-writer conflict;
- release gate without evidence;
- accepted risk without owner.

Acceptance:

- [ ] Complete transition chains pass without manual edits.
- [ ] Every invalid chain fails at the first violated guard.
- [ ] Review cannot approve with open blocking/high findings.
- [ ] Release cannot pass a gate with empty or non-resolving evidence.

Rollback:

- Revert validator, templates, tests, and status expectations as a coordinated unit.

Escalation:

- Stop if reviewer policy cannot be determined from routing artifacts.

#### F01-006 - Make repository validation prove workflow integrity

Requirement IDs: REQ-036 through REQ-042

Defect IDs: DEF-007, DEF-008, DEF-009, DEF-013, DEF-014, DEF-019, DEF-020

Dependencies: F01-003, F01-004, F01-005

Priority: CRITICAL

Risk: MEDIUM

Write scope:

- `scripts/validate_repository.py`
- `scripts/validate_catalog.py`
- catalog files
- migration documentation
- README and AGENTS factual references
- repository-level tests and fixtures

Expected implementation:

1. Correct catalog status, output paths, and stale notes.
2. Remove obsolete advisor exceptions where migration does not require them.
3. Validate catalog `produces` paths against skill contracts.
4. Validate schemas and canonical template instances.
5. Run representative stage validators from repository validation.
6. Add complete greenfield, brownfield, UX, compact, review, and release fixture chains.
7. Add negative fixtures for stale revisions, aliases, placeholders, path drift, and lock conflicts.
8. Ensure tests assert exit codes and specific failure reasons, not only text presence.

Acceptance:

- [ ] Repository validation catches every DEF-001 through DEF-020 regression class.
- [ ] All valid end-to-end fixtures pass.
- [ ] All invalid fixtures fail for expected reasons.
- [ ] Catalog, README, contracts, and actual files agree.
- [ ] Phase F01 gate is recorded as PASS.

Rollback:

- Revert repository gate only if the entire strict contract repair is reverted.

Escalation:

- Stop if a passing result depends on tolerating unrelated validator failures.

### Phase F02 - Specification quality and user experience

#### Entry gate

- F01-006 PASS.
- No live v2 aliases outside migration.
- Complete workflow fixtures green.

#### F02-001 - Add project governance and governance checks

Requirement IDs: REQ-019, REQ-020

Dependencies: F01-006

Priority: HIGH

Risk: MEDIUM

Write scope:

- new governance template under planning assets
- planning and brainstorm instructions/references
- plan validator and tests
- tests and fixtures listed for F02-001 in the exact manifest; final catalog synchronization belongs to F03-003

Expected implementation:

1. Define governance version, principles, authority, rationale, amendment process, and exceptions.
2. Add `plan/GOVERNANCE-CHECK.md`.
3. Require checks before and after technical design for applicable principles.
4. Treat unresolved `MUST` conflicts as blocking.
5. Permit documented exceptions only with authority and rationale.

Acceptance:

- [ ] Governance can be absent only when profile/rules explicitly permit it.
- [ ] A violated `MUST` blocks plan validation.
- [ ] User authority and security precedence are documented.
- [ ] Template placeholders cannot survive `PLAN_VALIDATED`.

Rollback:

- Remove governance capability without restoring any F01 defects.

Escalation:

- Stop on conflict between governance, law, security, and explicit user authority.

#### F02-002 - Generate the compact product specification

Requirement IDs: REQ-013 through REQ-018, REQ-045

Dependencies: F02-001

Priority: HIGH

Risk: MEDIUM

Write scope:

- new `SPEC.template.md`
- planning skill and method
- planning validator
- traceability template
- fixtures and tests

Expected implementation:

1. Generate `plan/SPEC.md` from validated discovery.
2. Preserve discovery IDs and source authority.
3. Add prioritized independently valuable stories.
4. Add Given/When/Then acceptance scenarios.
5. Add functional and quality requirements with stable IDs.
6. Add measurable outcomes, edge cases, assumptions, non-goals, and open decisions.
7. Validate that technical implementation details do not leak into product requirements unless explicit constraints.

Acceptance:

- [ ] A non-technical stakeholder can understand the first release.
- [ ] Every P1 story has independent value and acceptance scenarios.
- [ ] Every requirement traces to discovery evidence or an identified planner proposal.
- [ ] `SPEC.md` does not replace detailed discovery.

Rollback:

- Remove only the derived spec capability and related validation.

Escalation:

- Return to discovery if a story requires an unconfirmed actor, outcome, or product rule.

#### F02-003 - Add incremental clarification

Requirement IDs: REQ-018, REQ-045

Dependencies: F02-002

Priority: HIGH

Risk: MEDIUM

Write scope:

- brainstorm and planning instructions/references
- brainstorm and spec templates
- validators and tests for clarification records

Expected implementation:

1. Implement the protocol in Section 15.
2. Persist each answer immediately with stable question ID, source, authority, and revision.
3. Keep one question per interaction.
4. Re-evaluate readiness after each answer.
5. Treat five questions as a checkpoint, not a hard completeness limit.
6. Prevent contradictory or duplicate clarification records.

Acceptance:

- [ ] Already answered questions are not repeated.
- [ ] Recommendations remain proposals until accepted.
- [ ] Structural ambiguity blocks plan validation.
- [ ] Context loss after any answer does not lose the decision.

Rollback:

- Preserve recorded user decisions even if the interaction feature is reverted.

Escalation:

- Stop when the answer changes product intent and return ownership to brainstorm.

#### F02-004 - Add requirements-quality checklists

Requirement IDs: REQ-021 through REQ-023

Dependencies: F02-003

Priority: HIGH

Risk: LOW

Write scope:

- new checklist template
- planning skill and validator
- checklist tests and fixtures

Expected implementation:

1. Add domain checklist files under `plan/checklists/`.
2. Use stable `CHK-*` IDs.
3. Require source or gap markers.
4. Separate requirements-quality questions from implementation tests.
5. Support profile-aware applicable domains.
6. Re-evaluate checklist state after material spec changes.

Acceptance:

- [ ] No checklist item instructs executing implementation behavior.
- [ ] Every active checklist item has traceability.
- [ ] Critical unchecked items block plan validation.
- [ ] Advisory items are explicitly marked and do not masquerade as blockers.

Rollback:

- Remove checklist gates and templates without changing requirement or task IDs.

Escalation:

- Stop if a checklist item introduces a new product requirement rather than detecting a gap.

#### F02-005 - Add persistent cross-artifact consistency analysis

Requirement IDs: REQ-024 through REQ-026

Dependencies: F02-004

Priority: HIGH

Risk: HIGH

Write scope:

- new consistency report template
- new `skills/create-spec-driven-plan/scripts/analyze_plan.py`; deterministic cross-artifact inventory and
  reporting logic belongs here, while `validate_plan.py` invokes it and enforces its blocking result
- planning validator integration
- analysis tests and fixtures

Expected implementation:

1. Build requirement, story, task, decision, governance, and path inventories.
2. Calculate requirement-to-task coverage.
3. Detect deterministic structural defects.
4. Produce stable finding IDs and severity.
5. Separate blocking mechanical results from advisory semantic findings.
6. Persist metrics and findings in `plan/CONSISTENCY-REPORT.md`.
7. Require remediation or explicit disposition before routing.

Acceptance:

- [ ] Uncovered active requirement blocks.
- [ ] Orphan implementation task blocks.
- [ ] Dependency cycle blocks.
- [ ] Stale revision blocks.
- [ ] Ambiguity and terminology findings are reported with locations.
- [ ] Report regeneration is deterministic for unchanged artifacts where mechanical findings are concerned.

Rollback:

- Remove analysis capability without weakening F01 contract validation.

Escalation:

- Do not convert probabilistic semantic judgment into a hard gate without explicit confirmation.

#### F02-006 - Strengthen vertical slices and safe parallel eligibility

Requirement IDs: REQ-027 through REQ-030

Dependencies: F02-005

Priority: MEDIUM

Risk: HIGH

Write scope:

- phase and traceability templates
- planning method
- routing templates and rubric
- routing validator and tests

Expected implementation:

1. Require each phase to expose observable user or operational value.
2. Require exact file scopes and independent oracles.
3. Add `parallel_eligible` and rationale fields.
4. Compute file/component lock intersections.
5. Reject parallel eligibility on shared files, unresolved dependencies, global state, migrations, or missing isolation strategy.
6. Preserve single-writer default.

Acceptance:

- [ ] Disjoint, dependency-ready tasks may be labeled eligible.
- [ ] Shared file or global-state tasks are rejected.
- [ ] Eligibility does not itself authorize concurrent writing.
- [ ] Isolated worktree and sequential merge review are documented when concurrency is used.

Rollback:

- Remove eligibility metadata; retain single-writer behavior.

Escalation:

- Stop if concurrent execution is requested without isolation and merge strategy.

#### F02-007 - Add controlled convergence to independent review

Requirement IDs: REQ-031 through REQ-034

Dependencies: F02-005, F02-006

Priority: HIGH

Risk: MEDIUM

Write scope:

- review skill and references
- review and finding templates
- review validator
- return-transition fixtures and tests

Expected implementation:

1. Add gap type to every actionable review finding.
2. Compare actual code with requirement, plan decision, task, acceptance, and governance obligations.
3. Record evidence path for every finding.
4. Return bounded corrections to implementation.
5. Return structural findings to their owning stage.
6. Never edit source or silently append tasks during review.

Acceptance:

- [ ] Each gap type has a tested example.
- [ ] Each return destination has a tested transition.
- [ ] Finding-to-requirement/task traceability is complete.
- [ ] Clean convergence produces review approval without creating empty findings.

Rollback:

- Remove gap-type enhancement while preserving independent review and strict transitions.

Escalation:

- Return to planning when remediation requires new requirements, dependencies, architecture, or write scope.

### Phase F03 - Migration, adoption, and release qualification

#### F03-001 - Harden v2-to-v3 migration

Requirement IDs: REQ-040, REQ-041

Defect IDs: DEF-009

Dependencies: F02-007

Priority: HIGH

Risk: HIGH

Write scope:

- `scripts/migrate_v2_to_v3.py`
- migration docs
- migration fixtures and tests

Expected implementation:

1. Add dry-run manifest of every proposed change.
2. Record source hashes and revisions.
3. Refuse migration while a writer lock is active.
4. Map known aliases exactly once.
5. Stop on unknown states instead of guessing.
6. Validate strict v3 output before success.
7. Make a second migration run a no-op.
8. Preserve modified user artifacts.

Acceptance:

- [ ] Dry run makes no changes.
- [ ] Repeated migration is idempotent.
- [ ] Unknown state stops safely.
- [ ] Interrupted migration has documented recovery.
- [ ] Rollback does not overwrite post-migration user changes.

Rollback:

- Restore only captured originals whose current hashes still match expected migrated output.

Escalation:

- Stop on unknown legacy status, slug collision, or active writer lock.

#### F03-002 - Add deterministic workflow scaffolding

Requirement IDs: REQ-036, REQ-039

Dependencies: F03-001

Priority: MEDIUM

Risk: MEDIUM

Write scope:

- new `scripts/init_workflow.py`
- initialization templates/tests/docs

Expected implementation:

1. Implement this exact CLI:

   ```text
   python scripts/init_workflow.py --root <repository-root> --project-id <stable-id> --project-slug <kebab-slug> --profile <compact|standard|critical> --discovery <brainstorm|codebase|ux> [--dry-run] [--timestamp <ISO-8601-UTC>]
   ```

2. All named arguments except `--dry-run` and `--timestamp` are required. `--timestamp` exists for deterministic
   tests and otherwise defaults to current UTC. Stdout is one JSON object with sorted keys:

   ```json
   {
     "created": ["<sorted relative paths>"],
     "discovery": "brainstorm|codebase|ux",
     "dry_run": false,
     "profile": "compact|standard|critical",
     "progress": "docs/ai/<slug>/PROGRESS.md",
     "project_id": "<stable-id>",
     "project_slug": "<slug>",
     "workflow_root": "docs/ai/<slug>"
   }
   ```

3. Create these common files: `PROGRESS.md`, `SOURCE-REGISTER.md`, `CONTEXT-INDEX.md`, and `GLOSSARY.md`.
4. For `brainstorm`, additionally create `discovery/brainstorm/BRAINSTORM.md`.
5. For `codebase`, additionally create `discovery/codebase/INVESTIGATION.md` and
   `discovery/codebase/EVIDENCE.md`.
6. For `ux`, additionally create `discovery/ux/SITEMAP.md`, `discovery/ux/COVERAGE.md`, and
   `discovery/ux/UX-AUDIT.md`.
7. Do not create a handoff at initialization because discovery is not ready.
8. Initialize progress fields exactly as follows:

   ```yaml
   workflow_contract: skill-team/v3
   project_id: <argument>
   project_slug: <argument>
   workflow_profile: <argument>
   stage: DISCOVERY
   status: <BRAINSTORM_IN_PROGRESS|CODEBASE_INVESTIGATION_IN_PROGRESS|UX_AUDIT_IN_PROGRESS>
   stage_owner: <discovery skill selected by mode>
   required_skill: <same discovery skill>
   successor_skill: create-spec-driven-plan
   handoff_status: NOT_READY
   discovery_revision: 1
   plan_revision: 0
   routing_revision: 0
   implementation_revision: 0
   review_revision: 0
   release_revision: 0
   active_artifact: <canonical discovery artifact selected by mode>
   active_task: null
   active_batch: null
   active_executor_model: null
   active_reviewer_model: null
   writer_skill: <same discovery skill>
   writer_task: null
   next_action: Complete the selected discovery artifact
   blockers: NONE
   last_validation_command: NONE
   last_validation_result: NOT_RUN
   updated_at: <timestamp>
   ```

9. Generate all files in a sibling temporary directory, validate them, and atomically rename that directory to
   `docs/ai/<slug>`. On any failure, remove only the temporary directory and leave no target partial output.
10. Refuse an existing target directory without modifying it. Use exit `1` with `STV3-E025-SCOPE` for collision,
    exit `1` with the applicable validation code for invalid values, and exit `2` with `STV3-E030-INTERNAL` for
    invalid CLI usage or I/O failure.
11. `--dry-run` performs validation and emits the same JSON with `dry_run: true` but creates no target or temporary
    residue.
12. Keep implementation standard-library only and reject symlink/path traversal outside `--root`.

Acceptance:

- [ ] Generated workflow passes strict initial-state validation.
- [ ] Existing files are never overwritten silently.
- [ ] Windows and POSIX path behavior is tested.
- [ ] Dry run and failed validation leave no partial output.
- [ ] Stdout and error codes match the specified contracts byte-for-byte after timestamp/path normalization.

Rollback:

- Remove only files generated by the command when their hashes remain unchanged.

Escalation:

- Do not expand this task into a Spec Kit-style package manager or workflow engine.

#### F03-003 - Align documentation, adapters, and release evidence

Requirement IDs: REQ-039, REQ-042 through REQ-044

Dependencies: all prior tasks

Priority: HIGH

Risk: MEDIUM

Write scope:

- `README.md`
- `CONTRIBUTING.md`
- `AGENTS.md`
- `adapters/*/README.md`
- `SECURITY.md`
- `.github/workflows/validate-skills.yml`
- release baseline evidence

Expected implementation:

1. Document exact entry modes and canonical paths.
2. Document clarification, spec, checklist, analysis, review, and release behavior.
3. Document migration and rollback.
4. Update adapter instructions without introducing platform-specific core behavior.
5. Add CI execution of the complete repository validation.
6. Attribute Spec Kit as conceptual inspiration where appropriate.
7. Record final requirement closure and command transcripts.

Acceptance:

- [ ] Documentation examples pass validators.
- [ ] No stale skill status or path remains.
- [ ] CI runs complete strict validation.
- [ ] Requirements whose final implementing task is F03-003 or earlier are VERIFIED or explicitly DEFERRED.
- [ ] Requirements requiring F03-004 rollout evidence remain `IN_PROGRESS` and name F03-004 as final owner; they
  MUST NOT be prematurely marked verified or deferred.

Rollback:

- Documentation may be reverted independently only if it still describes actual behavior after reversion.

Escalation:

- Stop if an adapter requires core contract divergence.

#### F03-004 - Execute rollout qualification waves

Requirement IDs: REQ-036 through REQ-044

Dependencies: F03-003

Priority: CRITICAL

Risk: HIGH

Write scope:

- `tests/integration/test_rollout_qualification.py`
- `tests/fixtures/rollout-sample/`
- `baseline/rollout/`
- task evidence from the inherited envelope

Expected implementation:

1. Create one sanitized controlled sample workflow at `tests/fixtures/rollout-sample/`.
2. Execute W1 strict validation in report-only mode without changing the sample.
3. Copy the sample to a disposable W2 workspace under `baseline/rollout/W2/workspace/`, run migration dry run,
   perform migration, validate, and run migration again to prove idempotence.
4. Initialize a new W3 workflow in `baseline/rollout/W3/workspace/` and validate governance, SPEC,
   clarification, checklist, and consistency artifacts.
5. Execute required-review and review-waived W4 fixture paths and validate convergence returns.
6. Rehearse rollback from copied checkpoint content in W5, restore the qualified state, and run the final suite.
7. Record metrics and an independently reviewed `PROMOTION.md` for each wave.
8. Stop at the first failed wave; later promotion files MUST remain absent.

Expected wave artifacts:

```text
baseline/rollout/W1/{METRICS.md,PROMOTION.md}
baseline/rollout/W2/{METRICS.md,PROMOTION.md,workspace/}
baseline/rollout/W3/{METRICS.md,PROMOTION.md,workspace/}
baseline/rollout/W4/{METRICS.md,PROMOTION.md,workspace/}
baseline/rollout/W5/{METRICS.md,PROMOTION.md,workspace/}
```

Every `PROMOTION.md` records wave, input revision, commands, metrics, blockers, executor, independent reviewer,
decision (`PROMOTE` or `STOP`), and timestamp.

Acceptance:

- [ ] W1 proves strict report-only validation does not mutate its input fixture.
- [ ] W2 proves migration dry run, strict output, and idempotence.
- [ ] W3 proves all specification-quality capabilities on a new workflow.
- [ ] W4 proves both review policies and every convergence return owner.
- [ ] W5 proves content-based rollback and complete final restoration.
- [ ] Every promoted wave has an independent reviewer and all required metrics.
- [ ] A failed wave prevents later promotion.
- [ ] After W5, every REQ-* entry is `VERIFIED` or explicitly `DEFERRED` with owner, rationale, and no violated gate.

Rollback:

- Delete only disposable rollout workspaces and restore F03-004 pre-change files from its checkpoint. Preserve
  failed wave metrics and promotion decision as evidence unless they contain prohibited data.

Escalation:

- Stop on sample mutation during W1, migration non-idempotence, rollback hash mismatch, missing reviewer, or any
  critical/high unresolved finding.

## 20. Dependency graph

```text
F00-001
  -> F01-001
       -> F01-002
            -> F01-003
                 -> F01-004
                 -> F01-005
                      -> F01-006 [MANDATORY V3 CONSISTENCY GATE]
                           -> F02-001
                                -> F02-002
                                     -> F02-003
                                          -> F02-004
                                               -> F02-005
                                                    -> F02-006
                                                    -> F02-007
                                                         -> F03-001
                                                              -> F03-002
                                                                   -> F03-003
                                                                        -> F03-004
```

F01-004 and F01-005 may be developed independently only if they use disjoint files and are merged sequentially
after shared validator changes. This is eligibility, not automatic permission for concurrent writers.

F03 begins only after F02-007. `F03-002` is required in this program; it is intentionally bounded to deterministic
scaffolding and MUST NOT expand into a workflow engine. Therefore `F03-003` has no optional unresolved predecessor.

## 21. Requirement traceability

| Requirement range | Primary tasks | State | Evidence |
|---|---|---|---|
| REQ-001 - REQ-011 | F01-001, F01-002, F01-003, F01-005 | VERIFIED | `baseline/validator-runs/F01-001.md` through `F01-005.md`; F03-003 repository validation |
| REQ-012 | F01-004 | VERIFIED | `baseline/validator-runs/F01-004.md`; F03-003 repository validation |
| REQ-013 - REQ-018 | F01-004, F02-002, F02-003 | VERIFIED | `baseline/validator-runs/F01-004.md`, `F02-002.md`, `F02-003.md`; F03-003 repository validation |
| REQ-019 - REQ-020 | F02-001 | VERIFIED | `baseline/validator-runs/F02-001.md`; F03-003 repository validation |
| REQ-021 - REQ-023 | F02-004 | VERIFIED | `baseline/validator-runs/F02-004.md`; F03-003 repository validation |
| REQ-024 - REQ-026 | F02-005 | VERIFIED | `baseline/validator-runs/F02-005.md`; F03-003 repository validation |
| REQ-027 - REQ-030 | F01-003, F01-005, F02-006 | VERIFIED | `baseline/validator-runs/F01-003.md`, `F01-005.md`, `F02-006.md`; F03-003 repository validation |
| REQ-031 - REQ-034 | F01-005, F02-007 | VERIFIED | `baseline/validator-runs/F01-005.md`, `F02-007.md`; F03-003 repository validation |
| REQ-035 | F01-001, F01-003, F01-005 | VERIFIED | `baseline/validator-runs/F01-001.md`, `F01-003.md`, `F01-005.md`; F03-003 repository validation |
| REQ-036 - REQ-039 | F00-001, F01-006, F03-002, F03-003, F03-004 | VERIFIED | `baseline/validator-runs/F01-006.md`, `F03-002.md`, `F03-003.md`, and `F03-004.md`; W1-W5 promoted. |
| REQ-040 | F03-001, F03-004 | VERIFIED | `baseline/validator-runs/F03-001.md` and `F03-004.md`; W2 migration and W5 restoration passed. |
| REQ-041 | Every F00-F03 task through the inherited envelope and checkpoint matrix | VERIFIED | Per-task rollback evidence and F03-004 W5 content-based rollback/restoration evidence. |
| REQ-042 - REQ-044 | F00-001, F01-006, F03-003, F03-004 | VERIFIED | `baseline/validator-runs/F03-003.md` and `F03-004.md`; final CI, release-gate, accepted-risk, and W1-W5 evidence passed. |
| REQ-045 | F02-002, F02-003 | VERIFIED | `baseline/validator-runs/F02-002.md`, `F02-003.md`; F03-003 repository validation |

Allowed closure states: `NOT_STARTED`, `IN_PROGRESS`, `VERIFIED`, `DEFERRED`.

`DEFERRED` requires owner, rationale, target release, and proof that deferral does not violate a mandatory gate.

## 22. Defect-to-task traceability

| Defect | Fixing tasks |
|---|---|
| DEF-001 | F01-003 |
| DEF-002 | F01-002, F01-004 |
| DEF-003 | F01-001, F01-004 |
| DEF-004 | F01-002, F01-005 |
| DEF-005 | F01-004 |
| DEF-006 | F01-001, F01-003 |
| DEF-007 | F01-003, F01-005, F01-006 |
| DEF-008 | F01-006 |
| DEF-009 | F01-006, F03-001 |
| DEF-010 | F01-001, F01-002 |
| DEF-011 | F01-002 |
| DEF-012 | F01-002, F01-004, F01-005 |
| DEF-013 | F00-001, F01-006 |
| DEF-014 | F01-006 |
| DEF-015 | F01-001, F01-004 |
| DEF-016 | F01-001, F01-003, F01-005 |
| DEF-017 | F01-001, F01-002 |
| DEF-018 | F01-001, F01-002 |
| DEF-019 | F01-006 |
| DEF-020 | F01-001, F01-002, F01-006 |

## 23. Test strategy

### 23.1 Unit tests

- frontmatter parsing;
- exact field validation;
- state relation validation;
- transitions;
- revision monotonicity;
- handoff types and body sections;
- task schema completeness;
- dependency graph cycles;
- path normalization;
- catalog path agreement;
- checklist ID and traceability parsing;
- consistency metrics.

### 23.2 Integration fixtures

- greenfield brainstorm to release;
- brownfield investigation to release;
- UX audit with approval to plan;
- combined discovery;
- compact bounded change;
- required review;
- waived review;
- bounded correction loop;
- reroute loop;
- replan loop;
- return to investigation;
- return to brainstorm;
- blocked task;
- blocked release;
- post-release return.

### 23.3 Negative fixtures

- v2 contract in live artifact;
- forbidden alias;
- invalid stage/status pair;
- wrong required skill;
- conflicting writer;
- stale handoff revision;
- missing artifact;
- broken local link;
- ready placeholder;
- missing validation result;
- requirement without task;
- task without requirement;
- dependency cycle;
- complete task without evidence;
- blocked task without blocker;
- routing model not registered;
- review approval with blocking finding;
- release gate without evidence;
- accepted risk without owner.

### 23.4 Mutation expectation

For every major invariant, temporarily introduce a representative defect in a fixture and prove repository
validation fails. Do not mutate production files during normal tests.

## 24. Migration plan

1. Freeze and inventory existing consumer artifacts.
2. Run `scripts/migrate_v2_to_v3.py --dry-run`.
3. Record hashes, workflow version, revisions, and active writer state.
4. Refuse migration with an active writer.
5. Back up only files that will change.
6. Convert known aliases exactly once.
7. Do not emit compatibility aliases in migrated output.
8. Stop on unknown state or ambiguous ownership.
9. Run strict stage and repository validators.
10. Mark migration complete only after all outputs pass.
11. Run migration again and require no changes.

## 25. Rollback strategy

- Section 18.4 defines the required phase checkpoints and takes precedence over shorter task-level rollback
  notes.
- A valid checkpoint contains recoverable file contents at original relative paths plus `MANIFEST.sha256`;
  hashes without copied content are not a rollback mechanism.
- In F01, a task-level rollback note applies only to unaccepted local edits before the coordinated checkpoint.
  Once an F01 task is accepted, rollback MUST use the complete coordinated F01 file set and verification suite.
- F01 is one coordinated contract repair release. Contract, schemas, templates, validators, fixtures, and catalog
  MUST not be rolled back independently into a mixed state.
- Each F02 capability MUST be independently removable without restoring F01 defects.
- Migration rollback restores original files only when current hashes prove they were not modified after migration.
- User-modified artifacts are never overwritten during rollback.
- Evidence and migration reports are preserved after rollback.
- No destructive Git command is part of rollback instructions.

### 25.1 Rollout strategy

Rollout is progressive and proof-driven. A later wave MUST NOT begin when the previous wave has unresolved
blocking findings.

| Wave | Owner | Controlled input and evidence | Command | Promotion gate |
|---|---|---|---|---|
| W0 - Baseline | F00-001 executor + reviewer | Repository baseline; `baseline/validator-runs/F00-001.md` | Commands in F00-001 | Baseline evidence approved |
| W1 - Strict validation shadow mode | F03-004 executor + reviewer | `tests/fixtures/rollout-sample/`; `baseline/rollout/W1/` | `python -m unittest tests.integration.test_rollout_qualification.RolloutQualificationTest.test_w1_shadow -v` | Valid fixtures pass, defect fixtures fail, input hash unchanged |
| W2 - Canonical v3 internal adoption | F03-004 executor + reviewer | Disposable copy at `baseline/rollout/W2/workspace/`; metrics and decision beside it | `python -m unittest tests.integration.test_rollout_qualification.RolloutQualificationTest.test_w2_migration -v` | G1-G3, dry run, strict migration, second-run no-op |
| W3 - Specification capabilities | F03-004 executor + reviewer | New workflow at `baseline/rollout/W3/workspace/` | `python -m unittest tests.integration.test_rollout_qualification.RolloutQualificationTest.test_w3_specification -v` | Governance, SPEC, clarification, checklist, analysis, and F01 regression pass |
| W4 - Review convergence | F03-004 executor + reviewer | Review fixtures at `baseline/rollout/W4/workspace/` | `python -m unittest tests.integration.test_rollout_qualification.RolloutQualificationTest.test_w4_review -v` | Required/waived review and all owner returns pass |
| W5 - General release | F03-004 executor + independent release reviewer | Qualified copy and checkpoint at `baseline/rollout/W5/workspace/` | `python -m unittest tests.integration.test_rollout_qualification.RolloutQualificationTest.test_w5_release -v` | G6, rollback rehearsal, restored hashes, final repository validation |

Rollout rules:

- Existing consumer artifacts are never rewritten merely because the repository was updated.
- Migration is explicit and preceded by dry run and backup.
- Shadow-mode strict validation reports defects but does not change consumer state.
- Promotion metrics include valid-fixture pass rate, invalid-fixture rejection rate, migration idempotence, and
  zero unresolved critical/high review findings.
- A failed promotion restores the applicable complete checkpoint and reruns the previous wave's validation.
- There is no percentage-based production rollout in this repository-only program; consumer maintainers opt in
  through explicit migration.

## 26. Risk register

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| RISK-001 | Strict validators break consumers that created v3 files with v2 aliases. | HIGH | HIGH | Dry-run migrator and explicit diagnostics; no silent compatibility. |
| RISK-002 | Contract and templates are changed independently. | MEDIUM | CRITICAL | Coordinated F01 scope and generated-template validation. |
| RISK-003 | Spec Kit concepts blur Skill Team stage ownership. | MEDIUM | HIGH | Extend existing owners; preserve stop boundaries. |
| RISK-004 | AI semantic analysis creates nondeterministic gates. | MEDIUM | HIGH | Mechanical checks block; AI findings advisory until confirmed. |
| RISK-005 | Governance conflicts with user authority. | MEDIUM | HIGH | Explicit authority order and exception/escalation process. |
| RISK-006 | Parallel eligibility is interpreted as write permission. | MEDIUM | CRITICAL | Preserve single-writer invariant and require isolation strategy. |
| RISK-007 | Migration overwrites customized artifacts. | LOW | CRITICAL | Hash inventory, dry run, conditional rollback, no overwrite. |
| RISK-008 | Test count rises without behavioral coverage. | MEDIUM | HIGH | Full transitions and negative mutation fixtures. |
| RISK-009 | Path handling breaks Windows consumers. | MEDIUM | MEDIUM | Test artifact POSIX paths and Windows filesystem resolution separately. |
| RISK-010 | Program expands into a workflow engine rewrite. | MEDIUM | HIGH | Enforce non-goals and escalation boundaries. |
| RISK-011 | Compact `SPEC.md` becomes a competing source of truth. | MEDIUM | HIGH | Declare it derived; preserve origins and detailed artifact authority. |
| RISK-012 | Lower-capability executor “fixes” tests instead of behavior. | MEDIUM | HIGH | Exact acceptance, baseline evidence, and prohibition against weakening gates. |

## 27. Release gates

### Gate G1 - Contract coherence

- All statuses and transitions are defined.
- Shared validator enforces all invariants.
- Schemas and contract agree.

### Gate G2 - Artifact coherence

- Every canonical template instantiates successfully.
- Paths and catalog outputs agree.
- No live v2 aliases exist.

### Gate G3 - Workflow interoperability

- Greenfield, brownfield, UX, compact, review-required, and review-waived chains pass.
- No stage requires manual field repair.

### Gate G4 - Specification quality

- Compact spec, clarification, governance, checklist, and consistency report are implemented and tested.
- Structural gaps block routing.

### Gate G5 - Execution and convergence

- Task evidence, blockers, review gap types, and return transitions are validated.
- Review does not mutate implementation.

### Gate G6 - Migration and adoption

- Migrator is dry-runnable and idempotent.
- Documentation and adapters match behavior.
- CI runs strict repository validation.

## 28. Program completion criteria

This improvement program is complete only when all conditions are true:

- [ ] Every DEF-* has a verified fixing task.
- [ ] Every REQ-* is `VERIFIED` or explicitly `DEFERRED` with acceptable rationale.
- [ ] No live validator accepts v2 or forbidden aliases.
- [ ] Every canonical template can produce a valid artifact.
- [ ] Every documented planning entry mode passes.
- [ ] Every allowed transition has a positive test.
- [ ] Every forbidden transition has a negative test.
- [ ] Repository validation catches malformed templates, stale revisions, path drift, invalid locks, and false-ready handoffs.
- [ ] Requirement-to-task and task-to-requirement coverage is 100% for active scope.
- [ ] Critical requirements map to explicit test oracles.
- [ ] Review-required and review-waived release paths are both validated.
- [ ] Migration is dry-runnable, idempotent, and rollback-safe.
- [ ] Catalog, README, contracts, templates, validators, tests, and actual paths agree.
- [ ] Final validation commands and outputs are preserved as release evidence.

## 29. Final validation commands

The executor MUST run at minimum:

```text
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

It MUST also run every stage validator against its valid fixtures and corresponding expected-failure fixtures.
The final report MUST list each command, exit code, result, and evidence path.

## 30. Planner stop instruction

This document completes the planning operation only. It does not itself start implementation.

The next operational step is for the human operator or primary maintenance agent to issue the exact standalone
authorization in Section 18.5 for task `F00-001` to an executor capable of repository inspection and test
authoring. The executor MUST verify the plan hash, start at the baseline, respect the exact task boundary,
produce evidence, and stop after `F00-001`.

No executor is authorized to skip directly to Spec Kit-inspired capabilities before the strict v3 consistency
gate in `F01-006` passes.
