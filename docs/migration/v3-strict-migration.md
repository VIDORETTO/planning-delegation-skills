# Strict v2 to v3 Migration

Run the migrator against the directory containing a v2 `PROGRESS.md`:

```text
python scripts/migrate_v2_to_v3.py docs/ai/example --dry-run --json
python scripts/migrate_v2_to_v3.py docs/ai/example
```

The dry run writes nothing. Its manifest lists each proposed file, source SHA-256,
expected migrated SHA-256, source revision values, and exact alias changes. Review it
before the non-dry run.

## Safety rules

- Migration refuses an active `writer_skill`, unknown stage/status, ambiguous alias,
  slug/field collision, or output that fails the strict v3 validator.
- Only documented v2 aliases are converted. `next_skill` must exactly match the
  required skill for the mapped state and is removed once.
- Existing non-pointer user artifacts are not rewritten. Regenerate v3 handoffs from
  the migrated pointer rather than guessing their missing v3 provenance.
- A second run is a no-op after a strict v3 pointer exists.

## Interruption and rollback

Before replacement, the migrator writes `.migration-backup/<UTC>/originals/PROGRESS.md`
and `MANIFEST.json`. The replacement is an atomic same-directory rename. If the process
is interrupted, inspect the manifest and run:

```text
python scripts/migrate_v2_to_v3.py --rollback docs/ai/example/.migration-backup/<UTC>
```

Rollback restores an original only when the current file SHA-256 equals the manifest's
expected migrated SHA-256. A changed file is preserved and reported, preventing rollback
from overwriting post-migration user work. Resolve preserved files manually using the
captured original and manifest hashes.
