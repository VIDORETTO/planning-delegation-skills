#!/usr/bin/env python3
"""Safely migrate a planning-delegation/v2 workflow pointer to skill-team/v3.

The migrator changes only known v2 PROGRESS.md aliases. It refuses ambiguous
state, active writers, unknown fields, and any result that fails strict v3
validation. Every run produces a source-hash manifest; non-dry runs retain the
originals and manifest under ``.migration-backup`` for hash-safe recovery.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress_contract import REQUIRED_FIELDS, REVISION_FIELDS, WORKFLOW_CONTRACT  # noqa: E402
from workflow_contract import STATES, validate_progress  # noqa: E402

LEGACY_CONTRACT = "planning-delegation/v2"
FIELD_ALIASES = {
    "active_skill": "stage_owner",
    "current_task": "active_task",
    "last_validation": "last_validation_result",
    "brainstorm_revision": "discovery_revision",
}
STAGE_ALIASES = {"BRAINSTORM": "DISCOVERY", "PLAN": "PLANNING"}
STATUS_ALIASES = {"BRAINSTORM_READY": "DISCOVERY_READY"}
LEGACY_NEXT_SKILL_LITERALS = {
    "implementation": "execute-routed-task",
    "review": "review-implementation-evidence",
    "release": "validate-release-readiness",
}

# Values are intentionally exact. A legacy value outside this table is not a
# safe migration input, even if it resembles a current skill name.
STATE_SUCCESSORS = {
    ("DISCOVERY", "BRAINSTORM_IN_PROGRESS"): "create-spec-driven-plan",
    ("DISCOVERY", "CODEBASE_INVESTIGATION_IN_PROGRESS"): "create-spec-driven-plan",
    ("DISCOVERY", "UX_AUDIT_IN_PROGRESS"): "create-spec-driven-plan",
    ("DISCOVERY", "DISCOVERY_READY"): "route-ai-work-by-capability",
    ("DISCOVERY", "DISCOVERY_BLOCKED"): "create-spec-driven-plan",
    ("PLANNING", "PLAN_IN_PROGRESS"): "route-ai-work-by-capability",
    ("PLANNING", "PLAN_VALIDATED"): "execute-routed-task",
    ("PLANNING", "REPLAN_REQUIRED"): "route-ai-work-by-capability",
    ("ROUTING", "ROUTING_IN_PROGRESS"): "execute-routed-task",
    ("ROUTING", "IMPLEMENTATION_READY"): "review-implementation-evidence",
    ("ROUTING", "REROUTE_REQUIRED"): "execute-routed-task",
    ("IMPLEMENTATION", "TASK_IN_PROGRESS"): "review-implementation-evidence",
    ("IMPLEMENTATION", "TASK_COMPLETE"): "review-implementation-evidence",
    ("IMPLEMENTATION", "TASK_BLOCKED"): "review-implementation-evidence",
    ("IMPLEMENTATION", "IMPLEMENTATION_COMPLETE"): "validate-release-readiness",
}


class MigrationRefusal(Exception):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_frontmatter(path: Path) -> tuple[list[str], dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise MigrationRefusal(f"{path}: missing YAML frontmatter")
    values: dict[str, str] = {}
    keys: list[str] = []
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            body = "\n".join(lines[index + 1:])
            if text.endswith("\n"):
                body += "\n"
            return keys, values, body
        if ":" not in line:
            raise MigrationRefusal(f"{path}: unsupported frontmatter line {line!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        if not key or key in values:
            raise MigrationRefusal(f"{path}: duplicate or invalid frontmatter field {key!r}")
        keys.append(key)
        values[key] = value.strip().strip("\"'")
    raise MigrationRefusal(f"{path}: unterminated YAML frontmatter")


def render_frontmatter(keys: list[str], values: dict[str, str], body: str) -> str:
    return "---\n" + "\n".join(f"{key}: {values[key]}" for key in keys) + "\n---\n" + body


def locate_progress(target: Path) -> Path | None:
    if target.is_file() and target.name == "PROGRESS.md":
        return target
    candidate = target / "PROGRESS.md"
    return candidate if candidate.is_file() else None


def active_writer(values: dict[str, str]) -> bool:
    return values.get("writer_skill") not in (None, "", "null", "NONE")


def normalize_state(values: dict[str, str]) -> tuple[str, str]:
    stage = STAGE_ALIASES.get(values.get("stage", ""), values.get("stage", ""))
    status = STATUS_ALIASES.get(values.get("status", ""), values.get("status", ""))
    if (stage, status) not in STATES or (stage, status) not in STATE_SUCCESSORS:
        raise MigrationRefusal(f"unknown legacy state ({stage!r}, {status!r})")
    return stage, status


def migrate_progress(path: Path) -> tuple[str, list[str], dict[str, object]]:
    keys, values, body = parse_frontmatter(path)
    if values.get("workflow_contract") == WORKFLOW_CONTRACT:
        return path.read_text(encoding="utf-8"), [], {"status": "already-migrated"}
    if values.get("workflow_contract") != LEGACY_CONTRACT:
        raise MigrationRefusal(f"{path}: workflow_contract is not {LEGACY_CONTRACT!r}")
    if path.parent.parent.name == "ai" and values.get("project_slug") != path.parent.name:
        raise MigrationRefusal(
            f"{path}: project_slug {values.get('project_slug')!r} collides with workflow directory {path.parent.name!r}"
        )
    if active_writer(values):
        raise MigrationRefusal(f"{path}: writer lock {values['writer_skill']!r} is active")
    source_revisions = {
        field: values[field]
        for field in (*REVISION_FIELDS, "brainstorm_revision")
        if field in values
    }

    def set_value(field: str, value: str) -> None:
        values[field] = value
        if field not in keys:
            keys.append(field)

    changes: list[str] = []
    for old, new in FIELD_ALIASES.items():
        if old in values:
            if new in values and values[new] != values[old]:
                raise MigrationRefusal(f"{path}: conflicting aliases {old!r} and {new!r}")
            values[new] = values.pop(old)
            keys[keys.index(old)] = new
            changes.append(f"mapped {old} -> {new}")
    stage, status = normalize_state(values)
    if values.get("stage") != stage:
        set_value("stage", stage)
        changes.append("mapped stage alias")
    if values.get("status") != status:
        set_value("status", status)
        changes.append("mapped status alias")

    owner, required, writer, handoff = STATES[(stage, status)]
    if owner:
        set_value("stage_owner", owner)
    elif values.get("stage_owner") not in {
        "brainstorm-idea-with-user",
        "investigate-existing-codebase",
        "product-ux-audit",
    }:
        raise MigrationRefusal(f"{path}: {stage}/{status} needs a known discovery stage_owner")
    set_value("required_skill", required or values["stage_owner"])
    set_value("successor_skill", STATE_SUCCESSORS[(stage, status)])
    set_value("handoff_status", handoff)
    set_value("writer_skill", writer or "null")
    set_value("writer_task", "null")
    changes.append(
        f"set required_skill={values['required_skill']} successor_skill={values['successor_skill']}"
    )
    legacy_next = values.pop("next_skill", None)
    if legacy_next is not None:
        keys.remove("next_skill")
        expected = values["required_skill"]
        if LEGACY_NEXT_SKILL_LITERALS.get(legacy_next, legacy_next) != expected:
            raise MigrationRefusal(f"{path}: next_skill {legacy_next!r} is not the exact mapping for {stage}/{status}")
        changes.append("mapped next_skill exactly once")

    for field in REVISION_FIELDS:
        if field not in values:
            set_value(field, "0")
            changes.append(f"added {field}")
    # These v3 fields have no v2 equivalent and do not encode a user decision.
    for field, value in {
        "workflow_profile": "standard",
        "active_batch": "null",
        "active_executor_model": "null",
        "active_reviewer_model": "null",
        "last_validation_command": "NONE",
    }.items():
        if field not in values:
            set_value(field, value)
            changes.append(f"added {field}")
    if values.get("last_validation_result") == "null":
        set_value("last_validation_result", "NOT_RUN")
        changes.append("mapped null last_validation_result to NOT_RUN")
    set_value("workflow_contract", WORKFLOW_CONTRACT)
    changes.append("set workflow_contract to skill-team/v3")

    unknown = set(values) - set(REQUIRED_FIELDS)
    if unknown:
        raise MigrationRefusal(f"{path}: unknown fields would violate strict v3: {', '.join(sorted(unknown))}")
    missing = set(REQUIRED_FIELDS) - set(values)
    if missing:
        raise MigrationRefusal(f"{path}: cannot infer required fields: {', '.join(sorted(missing))}")
    rendered = render_frontmatter(keys, values, body)
    _, strict_values, _ = parse_frontmatter_text(rendered)
    errors = validate_progress(strict_values)
    if errors:
        raise MigrationRefusal(f"{path}: strict v3 validation failed: {'; '.join(errors)}")
    revisions = {field: values[field] for field in REVISION_FIELDS}
    return rendered, changes, {
        "status": "migrated",
        "source_revisions": source_revisions,
        "migrated_revisions": revisions,
    }


def parse_frontmatter_text(text: str) -> tuple[list[str], dict[str, str], str]:
    # Keep strict validation on the same parser without writing a staging file.
    lines = text.splitlines()
    keys, values = [], {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, _, value = line.partition(":")
        keys.append(key)
        values[key] = value.strip().strip("\"'")
    return keys, values, ""


def build_manifest(project_root: Path, progress_path: Path, original: bytes, migrated: bytes, changes: list[str], metadata: dict[str, object]) -> dict[str, object]:
    return {
        "format": "skill-team/v3-migration-manifest/1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "files": [{
            "path": str(progress_path.relative_to(project_root)).replace("\\", "/"),
            "source_sha256": sha256_bytes(original),
            "migrated_sha256": sha256_bytes(migrated),
            "source_revisions": metadata.get("source_revisions", {}),
            "migrated_revisions": metadata.get("migrated_revisions", {}),
            "changes": changes,
        }],
    }


def restore_hash_safe(backup_dir: Path) -> tuple[int, list[str]]:
    manifest = json.loads((backup_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    root = Path(manifest["project_root"])
    messages: list[str] = []
    for entry in manifest["files"]:
        target = root / entry["path"]
        original = backup_dir / "originals" / entry["path"]
        current_hash = sha256_bytes(target.read_bytes()) if target.exists() else None
        if current_hash != entry["migrated_sha256"]:
            messages.append(f"preserved {entry['path']}: current hash differs from migrated output")
            continue
        shutil.copy2(original, target)
        messages.append(f"restored {entry['path']}")
    return 0, messages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path, nargs="?", help="workflow root or PROGRESS.md")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--rollback", type=Path, help="hash-safe restore from a backup directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rollback:
        try:
            _, messages = restore_hash_safe(args.rollback.resolve())
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            print(f"MIGRATION ROLLBACK REFUSED: {error}", file=sys.stderr)
            return 2
        print("\n".join(messages))
        return 0
    if args.project_root is None:
        print("MIGRATION REFUSED: project_root is required", file=sys.stderr)
        return 2
    progress_path = locate_progress(args.project_root.resolve())
    if progress_path is None:
        print("MIGRATION REFUSED: PROGRESS.md not found", file=sys.stderr)
        return 2
    project_root = progress_path.parent
    try:
        original = progress_path.read_bytes()
        migrated_text, changes, metadata = migrate_progress(progress_path)
        migrated = migrated_text.encode("utf-8")
        manifest = build_manifest(project_root, progress_path, original, migrated, changes, metadata)
    except (OSError, MigrationRefusal) as error:
        print(f"MIGRATION REFUSED: {error}", file=sys.stderr)
        return 1
    if metadata["status"] == "already-migrated":
        manifest["files"] = []
    if args.dry_run:
        result = {"dry_run": True, "manifest": manifest, "migrated_count": len(manifest["files"])}
        print(json.dumps(result, indent=2) if args.as_json else json.dumps(result, indent=2))
        return 0
    if not manifest["files"]:
        print("MIGRATION NO-OP: strict v3 pointer already present")
        return 0
    backup_dir = project_root / ".migration-backup" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    try:
        original_path = backup_dir / "originals" / "PROGRESS.md"
        original_path.parent.mkdir(parents=True, exist_ok=False)
        original_path.write_bytes(original)
        (backup_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        temporary = progress_path.with_name(f".{progress_path.name}.migration-tmp")
        temporary.write_bytes(migrated)
        temporary.replace(progress_path)
    except OSError as error:
        print(f"MIGRATION INTERRUPTED: {error}; recover with --rollback {backup_dir}", file=sys.stderr)
        return 2
    result = {"dry_run": False, "backup_dir": str(backup_dir), "manifest": manifest, "migrated_count": 1}
    print(json.dumps(result, indent=2) if args.as_json else f"MIGRATION COMPLETE\nbackup_dir={backup_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
