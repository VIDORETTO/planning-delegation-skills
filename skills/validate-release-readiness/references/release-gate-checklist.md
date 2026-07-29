# Release gate checklist

Evaluate every gate that applies to the project's `workflow_profile`. Profiles change which
documents are required, never whether a security, privacy, or data-loss gate can be skipped.

## Implementation and review

- Every task in the release scope is `COMPLETE` with recorded evidence.
- Every task whose routing required review has a `REVIEW_APPROVED` outcome, or an explicit,
  owner-approved waiver recorded at routing time.
- A review-required route reaches release only through `REVIEW-TO-RELEASE.md`; a fully waived route
  reaches release only through `IMPLEMENTATION-TO-RELEASE.md`. Exactly one current input is valid.
- No open `BLOCKING`/`HIGH` finding remains in `findings/`.

## Tests

- The full required test suite for the release scope passes, cited with the command and result.
- Coverage gaps identified during investigation or review are either closed or explicitly accepted.

## Security and privacy

- No known unresolved security finding at `BLOCKING`/`HIGH` severity.
- Data handling changes (new fields, new storage, new third-party sharing) have an explicit privacy
  note, not silence.
- Authentication, authorization, and tenancy boundaries touched by this release were reviewed, not
  assumed unaffected.

## Migration and rollback

- Any schema or data migration has a tested rollback path, or is explicitly irreversible with a
  recorded, owner-approved justification.
- Destructive operations are additive-first or behind a flag where feasible.

## Observability

- New failure modes introduced by this release have a way to be detected in production (logging,
  metrics, alerting) — "we will notice if it breaks" is not itself evidence.

## Operational documentation

- Runbook/operational notes exist for any new operational behavior (new job, new external
  dependency, new manual step).

## Accepted risk register

- Every gate that did not fully pass is either fixed or listed here with an explicit owner and
  rationale, review/expiration condition, and resolving evidence citation — never silently omitted.

## Profile guidance

| Profile | Typical scope | Effect |
|---|---|---|
| `compact` | Small, bounded change | Minimum artifact set; all gates above still apply, evaluated briefly |
| `standard` | Medium feature/project | Intermediate artifact set; full gate evaluation expected |
| `critical` | Security, data, migration, architecture, regulated | Full artifact set; no gate above may be waived without a named, accountable owner |
