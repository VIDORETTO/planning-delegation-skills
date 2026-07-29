# Product Specification: Saved searches

## Identification

- Plan revision: 2

## Problem and intended outcome

People need to return to a useful search without recreating it.

## Actors and authority

- Account holder: creates saved searches.

## Scope of the first usable release

An account holder can save a search.

## Non-goals

- Search sharing.

## Prioritized user journeys

### US-001 - Save a search (P1)

#### Why this priority

It provides repeat-use value.

#### Independent value

An account holder keeps a useful search.

#### Acceptance scenarios

1. Given search criteria, when an account holder saves them, then the saved search is available.

## Functional requirements

- REQ-001: The product stores saved searches in PostgreSQL.
  - Origin: CR-001 / SRC-001
  - Priority: P1
  - Release: R1
  - Oracle: The saved search is available.
  - State: ACTIVE
  - Implementation constraint: NONE

## Quality requirements

- REQ-002: A saved search is visible only to its account holder.
  - Origin: CR-002 / SRC-001
  - Priority: P1
  - Release: R1
  - Oracle: Another account cannot access it.
  - State: ACTIVE
  - Implementation constraint: NONE

## Key entities and lifecycle

A saved search is created and available.

## Edge, failure, and recovery cases

- Duplicate names are rejected.

## Success criteria

- Saved searches are reusable.

## Assumptions

- ASM-001: Search exists.

## Rejected and deferred options

- Sharing is deferred.

## Open decisions

- NONE

## Source and revision references

- SRC-001: validated discovery.
