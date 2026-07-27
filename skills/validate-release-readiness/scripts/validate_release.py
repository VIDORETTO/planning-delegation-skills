#!/usr/bin/env python3
"""Validate skill-team/v3 release-stage artifacts (stdlib only).

Usage:
    python validate_release.py docs/ai/<project-slug>

Exit code 0 on PASS, non-zero on FAIL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

CONTRACT = "skill-team/v3"
SKILL = "validate-release-readiness"
ALLOWED_STATUSES = {
    "RELEASE_REVIEW_REQUIRED", "RELEASE_BLOCKED", "RELEASE_READY", "RELEASED",
    "POST_RELEASE_REVIEW_REQUIRED",
}
GATE_ROW_RE = re.compile(r"^\|\s*(?P<gate>[^|]+?)\s*\|\s*(?P<result>PASS|FAIL|ACCEPTED_RISK|N/A)\s*\|\s*(?P<evidence>[^|]*?)\s*\|\s*$")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FORBIDDEN_FIELD_RE = re.compile(r"(?m)^next_skill\s*:")

REQUIRED_DECISION_HEADINGS = (
    "Identification", "Gate evaluation", "Accepted risk register", "Blockers", "Decision",
    "Next required skill",
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


def parse_gates(text: str) -> list[dict[str, str]]:
    gates: list[dict[str, str]] = []
    for line in text.splitlines():
        match = GATE_ROW_RE.match(line.strip())
        if not match:
            continue
        gate = match.group("gate").strip()
        if gate.lower() in {"gate", "---"} or set(gate) <= {"-"}:
            continue
        gates.append({"gate": gate, "result": match.group("result"), "evidence": match.group("evidence").strip()})
    return gates


NON_WAIVABLE_GATES = {"security and privacy", "migration and rollback"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path, help="docs/ai/<project-slug>")
    args = parser.parse_args(argv)
    report = Report()
    base = args.project_dir.resolve()

    paths = {
        "progress": base / "PROGRESS.md",
        "decision": base / "release" / "RELEASE-READINESS.md",
        "post_release": base / "release" / "POST-RELEASE.md",
    }
    if not paths["progress"].is_file():
        report.error(f"missing required document: {paths['progress']}")

    progress, _ = frontmatter(paths["progress"], report) if paths["progress"].is_file() else ({}, "")
    status = progress.get("status")

    needs_decision = status in {"RELEASE_READY", "RELEASE_BLOCKED"}
    if needs_decision and not paths["decision"].is_file():
        report.error(f"missing required document: {paths['decision']}")
    decision, decision_body = frontmatter(paths["decision"], report) if paths["decision"].is_file() else ({}, "")

    if progress:
        require_keys(progress, (
            "workflow_contract", "project_id", "project_slug", "stage", "status",
            "required_skill", "successor_skill", "handoff_status", "release_revision",
            "workflow_profile", "next_action", "blockers", "last_validation_command",
            "last_validation_result", "updated_at",
        ), paths["progress"], report)
        if progress.get("workflow_contract") != CONTRACT:
            report.error(f"PROGRESS.md workflow_contract must be '{CONTRACT}'")
        if progress.get("stage") != "RELEASE":
            report.error(f"PROGRESS.md stage must be 'RELEASE', got '{progress.get('stage')}'")
        if status not in ALLOWED_STATUSES:
            report.error(f"invalid release status: {status}")
        if status == "RELEASE_READY" and progress.get("required_skill") != "NONE":
            report.error("required_skill must be 'NONE' when RELEASE_READY (a human deploys)")
        if status == "RELEASE_BLOCKED" and progress.get("required_skill") in (None, "", "NONE"):
            report.error("RELEASE_BLOCKED must name a required_skill to resolve the blocker")

    if decision:
        require_keys(decision, (
            "workflow_contract", "project_id", "project_slug", "release_revision",
            "workflow_profile", "decision", "updated_at",
        ), paths["decision"], report)
        if decision.get("workflow_contract") != CONTRACT:
            report.error(f"RELEASE-READINESS.md uses the wrong workflow contract: {paths['decision']}")
        validate_headings(decision_body, REQUIRED_DECISION_HEADINGS, paths["decision"], report)
        validate_links(decision_body, paths["decision"], report)
        gates = parse_gates(decision_body)
        if not gates:
            report.error("RELEASE-READINESS.md has no parseable gate rows")
        failing = [g for g in gates if g["result"] == "FAIL"]
        unevidenced = [g for g in gates if g["result"] in {"PASS", "ACCEPTED_RISK"} and not g["evidence"]]
        non_waivable_failed = [g for g in gates if g["gate"].lower() in NON_WAIVABLE_GATES and g["result"] == "FAIL"]
        if unevidenced:
            report.error(f"gate marked PASS/ACCEPTED_RISK without evidence citation: {[g['gate'] for g in unevidenced]}")
        if decision.get("decision") == "RELEASE_READY":
            if failing:
                report.error(f"decision is RELEASE_READY but gates still FAIL: {[g['gate'] for g in failing]}")
            if non_waivable_failed:
                report.error("security/privacy or migration/rollback gate cannot be marked FAIL under RELEASE_READY")
        elif decision.get("decision") == "RELEASE_BLOCKED":
            if not failing:
                report.error("decision is RELEASE_BLOCKED but no gate is marked FAIL")
        if PLACEHOLDER_RE.search(decision_body) and decision.get("decision") == "RELEASE_READY":
            report.error(f"placeholder remains in a RELEASE_READY decision: {paths['decision']}")

    if paths["post_release"].is_file():
        post, post_body = frontmatter(paths["post_release"], report)
        require_keys(post, (
            "workflow_contract", "project_id", "project_slug", "release_revision", "status",
            "updated_at",
        ), paths["post_release"], report)
        if post.get("workflow_contract") != CONTRACT:
            report.error(f"POST-RELEASE.md uses the wrong workflow contract: {paths['post_release']}")

    for path in paths.values():
        if path.is_file():
            validate_no_next_skill(path.read_text(encoding="utf-8"), path, report)

    print(f"workflow_contract={CONTRACT}")
    print(f"skill={SKILL}")
    print(f"status={status or 'UNKNOWN'}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.errors:
        print(f"RELEASE INVALID ({len(report.errors)} errors)")
        return 1
    print("RELEASE VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
