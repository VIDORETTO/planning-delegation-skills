# Finding classification

Use exactly these labels, in English, for every finding — they are contract vocabulary, not free
text.

| Label | Meaning | Effect on outcome |
|---|---|---|
| `BLOCKING` | The work does not satisfy the plan, breaks a contract, or introduces a security/data-loss risk | Approval is impossible until resolved |
| `HIGH` | A significant defect or regression risk that should be fixed before release, though not an immediate contract break | Approval requires an explicit accepted-risk note, or a bounded fix |
| `MEDIUM` | A real but non-urgent defect, inconsistency, or missing polish | May be deferred with a recorded follow-up |
| `LOW` | Minor, cosmetic, or stylistic observation | Does not block approval |
| `QUESTION` | Genuinely unclear whether something is a defect; needs an answer, not a fix | Route to the owner who can answer it |
| `OUT_OF_SCOPE` | A real observation unrelated to this task's write scope or acceptance criteria | Record for later; do not fold into this review's outcome |

## Deciding the return stage for a BLOCKING or HIGH finding

- If the defect stems from a wrong model assignment, mismatched capability tier, or a batching
  conflict: reroute (`route-ai-work-by-capability`).
- If the defect stems from an incomplete or contradictory task, dependency, acceptance criterion, or
  contract: replan (`create-spec-driven-plan`).
- If the defect stems from a technical assumption that turns out to be wrong: rediscover
  (`investigate-existing-codebase`).
- If the defect is a local implementation mistake within the same write scope and contract: request
  bounded changes back to `execute-routed-task`.

## Writing a finding

Every finding needs: precise location (`path/file.ext:line` or artifact section), what is wrong,
why it matters, and the classification. A finding without a location is not actionable and should be
turned into a `QUESTION` addressed to whoever can supply the missing context instead.

## Never do this

- Never downgrade a `BLOCKING` finding to force an approval.
- Never mark `OUT_OF_SCOPE` findings as resolved by editing the code yourself — record them for the
  appropriate future task.
- Never leave a finding unclassified; every entry in `findings/` carries exactly one label from the
  table above.
