# Product Specification: Saved searches

## Identification

- Plan revision: 2
- Derived from: discovery/brainstorm/BRAINSTORM.md revision 1

## Problem and intended outcome

People need to return to a useful search without recreating it; saved searches are available after creation.

## Actors and authority

- Account holder: creates and uses their own saved searches.

## Scope of the first usable release

An account holder can save one search and run it later.

## Non-goals

- Sharing searches with other accounts.

## Prioritized user journeys

### US-001 - Save and reuse a search (P1)

#### Why this priority

It provides the first repeat-use benefit.

#### Independent value

An account holder can reuse a saved search without recreating its criteria.

#### Acceptance scenarios

1. Given an account holder has search criteria, when they save the search, then it appears in their saved-search list.

## Functional requirements

- REQ-001: The account holder can save search criteria under a name.
  - Origin: CR-001 / SRC-001
  - Priority: P1
  - Release: R1
  - Oracle: A saved search appears in the account holder's list.
  - State: ACTIVE
  - Implementation constraint: NONE

## Quality requirements

- REQ-002: A saved search is visible only to its account holder.
  - Origin: CR-002 / SRC-001
  - Priority: P1
  - Release: R1
  - Oracle: A different account holder cannot find the saved search.
  - State: ACTIVE
  - Implementation constraint: NONE

## Key entities and lifecycle

A saved search is created, available, and deleted by its account holder.

## Edge, failure, and recovery cases

- If a name is already used, the account holder is asked to choose another name.

## Success criteria

- A saved search can be created and reused in the first release.

## Assumptions

- ASM-001: Search criteria are already available to the account holder.

## Rejected and deferred options

- Shared searches are deferred until a later release.

## Open decisions

- NONE

## Source and revision references

- SRC-001: validated brainstorm revision 1.
