# Decision and blockers

## Evidence-backed decision format

Every gate row in `RELEASE-READINESS.md` needs three things: the gate, the result, and a citation —
the artifact path, command, or handoff that proves the result. A result without a citation is not a
valid pass; treat it as unresolved.

```text
| Gate | Result | Evidence |
|---|---|---|
| Tests | PASS | `execution/EVIDENCE.md#T-07`, `npm test` output |
| Security | ACCEPTED_RISK | `release/RELEASE-READINESS.md#risk-1`, owner: <name>, rationale: <reason> |
```

## Writing a blocker

For every `RELEASE_BLOCKED` gate:

- name the gate that failed;
- state exactly why it failed (cite the evidence, do not paraphrase from memory);
- name the upstream skill or human decision required to resolve it.

```text
| Gate | Why it fails | Resolved by |
|---|---|---|
| Migration rollback | No rollback path recorded for the schema change in T-04 | execute-routed-task |
| Accepted risk | Security finding FND-003 has no owner | human decision |
```

## Accepting a risk instead of blocking

An accepted risk is a deliberate, visible decision, not a way to avoid writing a blocker. It requires:
an explicit owner (a named person or role, not "the team"), a rationale grounded in the actual
evidence, and — where meaningful — an expiry or follow-up condition. Silence is never an accepted
risk.

## Post-release routing

When observed outcomes diverge from what the release decision expected:

- an unexpected technical failure routes to `investigate-existing-codebase`;
- an unexpected product/business outcome routes to `brainstorm-idea-with-user`;
- a fully expected outcome needs no further routing; record it and close the cycle.

Never silently absorb a divergence into the next release without recording it in
`release/POST-RELEASE.md` first.
