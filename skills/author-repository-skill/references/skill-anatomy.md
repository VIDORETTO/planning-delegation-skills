# Skill anatomy

The standard shape every skill in this repository should follow, and why each part exists.

## Directory layout

```text
skills/<skill-name>/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── <topic>.md
├── assets/
│   └── <ARTIFACT>.template.md
└── scripts/
    └── validate_<stage>.py
```

`<skill-name>` is kebab-case and matches the `name` field in `SKILL.md` frontmatter exactly.

## SKILL.md

- Frontmatter contains only `name` and `description` — nothing else. The description is the trigger:
  it should say what to use the skill for, and, in the same breath, what it explicitly does not do.
  A description without an exclusion clause is how two skills end up silently competing for the same
  request later.
- Body target: 100–220 lines for a focused skill; 500 lines is a hard ceiling, not a target. A file
  approaching the ceiling is a sign the skill may be doing two jobs — see
  [overlap-and-boundaries.md](overlap-and-boundaries.md) on splitting.
- Load conditionally: point to `references/` and `assets/` files by relative link instead of inlining
  their full content, so an agent only pulls in what the current step needs.
- State the stop condition explicitly: what this skill produces, and what it does not do even if the
  user asks in the same turn.

## agents/openai.yaml

A short adapter, not a duplicate of `SKILL.md`:

```yaml
interface:
  display_name: "<Human name>"
  short_description: "<One line>"
  default_prompt: "<When to use $<skill-name>, what it must verify first, and its stop condition>"
```

Every skill in the catalog needs this file so any harness that surfaces a skill picker has a
consistent, short description to show, independent of the full `SKILL.md` body.

## references/

- English file names and English prose, even when the skill's user-facing conversation happens in
  another language — references are read by the agent, not shown verbatim to the user.
- Vendor-neutral: do not hardcode a specific assistant brand name inside method text. Skills in this
  repository are meant to be portable across any harness that reads `SKILL.md`, `AGENTS.md`, Markdown,
  and local scripts.
- One topic per file. If a reference file is trying to cover two unrelated concerns, split it.

## assets/

Templates the skill instantiates into a real project artifact. Prefer `assets/` as the directory name
for new skills; a few earlier skills in this repository still use `templates/` for the same purpose —
leave those as they are unless a dedicated migration task covers renaming and relinking them, since
other documents may already point at the old path.

## scripts/validate_*.py

- Standard library only — no third-party dependency, so the script runs in any Python 3 environment
  without setup.
- Accepts the artifact root the skill actually reads/writes (typically `docs/ai/<project-slug>` for a
  pipeline skill, or a skill directory for this authoring skill itself).
- Prints a clear PASS/FAIL summary line and exits `0` on PASS, non-zero on FAIL — this is what lets a
  skill's own workflow check "did validation actually pass" instead of trusting a claim.
- Named after the stage or artifact it checks (`validate_investigation.py`, `validate_execution.py`,
  `validate_review.py`, `validate_release.py`, `validate_skill.py`), not generically `validate.py`,
  since multiple skills' scripts may be referenced together in documentation.
