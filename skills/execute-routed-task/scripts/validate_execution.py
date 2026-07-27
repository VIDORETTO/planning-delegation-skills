#!/usr/bin/env python3
"""Validate skill-team/v3 implementation-stage artifacts (stdlib only).

Usage:
    python validate_execution.py docs/ai/<project-slug>

Exit code 0 on PASS, non-zero on FAIL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

CONTRACT = "skill-team/v3"
SKILL = "execute-routed-task"
COMPLETE_STATUS = "IMPLEMENTATION_COMPLETE"
ALLOWED_STATUSES = {COMPLETE_STATUS, "TASK_IN_PROGRESS", "TASK_BLOCKED", "TASK_COMPLETE"}
ALLOWED_SUCCESSORS = {"review-implementation-evidence", "validate-release-readiness"}
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?)?$")
FORBIDDEN_FIELD_RE = re.compile(r"(?m)^next_skill\s*:")

REQUIRED_HANDOFF_HEADINGS = (
    "Identification", "Summary", "Artifact inventory", "Preserved decisions",
    "Allowed open questions", "Blockers", "Consumer write scope", "Forbidden files",
    "Commands and results", "Stop instruction",
)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)


def scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"null", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def frontmatter(path: Path, report: Report) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", text, re.DOTALL)
    if not match:
        report.error(f"missing or unterminated YAML frontmatter: {path}")
        return {}, text
    data: dict[str, Any] = {}
    for lineno, raw in enumerate(match.group(1).splitlines(), 2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if not item:
            report.error(f"unsupported frontmatter syntax {path}:{lineno}: {raw.strip()}")
            continue
        data[item.group(1)] = scalar(item.group(2))
    return data, text[match.end():]


def require_keys(data: dict[str, Any], keys: tuple[str, ...], path: Path, report: Report) -> None:
    for key in keys:
        if key not in data:
            report.error(f"missing frontmatter key '{key}': {path}")


def validate_headings(text: str, headings: tuple[str, ...], path: Path, report: Report) -> None:
    found = {m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)}
    for heading in headings:
        if heading not in found:
            report.error(f"missing section '## {heading}': {path}")


def validate_links(text: str, path: Path, report: Report) -> None:
    for raw in LINK_RE.findall(text):
        target = raw.strip().strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).resolve().exists():
            report.error(f"broken local link '{raw}': {path}")


def validate_no_next_skill(text: str, path: Path, report: Report) -> None:
    if FORBIDDEN_FIELD_RE.search(text):
        report.error(f"'next_skill' is forbidden in skill-team/v3 artifacts: {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path, help="docs/ai/<project-slug>")
    args = parser.parse_args(argv)
    report = Report()
    base = args.project_dir.resolve()

    paths = {
        "progress": base / "PROGRESS.md",
        "evidence": base / "execution" / "EVIDENCE.md",
        "history": base / "execution" / "HISTORY.md",
        "handoff": base / "handoffs" / "IMPLEMENTATION-TO-REVIEW.md",
    }
    for name in ("progress", "evidence", "history"):
        if not paths[name].is_file():
            report.error(f"missing required document: {paths[name]}")

    progress, _ = frontmatter(paths["progress"], report) if paths["progress"].is_file() else ({}, "")
    status = progress.get("status")
    complete = status == COMPLETE_STATUS

    if complete and not paths["handoff"].is_file():
        report.error(f"missing required READY handoff: {paths['handoff']}")
    handoff, handoff_body = frontmatter(paths["handoff"], report) if paths["handoff"].is_file() else ({}, "")

    if progress:
        require_keys(progress, (
            "workflow_contract", "project_id", "project_slug", "stage", "status",
            "required_skill", "successor_skill", "handoff_status", "implementation_revision",
            "active_task", "writer_skill", "writer_task", "next_action", "blockers",
            "last_validation_command", "last_validation_result", "updated_at",
        ), paths["progress"], report)
        if progress.get("workflow_contract") != CONTRACT:
            report.error(f"PROGRESS.md workflow_contract must be '{CONTRACT}'")
        if progress.get("stage") != "IMPLEMENTATION":
            report.error(f"PROGRESS.md stage must be 'IMPLEMENTATION', got '{progress.get('stage')}'")
        if status not in ALLOWED_STATUSES:
            report.error(f"invalid implementation status: {status}")
        if complete:
            if progress.get("writer_skill") is not None:
                report.error("writer_skill must be released (null) once IMPLEMENTATION_COMPLETE")
            if progress.get("writer_task") is not None:
                report.error("writer_task must be null once IMPLEMENTATION_COMPLETE")
            if progress.get("required_skill") not in ALLOWED_SUCCESSORS:
                report.error(f"required_skill must be one of {sorted(ALLOWED_SUCCESSORS)} once complete")
            if progress.get("successor_skill") not in ALLOWED_SUCCESSORS:
                report.error(f"successor_skill must be one of {sorted(ALLOWED_SUCCESSORS)} once complete")
            if progress.get("handoff_status") != "READY":
                report.error("handoff_status must be READY when IMPLEMENTATION_COMPLETE")
        else:
            if progress.get("required_skill") != SKILL:
                report.error(f"required_skill must be '{SKILL}' while implementation is in progress")
        if status == "TASK_BLOCKED":
            blockers_dir = base / "blockers"
            open_blockers = []
            if blockers_dir.is_dir():
                for blocker_path in sorted(blockers_dir.glob("*.md")):
                    data, _ = frontmatter(blocker_path, report)
                    if data.get("status") == "OPEN":
                        open_blockers.append(blocker_path)
            if not open_blockers:
                report.error("status TASK_BLOCKED requires an OPEN document under blockers/")
            if progress.get("blockers") in (None, "NONE", ""):
                report.error("PROGRESS.md blockers field must describe the blocker when TASK_BLOCKED")

    if handoff:
        require_keys(handoff, (
            "workflow_contract", "handoff_type", "project_id", "producer_skill", "consumer_skill",
            "input_revision", "output_revision", "handoff_status", "validation_command",
            "validation_result", "generated_at",
        ), paths["handoff"], report)
        if handoff.get("workflow_contract") != CONTRACT:
            report.error(f"handoff workflow_contract must be '{CONTRACT}'")
        if handoff.get("handoff_type") != "implementation-to-review":
            report.error("handoff_type must be 'implementation-to-review'")
        if handoff.get("producer_skill") != SKILL:
            report.error(f"handoff producer_skill must be '{SKILL}'")
        if handoff.get("consumer_skill") not in ALLOWED_SUCCESSORS:
            report.error(f"handoff consumer_skill must be one of {sorted(ALLOWED_SUCCESSORS)}")
        if complete and handoff.get("handoff_status") != "READY":
            report.error("handoff_status must be READY when IMPLEMENTATION_COMPLETE")
        if complete and handoff.get("output_revision") != progress.get("implementation_revision"):
            report.error("handoff output_revision does not match PROGRESS.md implementation_revision")
        if complete and handoff.get("validation_result") != "PASS":
            report.error("READY handoff must record validation_result: PASS")
        validate_headings(handoff_body, REQUIRED_HANDOFF_HEADINGS, paths["handoff"], report)
        validate_links(handoff_body, paths["handoff"], report)
        if PLACEHOLDER_RE.search(handoff_body):
            report.error(f"placeholder remains in {paths['handoff']}")

    for path in paths.values():
        if path.is_file():
            validate_no_next_skill(path.read_text(encoding="utf-8"), path, report)

    print(f"workflow_contract={CONTRACT}")
    print(f"skill={SKILL}")
    print(f"status={status or 'UNKNOWN'}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.errors:
        print(f"EXECUTION INVALID ({len(report.errors)} errors)")
        return 1
    print("EXECUTION VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
