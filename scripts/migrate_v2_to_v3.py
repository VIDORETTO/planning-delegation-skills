#!/usr/bin/env python3
"""Migrate a planning-delegation/v2 project workflow to skill-team/v3.

Targets a project workflow root (a directory containing PROGRESS.md, e.g.
`docs/ai/<project-slug>`), not this skills repository itself.

What it does, per frontmatter block found under the project root:
  - Renames legacy field names to their v3 equivalents when the v3 name is
    absent (active_skill -> stage_owner, current_task -> active_task,
    last_validation -> last_validation_result, brainstorm_revision ->
    discovery_revision).
  - Normalizes legacy stage/status vocabulary (BRAINSTORM -> DISCOVERY,
    PLAN -> PLANNING, BRAINSTORM_READY -> DISCOVERY_READY).
  - Splits the forbidden `next_skill` field into `required_skill` and
    `successor_skill` using a documented (stage, status) heuristic table,
    falling back to the literal next_skill value when it already names a
    real skill-team/v3 skill, and flagging anything it cannot infer safely
    for manual review instead of guessing.
  - Adds any missing `*_revision` field with a default of `0`, never
    decreasing an existing value.
  - Adds missing `writer_skill` / `writer_task` as `null`.
  - Sets `workflow_contract: skill-team/v3`.
  - Never deletes unknown fields or unknown files; only rewrites recognized
    v2 frontmatter blocks.

Safety:
  - `--dry-run` prints the full report and performs no writes.
  - Every file that would be modified is backed up (verbatim copy) under
    `<project_root>/.migration-backup/<UTC-timestamp>/` before any write.
  - All files are validated and staged in memory first; if PROGRESS.md
    itself cannot be safely migrated, nothing is written (all-or-nothing
    for the primary file; secondary files are best-effort and independently
    skippable).
  - Already-migrated files (workflow_contract already skill-team/v3) are
    left untouched and reported as no-ops, so re-running is safe.

Usage:
    python scripts/migrate_v2_to_v3.py <project-root> [--dry-run] [--json]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress_contract import REVISION_FIELDS, WORKFLOW_CONTRACT  # noqa: E402

LEGACY_CONTRACT = "planning-delegation/v2"

FIELD_ALIASES: dict[str, str] = {
    "active_skill": "stage_owner",
    "current_task": "active_task",
    "last_validation": "last_validation_result",
    "brainstorm_revision": "discovery_revision",
}

STAGE_ALIASES: dict[str, str] = {
    "BRAINSTORM": "DISCOVERY",
    "PLAN": "PLANNING",
}

STATUS_ALIASES: dict[str, str] = {
    "BRAINSTORM_READY": "DISCOVERY_READY",
}

# (normalized stage, normalized status) -> (required_skill, successor_skill)
STATUS_HEURISTICS: dict[tuple[str, str], tuple[str, str | None]] = {
    ("DISCOVERY", "BRAINSTORM_IN_PROGRESS"): ("brainstorm-idea-with-user", "create-spec-driven-plan"),
    ("DISCOVERY", "CODEBASE_INVESTIGATION_IN_PROGRESS"): ("investigate-existing-codebase", "create-spec-driven-plan"),
    ("DISCOVERY", "UX_AUDIT_IN_PROGRESS"): ("product-ux-audit", "create-spec-driven-plan"),
    ("DISCOVERY", "DISCOVERY_READY"): ("create-spec-driven-plan", "route-ai-work-by-capability"),
    ("PLANNING", "PLAN_IN_PROGRESS"): ("create-spec-driven-plan", "route-ai-work-by-capability"),
    ("PLANNING", "PLAN_VALIDATED"): ("route-ai-work-by-capability", "execute-routed-task"),
    ("PLANNING", "REPLAN_REQUIRED"): ("create-spec-driven-plan", "route-ai-work-by-capability"),
    ("ROUTING", "ROUTING_IN_PROGRESS"): ("route-ai-work-by-capability", "execute-routed-task"),
    ("ROUTING", "IMPLEMENTATION_READY"): ("execute-routed-task", "review-implementation-evidence"),
    ("ROUTING", "REROUTE_REQUIRED"): ("route-ai-work-by-capability", "execute-routed-task"),
    ("IMPLEMENTATION", "TASK_IN_PROGRESS"): ("execute-routed-task", "review-implementation-evidence"),
    ("IMPLEMENTATION", "TASK_BLOCKED"): ("execute-routed-task", "review-implementation-evidence"),
    ("IMPLEMENTATION", "TASK_COMPLETE"): ("execute-routed-task", "review-implementation-evidence"),
    ("IMPLEMENTATION", "IMPLEMENTATION_COMPLETE"): ("review-implementation-evidence", "validate-release-readiness"),
}

DEFAULT_SUCCESSOR: dict[str, str | None] = {
    "brainstorm-idea-with-user": "create-spec-driven-plan",
    "investigate-existing-codebase": "create-spec-driven-plan",
    "product-ux-audit": "create-spec-driven-plan",
    "create-spec-driven-plan": "route-ai-work-by-capability",
    "route-ai-work-by-capability": "execute-routed-task",
    "execute-routed-task": "review-implementation-evidence",
    "review-implementation-evidence": "validate-release-readiness",
    "validate-release-readiness": None,
}

# next_skill values that were informal v2 placeholders, not real skill names.
LEGACY_NEXT_SKILL_LITERALS: dict[str, str] = {
    "implementation": "execute-routed-task",
    "review": "review-implementation-evidence",
    "release": "validate-release-readiness",
}


def load_known_skills(repo_root: Path) -> set[str]:
    catalog_path = repo_root / "catalog" / "skills.json"
    known = set(DEFAULT_SUCCESSOR.keys())
    if catalog_path.is_file():
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            known.update(
                entry["name"] for entry in catalog.get("skills", [])
                if isinstance(entry, dict) and isinstance(entry.get("name"), str)
            )
        except json.JSONDecodeError:
            pass
    return known


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_root", type=Path, help="Project workflow root, or a direct path to PROGRESS.md")
    parser.add_argument("--dry-run", action="store_true", help="report planned changes without writing")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def locate_progress(project_root: Path) -> Path | None:
    if project_root.is_file() and project_root.name == "PROGRESS.md":
        return project_root
    candidate = project_root / "PROGRESS.md"
    return candidate if candidate.is_file() else None


class FrontmatterBlock:
    """A parsed, order-preserving flat YAML frontmatter block plus its body."""

    def __init__(self, path: Path, keys: list[str], values: dict[str, str], body: str):
        self.path = path
        self.keys = keys  # preserves original order, excluding dropped keys
        self.values = values
        self.body = body
        self.changes: list[str] = []

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def set(self, key: str, value: str, reason: str) -> None:
        if key not in self.values:
            self.keys.append(key)
        elif self.values[key] == value:
            return
        self.values[key] = value
        self.changes.append(reason)

    def rename(self, old: str, new: str) -> None:
        if old not in self.values or new in self.values:
            return
        self.values[new] = self.values.pop(old)
        self.keys[self.keys.index(old)] = new
        self.changes.append(f"renamed field '{old}' -> '{new}'")

    def drop(self, key: str) -> str | None:
        if key not in self.values:
            return None
        value = self.values.pop(key)
        self.keys.remove(key)
        self.changes.append(f"removed forbidden field '{key}' (was {value!r})")
        return value

    def render(self) -> str:
        lines = ["---"]
        for key in self.keys:
            lines.append(f"{key}: {self.values[key]}")
        lines.append("---")
        return "\n".join(lines) + "\n" + self.body


def parse_block(path: Path) -> FrontmatterBlock | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    keys: list[str] = []
    values: dict[str, str] = {}
    end_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip("\"'")
        if not key:
            continue
        if key not in values:
            keys.append(key)
        values[key] = value
    if end_index is None:
        return None
    body = "\n".join(lines[end_index + 1:])
    if text.endswith("\n") and not body.endswith("\n"):
        body += "\n"
    return FrontmatterBlock(path, keys, values, body)


def normalize_aliases(block: FrontmatterBlock) -> None:
    for old, new in FIELD_ALIASES.items():
        block.rename(old, new)

    stage = block.get("stage")
    if stage in STAGE_ALIASES:
        block.set("stage", STAGE_ALIASES[stage], f"normalized stage '{stage}' -> '{STAGE_ALIASES[stage]}'")

    status = block.get("status")
    if status in STATUS_ALIASES:
        block.set("status", STATUS_ALIASES[status], f"normalized status '{status}' -> '{STATUS_ALIASES[status]}'")


def infer_required_and_successor(
    block: FrontmatterBlock, known_skills: set[str], warnings: list[str]
) -> None:
    if "next_skill" not in block.values:
        return

    legacy_value = block.drop("next_skill")
    stage = block.get("stage") or ""
    status = block.get("status") or ""

    inferred = STATUS_HEURISTICS.get((stage, status))
    if inferred is None and legacy_value in known_skills:
        inferred = (legacy_value, DEFAULT_SUCCESSOR.get(legacy_value))
    if inferred is None and legacy_value in LEGACY_NEXT_SKILL_LITERALS:
        required = LEGACY_NEXT_SKILL_LITERALS[legacy_value]
        inferred = (required, DEFAULT_SUCCESSOR.get(required))

    if inferred is None:
        warnings.append(
            f"{block.path}: could not infer required_skill/successor_skill from "
            f"next_skill={legacy_value!r} stage={stage!r} status={status!r}; "
            "MANUAL REVIEW REQUIRED"
        )
        block.set("required_skill", legacy_value, "kept unmapped legacy next_skill value as required_skill (manual review required)")
        if "successor_skill" not in block.values:
            block.set("successor_skill", "null", "defaulted unresolved successor_skill to null")
        return

    required_skill, successor_skill = inferred
    if block.get("required_skill") != required_skill:
        block.set("required_skill", required_skill, f"required_skill inferred as '{required_skill}' from next_skill={legacy_value!r}")
    if successor_skill is not None and block.get("successor_skill") != successor_skill:
        block.set("successor_skill", successor_skill, f"successor_skill inferred as '{successor_skill}'")
    elif "successor_skill" not in block.values:
        block.set("successor_skill", "null", "defaulted successor_skill to null (end of pipeline)")


def apply_revision_defaults(block: FrontmatterBlock) -> None:
    for name in REVISION_FIELDS:
        if name not in block.values:
            block.set(name, "0", f"added missing '{name}' with default 0")


def apply_writer_defaults(block: FrontmatterBlock) -> None:
    for name in ("writer_skill", "writer_task"):
        if name not in block.values:
            block.set(name, "null", f"added missing '{name}' defaulted to null")


def migrate_block(path: Path, known_skills: set[str], warnings: list[str]) -> tuple[FrontmatterBlock | None, str]:
    """Returns (block_or_None, status) where status is one of:
    'migrated', 'already-migrated', 'not-v2', 'malformed'.
    """

    block = parse_block(path)
    if block is None:
        return None, "malformed"

    contract = block.get("workflow_contract")
    if contract == WORKFLOW_CONTRACT:
        return None, "already-migrated"
    if contract != LEGACY_CONTRACT:
        return None, "not-v2"

    block.set("workflow_contract", WORKFLOW_CONTRACT, f"workflow_contract '{LEGACY_CONTRACT}' -> '{WORKFLOW_CONTRACT}'")
    normalize_aliases(block)
    infer_required_and_successor(block, known_skills, warnings)
    apply_revision_defaults(block)
    apply_writer_defaults(block)
    return block, "migrated"


def backup_files(files: list[Path], project_root: Path, dry_run: bool) -> Path | None:
    if not files:
        return None
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = project_root / ".migration-backup" / timestamp
    if not dry_run:
        for path in files:
            rel = path.relative_to(project_root)
            destination = backup_root / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    return backup_root


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    known_skills = load_known_skills(repo_root)

    progress_path = locate_progress(args.project_root.resolve())
    if progress_path is None:
        print(f"error: PROGRESS.md not found under {args.project_root}", file=sys.stderr)
        return 2

    project_root = progress_path.parent
    candidate_files = sorted(project_root.rglob("*.md"))
    candidate_files = [p for p in candidate_files if ".migration-backup" not in p.parts]

    warnings: list[str] = []
    staged: dict[Path, FrontmatterBlock] = {}
    report_entries: list[dict] = []

    progress_block, progress_status = migrate_block(progress_path, known_skills, warnings)
    if progress_status == "malformed":
        print(f"error: {progress_path} has no valid, terminated YAML frontmatter; aborting without changes", file=sys.stderr)
        return 2
    if progress_status == "not-v2":
        print(
            f"error: {progress_path} does not declare workflow_contract: {LEGACY_CONTRACT!r} "
            f"(found {parse_block(progress_path).get('workflow_contract')!r}); nothing to migrate",
            file=sys.stderr,
        )
        return 2
    if progress_status == "already-migrated":
        report_entries.append({"file": str(progress_path.relative_to(project_root)), "status": "already-migrated"})
    else:
        staged[progress_path] = progress_block
        report_entries.append({
            "file": str(progress_path.relative_to(project_root)),
            "status": "migrated",
            "changes": progress_block.changes,
        })

    for path in candidate_files:
        if path == progress_path:
            continue
        block, status = migrate_block(path, known_skills, warnings)
        if status == "migrated":
            staged[path] = block
            report_entries.append({"file": str(path.relative_to(project_root)), "status": "migrated", "changes": block.changes})
        elif status == "already-migrated":
            report_entries.append({"file": str(path.relative_to(project_root)), "status": "already-migrated"})
        elif status == "malformed":
            warnings.append(f"{path}: skipped (frontmatter present but malformed/unterminated)")
        # 'not-v2' files (no workflow_contract or unrelated docs) are silently left alone.

    backup_root = None
    if staged:
        backup_root = backup_files(list(staged.keys()), project_root, args.dry_run)
        if not args.dry_run:
            for path, block in staged.items():
                path.write_text(block.render(), encoding="utf-8")

    result = {
        "project_root": str(project_root),
        "dry_run": args.dry_run,
        "backup_dir": str(backup_root) if backup_root else None,
        "files": report_entries,
        "warnings": warnings,
        "migrated_count": sum(1 for e in report_entries if e["status"] == "migrated"),
    }

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"project_root={result['project_root']}")
        print(f"dry_run={result['dry_run']}")
        print(f"backup_dir={result['backup_dir']}")
        for entry in report_entries:
            print(f"\n{entry['file']}: {entry['status']}")
            for change in entry.get("changes", []):
                print(f"  - {change}")
        if warnings:
            print("\nwarnings:")
            for warning in warnings:
                print(f"  - {warning}")
        print(f"\nmigrated {result['migrated_count']} file(s)")
        print("MIGRATION DRY-RUN COMPLETE" if args.dry_run else "MIGRATION COMPLETE")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
