#!/usr/bin/env python3
"""Create a strict, empty skill-team/v3 discovery workflow atomically."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress_contract import parse_frontmatter  # noqa: E402
from workflow_contract import validate_progress  # noqa: E402

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
DISCOVERIES = {
    "brainstorm": {
        "artifact": "discovery/brainstorm/BRAINSTORM.md",
        "files": ("discovery/brainstorm/BRAINSTORM.md",),
        "skill": "brainstorm-idea-with-user",
        "status": "BRAINSTORM_IN_PROGRESS",
    },
    "codebase": {
        "artifact": "discovery/codebase/INVESTIGATION.md",
        "files": ("discovery/codebase/INVESTIGATION.md", "discovery/codebase/EVIDENCE.md"),
        "skill": "investigate-existing-codebase",
        "status": "CODEBASE_INVESTIGATION_IN_PROGRESS",
    },
    "ux": {
        "artifact": "discovery/ux/UX-AUDIT.md",
        "files": ("discovery/ux/SITEMAP.md", "discovery/ux/COVERAGE.md", "discovery/ux/UX-AUDIT.md"),
        "skill": "product-ux-audit",
        "status": "UX_AUDIT_IN_PROGRESS",
    },
}
COMMON_FILES = ("PROGRESS.md", "SOURCE-REGISTER.md", "CONTEXT-INDEX.md", "GLOSSARY.md")


class InitError(Exception):
    def __init__(self, code: str, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise InitError("STV3-E030-INTERNAL", f"invalid CLI usage: {message}", 2)


def utc_timestamp(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InitError("STV3-E005-ENUM", "timestamp must be ISO-8601 UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise InitError("STV3-E005-ENUM", "timestamp must be ISO-8601 UTC")
    return parsed.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_arguments(args: argparse.Namespace) -> tuple[Path, str]:
    root = Path(args.root)
    if not root.exists() or not root.is_dir() or root.is_symlink():
        raise InitError("STV3-E025-SCOPE", "root must be an existing non-symlink directory")
    root = root.resolve()
    if not PROJECT_ID_RE.fullmatch(args.project_id):
        raise InitError("STV3-E005-ENUM", "project_id must be a stable identifier")
    if not SLUG_RE.fullmatch(args.project_slug):
        raise InitError("STV3-E025-SCOPE", "project_slug must be a kebab-case path-safe slug")
    if args.profile not in {"compact", "standard", "critical"}:
        raise InitError("STV3-E005-ENUM", "profile is not canonical")
    if args.discovery not in DISCOVERIES:
        raise InitError("STV3-E005-ENUM", "discovery is not canonical")
    return root, utc_timestamp(args.timestamp)


def checked_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts)
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise InitError("STV3-E025-SCOPE", f"symlink is not allowed: {current}")
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError as error:
        raise InitError("STV3-E025-SCOPE", "target escapes root") from error
    return candidate


def progress_text(project_id: str, slug: str, profile: str, discovery: str, timestamp: str) -> str:
    mode = DISCOVERIES[discovery]
    artifact = f"docs/ai/{slug}/{mode['artifact']}"
    fields = (
        ("workflow_contract", "skill-team/v3"), ("project_id", project_id), ("project_slug", slug),
        ("workflow_profile", profile), ("stage", "DISCOVERY"), ("status", mode["status"]),
        ("stage_owner", mode["skill"]), ("required_skill", mode["skill"]),
        ("successor_skill", "create-spec-driven-plan"), ("handoff_status", "NOT_READY"),
        ("discovery_revision", "1"), ("plan_revision", "0"), ("routing_revision", "0"),
        ("implementation_revision", "0"), ("review_revision", "0"), ("release_revision", "0"),
        ("active_artifact", artifact), ("active_task", "null"), ("active_batch", "null"),
        ("active_executor_model", "null"), ("active_reviewer_model", "null"), ("writer_skill", mode["skill"]),
        ("writer_task", "null"), ("next_action", "Complete the selected discovery artifact"),
        ("blockers", "NONE"), ("last_validation_command", "NONE"), ("last_validation_result", "NOT_RUN"),
        ("updated_at", timestamp),
    )
    return "---\n" + "\n".join(f"{key}: {value}" for key, value in fields) + "\n---\n\n# Workflow Progress\n\nDiscovery is in progress.\n"


def file_text(relative: str) -> str:
    titles = {
        "SOURCE-REGISTER.md": "# Source Register\n\n| ID | Source | Type | Authority | Notes |\n|---|---|---|---|---|\n",
        "CONTEXT-INDEX.md": "# Context Index\n\nRead `PROGRESS.md` first.\n",
        "GLOSSARY.md": "# Glossary\n\n| Term | Project meaning | Source | Revision |\n|---|---|---|---|\n",
        "discovery/brainstorm/BRAINSTORM.md": "# Brainstorm\n\n## Original idea\n\nRecord the user's request here.\n",
        "discovery/codebase/INVESTIGATION.md": "---\nworkflow_contract: skill-team/v3\ndiscovery_revision: 1\n---\n\n# Investigation\n\n## Facts\n\n- None recorded.\n",
        "discovery/codebase/EVIDENCE.md": "# Evidence\n\n| ID | Kind | Location | Notes |\n|---|---|---|---|\n",
        "discovery/ux/SITEMAP.md": "# Sitemap\n\n| ID | Page | Status |\n|---|---|---|\n",
        "discovery/ux/COVERAGE.md": "# Coverage Matrix\n\n| Screen ID | Evidence | Status |\n|---|---|---|\n",
        "discovery/ux/UX-AUDIT.md": "# UX Audit\n\n## Findings\n\n- None recorded.\n",
    }
    return titles[relative]


def validate_staged(workflow: Path) -> None:
    parsed = parse_frontmatter((workflow / "PROGRESS.md").read_text(encoding="utf-8"))
    errors = validate_progress(parsed.data)
    if not parsed.found or not parsed.terminated or errors:
        detail = "; ".join(errors) if errors else "invalid PROGRESS.md frontmatter"
        raise InitError("STV3-E030-INTERNAL", detail, 2)


def initialize(args: argparse.Namespace) -> dict[str, object]:
    root, timestamp = validate_arguments(args)
    ai_root = checked_child(root, "docs", "ai")
    target = checked_child(root, "docs", "ai", args.project_slug)
    if target.exists() or target.is_symlink():
        raise InitError("STV3-E025-SCOPE", f"workflow target already exists: {target}")
    mode = DISCOVERIES[args.discovery]
    created = sorted((*COMMON_FILES, *mode["files"]))
    result = {
        "created": [f"docs/ai/{args.project_slug}/{path}" for path in created],
        "discovery": args.discovery,
        "dry_run": args.dry_run,
        "profile": args.profile,
        "progress": f"docs/ai/{args.project_slug}/PROGRESS.md",
        "project_id": args.project_id,
        "project_slug": args.project_slug,
        "workflow_root": f"docs/ai/{args.project_slug}",
    }
    if args.dry_run:
        staging = Path(tempfile.mkdtemp(prefix=".skill-team-init-", dir=root))
        try:
            workflow = staging / args.project_slug
            workflow.mkdir()
            (workflow / "PROGRESS.md").write_text(progress_text(args.project_id, args.project_slug, args.profile, args.discovery, timestamp), encoding="utf-8")
            for relative in created:
                if relative != "PROGRESS.md":
                    path = workflow / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(file_text(relative), encoding="utf-8")
            validate_staged(workflow)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
        return result
    try:
        if not ai_root.exists():
            ai_root.mkdir(parents=True)
        if ai_root.is_symlink() or not ai_root.is_dir():
            raise InitError("STV3-E025-SCOPE", f"workflow parent is unsafe: {ai_root}")
        staging = Path(tempfile.mkdtemp(prefix=".skill-team-init-", dir=ai_root))
        workflow = staging / args.project_slug
        workflow.mkdir()
        (workflow / "PROGRESS.md").write_text(progress_text(args.project_id, args.project_slug, args.profile, args.discovery, timestamp), encoding="utf-8")
        for relative in created:
            if relative != "PROGRESS.md":
                path = workflow / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(file_text(relative), encoding="utf-8")
        validate_staged(workflow)
        if target.exists() or target.is_symlink():
            raise InitError("STV3-E025-SCOPE", f"workflow target already exists: {target}")
        os.replace(workflow, target)
        staging.rmdir()
    except InitError:
        if "staging" in locals():
            shutil.rmtree(staging, ignore_errors=True)
        raise
    except OSError as error:
        if "staging" in locals():
            shutil.rmtree(staging, ignore_errors=True)
        raise InitError("STV3-E030-INTERNAL", f"I/O failure: {error}", 2) from error
    return result


def main(argv: list[str] | None = None) -> int:
    parser = Parser(add_help=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--discovery", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timestamp")
    try:
        result = initialize(parser.parse_args(argv))
    except InitError as error:
        print(f"{error.code} {error}", file=sys.stderr)
        return error.exit_code
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
