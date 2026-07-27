#!/usr/bin/env python3
"""Validate skill-team/v3 review-stage artifacts (stdlib only).

Usage:
    python validate_review.py docs/ai/<project-slug>

Exit code 0 on PASS, non-zero on FAIL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

CONTRACT = "skill-team/v3"
SKILL = "review-implementation-evidence"
ALLOWED_STATUSES = {"REVIEW_REQUIRED", "REVIEW_IN_PROGRESS", "CHANGES_REQUIRED", "REVIEW_APPROVED"}
CLASSIFICATIONS = {"BLOCKING", "HIGH", "MEDIUM", "LOW", "QUESTION", "OUT_OF_SCOPE"}
BLOCKING_CLASS = {"BLOCKING", "HIGH"}
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FORBIDDEN_FIELD_RE = re.compile(r"(?m)^next_skill\s*:")
FINDING_ID_RE = re.compile(r"\bFND-\d{3}\b")

REQUIRED_REPORT_HEADINGS = (
    "Identification", "Verification performed", "Scope adherence",
    "Contracts, security, and regression risk", "Findings summary", "Outcome",
    "Next required skill",
)
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


def load_findings(findings_dir: Path, report: Report) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not findings_dir.is_dir():
        return records
    for path in sorted(findings_dir.glob("*.md")):
        data, _ = frontmatter(path, report)
        classification = data.get("classification")
        if classification and classification not in CLASSIFICATIONS:
            report.error(f"invalid finding classification '{classification}': {path}")
        records.append(data)
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path, help="docs/ai/<project-slug>")
    args = parser.parse_args(argv)
    report = Report()
    base = args.project_dir.resolve()

    paths = {
        "progress": base / "PROGRESS.md",
        "report": base / "review" / "REVIEW-REPORT.md",
        "input_handoff": base / "handoffs" / "IMPLEMENTATION-TO-REVIEW.md",
        "to_implementation": base / "handoffs" / "REVIEW-TO-IMPLEMENTATION.md",
        "to_release": base / "handoffs" / "REVIEW-TO-RELEASE.md",
    }
    for name in ("progress", "report"):
        if not paths[name].is_file():
            report.error(f"missing required document: {paths[name]}")

    progress, _ = frontmatter(paths["progress"], report) if paths["progress"].is_file() else ({}, "")
    review_report, report_body = frontmatter(paths["report"], report) if paths["report"].is_file() else ({}, "")
    status = progress.get("status")
    findings = load_findings(base / "findings", report)
    open_blocking = [f for f in findings if f.get("classification") in BLOCKING_CLASS and f.get("status") == "OPEN"]

    if progress:
        require_keys(progress, (
            "workflow_contract", "project_id", "project_slug", "stage", "status",
            "required_skill", "successor_skill", "handoff_status", "review_revision",
            "next_action", "blockers", "last_validation_command", "last_validation_result",
            "updated_at",
        ), paths["progress"], report)
        if progress.get("workflow_contract") != CONTRACT:
            report.error(f"PROGRESS.md workflow_contract must be '{CONTRACT}'")
        if progress.get("stage") != "REVIEW":
            report.error(f"PROGRESS.md stage must be 'REVIEW', got '{progress.get('stage')}'")
        if status not in ALLOWED_STATUSES:
            report.error(f"invalid review status: {status}")
        if status == "REVIEW_APPROVED":
            if open_blocking:
                report.error(f"REVIEW_APPROVED with open BLOCKING/HIGH findings: {[f.get('finding_id') for f in open_blocking]}")
            if progress.get("required_skill") != "validate-release-readiness":
                report.error("required_skill must be 'validate-release-readiness' once REVIEW_APPROVED")
            if not paths["to_release"].is_file():
                report.error(f"missing required handoff: {paths['to_release']}")
            if paths["to_implementation"].is_file():
                report.error("both REVIEW-TO-IMPLEMENTATION.md and REVIEW-TO-RELEASE.md exist; only one may be current")
        elif status == "CHANGES_REQUIRED":
            if not open_blocking:
                report.error("CHANGES_REQUIRED requires at least one open BLOCKING/HIGH finding")
            if progress.get("required_skill") != "execute-routed-task":
                report.error("required_skill must be 'execute-routed-task' when CHANGES_REQUIRED")
            if not paths["to_implementation"].is_file():
                report.error(f"missing required handoff: {paths['to_implementation']}")

    if review_report:
        require_keys(review_report, (
            "workflow_contract", "project_id", "project_slug", "review_revision",
            "implementation_revision_reviewed", "outcome", "updated_at",
        ), paths["report"], report)
        if review_report.get("workflow_contract") != CONTRACT:
            report.error(f"REVIEW-REPORT.md uses the wrong workflow contract: {paths['report']}")
        validate_headings(report_body, REQUIRED_REPORT_HEADINGS, paths["report"], report)
        validate_links(report_body, paths["report"], report)
        if PLACEHOLDER_RE.search(report_body):
            report.error(f"placeholder remains in {paths['report']}")
        cited = set(FINDING_ID_RE.findall(report_body))
        declared = {f.get("finding_id") for f in findings if f.get("finding_id")}
        missing = cited - declared
        if missing:
            report.error(f"REVIEW-REPORT.md cites findings absent from findings/: {sorted(missing)}")

    for name, handoff_path in (("to_implementation", paths["to_implementation"]), ("to_release", paths["to_release"])):
        if not handoff_path.is_file():
            continue
        handoff, handoff_body = frontmatter(handoff_path, report)
        require_keys(handoff, (
            "workflow_contract", "handoff_type", "project_id", "producer_skill", "consumer_skill",
            "input_revision", "output_revision", "handoff_status", "validation_command",
            "validation_result", "generated_at",
        ), handoff_path, report)
        if handoff.get("producer_skill") != SKILL:
            report.error(f"handoff producer_skill must be '{SKILL}': {handoff_path}")
        validate_headings(handoff_body, REQUIRED_HANDOFF_HEADINGS, handoff_path, report)
        validate_links(handoff_body, handoff_path, report)
        if PLACEHOLDER_RE.search(handoff_body) and handoff.get("handoff_status") == "READY":
            report.error(f"placeholder remains in READY handoff: {handoff_path}")

    for path in paths.values():
        if path.is_file():
            validate_no_next_skill(path.read_text(encoding="utf-8"), path, report)

    print(f"workflow_contract={CONTRACT}")
    print(f"skill={SKILL}")
    print(f"status={status or 'UNKNOWN'}")
    print(f"open_blocking_or_high={len(open_blocking)}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.errors:
        print(f"REVIEW INVALID ({len(report.errors)} errors)")
        return 1
    print("REVIEW VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
