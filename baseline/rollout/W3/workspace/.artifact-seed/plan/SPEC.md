# Product Specification: W3 initialized-workflow check

## Identification

- Plan revision: 1
- Derived from: rollout W3 initialization

## Problem and intended outcome

The initialized workflow needs a bounded specification-quality record.

## Actors and authority

- Rollout owner: authorizes the controlled qualification.

## Scope of the first usable release

The workflow records a validated specification artifact.

## Non-goals

- Shipping application behavior.

## Prioritized user journeys

### US-001 - Inspect qualified workflow evidence (P1)

#### Why this priority

It proves qualification uses the initialized workflow.

#### Independent value

An auditor can inspect the workflow's planning artifacts.

#### Acceptance scenarios

1. Given the initialized workflow, when its plan is validated, then its evidence is internally consistent.

## Functional requirements

- REQ-001: The initialized workflow contains a validated planning record.
  - Origin: SRC-001
  - Priority: P1
  - Release: R1
  - Oracle: The planner validator accepts the workflow artifacts.
  - State: ACTIVE
  - Implementation constraint: NONE

## Quality requirements

- NONE

## Key entities and lifecycle

A workflow is initialized, planned, analyzed, and retained as rollout evidence.

## Edge, failure, and recovery cases

- Missing required planning artifacts block validation.

## Success criteria

- The planning validator and consistency analysis pass.

## Assumptions

- ASM-001: The rollout workspace is controlled evidence.

## Rejected and deferred options

- Detached capability fixtures are not W3 evidence.

## Open decisions

- NONE

## Clarification records

### Q-001

- Question: Must W3 validate artifacts in its initialized workflow?
- Decision key: w3-initialized-workflow
- Scope: PLAN
- Status: ANSWERED
- Asked by: create-spec-driven-plan
- Answer: Yes, artifacts belong to the initialized workflow.
- Source: SRC-001
- Authority: user
- Revision: 1
- Recommendation: Validate the initialized workflow directly.
- Accepted: true
- Supersedes: NONE
- Readiness after answer: READY

## Source and revision references

- W3-INIT: initializer output revision 1.
