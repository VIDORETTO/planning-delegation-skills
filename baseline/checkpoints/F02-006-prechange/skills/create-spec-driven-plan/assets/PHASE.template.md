# <PHASE_ID> — <TITLE>

## Objective

<OBSERVABLE_VALUE>

## Vertical-slice value

<USER_OR_OPERATIONAL_VALUE_OBSERVABLE_WITHOUT_LATER_PHASES>

## Entry conditions

- <DEPENDENCY_OR_NONE>

## Exit gate

- <MEASURABLE_GATE>

## Non-scope

- <DEFERRED_ITEM>

## Tasks

### [ ] <TASK_ID> — <VERB_AND_OBSERVABLE_RESULT>

Requirement IDs: <REQ_IDS>
Decision IDs: <DEC_IDS_OR_NONE>
Executor: UNASSIGNED
Reviewer: NONE
State: PENDING
Priority: HIGH
Risk: MEDIUM

#### Why this task exists

<RATIONALE>

#### Mandatory reading

- `<CONTRACT_PATH>#<SECTION>`

#### Dependencies

- NONE

#### Write scope

- Allowed files: <PATHS>
- Allowed components: <COMPONENTS>
- Global state: NONE | <STATE_AND_REASON>
- Migration: NONE | <MIGRATION_AND_REASON>

#### Parallel eligibility

- Parallel eligible: false
- Rationale: Single-writer execution is the default; state why this task is or is not independently safe.
- Isolation and merge strategy: NOT_APPLICABLE | ISOLATED_WORKTREE_SEQUENTIAL_MERGE_REVIEW

#### Outside scope

- Do not change: <ITEMS>
- Do not decide: <ITEMS>
- Do not refactor: <ITEMS>

#### Observable objective

<OBSERVABLE_RESULT>

#### Inputs, outputs and errors

- <CONTRACT>

#### Invariants

- <INVARIANT>

#### Security and privacy

- <CONTROL_OR_NOT_APPLICABLE_WITH_REASON>

#### Expected implementation

1. <STEP>
2. <STEP>

#### Test cases

- success: <ORACLE>
- failure: <ORACLE>
- boundary/security: <ORACLE>

#### Independent oracle

<COMMAND_OR_OBSERVATION_THAT_PROVES_THIS_TASK_WITHOUT_ANOTHER_TASK'S_UNVERIFIED_OUTPUT>

#### Acceptance criteria

- [ ] <PROVABLE_CONDITION>
- [ ] required evidence recorded
- [ ] traceability and progress updated

#### Rollback

- <ROLLBACK_OR_NOT_APPLICABLE_WITH_REASON>

#### Required evidence

- Evidence file: <PATH>
- Commands: <COMMANDS>
- Expected output: <EXPECTED_OUTPUT>

#### Escalation

Stop if:

- a required contract is absent;
- a schema or public contract change is required;
- a new architectural decision appears;
- scope must expand.
