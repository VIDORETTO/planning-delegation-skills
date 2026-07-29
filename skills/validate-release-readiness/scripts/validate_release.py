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

REPOSITORY_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(REPOSITORY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_SCRIPTS))
from workflow_contract import validate_handoff as validate_shared_handoff, validate_progress as validate_shared_progress

CONTRACT = "skill-team/v3"
SKILL = "validate-release-readiness"
ALLOWED_STATUSES = {
    "RELEASE_REVIEW_REQUIRED", "RELEASE_REVIEW_IN_PROGRESS", "RELEASE_BLOCKED", "RELEASE_READY", "RELEASED",
    "POST_RELEASE_REVIEW_REQUIRED", "POST_RELEASE_REVIEW_IN_PROGRESS",
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


def table_records(path: Path, required: set[str]) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        header = [cell.strip() for cell in line.strip().strip("|").split("|")] if line.strip().startswith("|") else []
        if not required.issubset(header):
            continue
        records = []
        for row_line in lines[index + 2:]:
            if not row_line.strip().startswith("|"):
                break
            row = [cell.strip() for cell in row_line.strip().strip("|").split("|")]
            if len(row) == len(header):
                records.append(dict(zip(header, row)))
        return records
    return []


def evidence_resolves(evidence: str, base: Path, decision: Path) -> bool:
    """Evidence is either a recorded command result or a path that exists locally."""
    if evidence.startswith("command:"):
        return "PASS" in evidence.upper() or "FAIL" in evidence.upper()
    target = evidence.strip().strip("`").split("#", 1)[0]
    return bool(target) and ((base / target).resolve().exists() or (decision.parent / target).resolve().exists())


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


def validate_accepted_risks(text: str, gates: list[dict[str, str]]) -> list[str]:
    """Accepted risks need accountable, time-bounded dispositions."""
    accepted = {gate["gate"].lower() for gate in gates if gate["result"] == "ACCEPTED_RISK"}
    if not accepted:
        return []
    errors: list[str] = []
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 6 and cells[0] not in {"ID", "---"} and cells[0].startswith("RISK-"):
            rows.append(cells)
    covered = set()
    for risk_id, gate, rationale, owner, review, non_waivable in rows:
        covered.add(gate.lower())
        if not all((rationale, owner, review)):
            errors.append(f"accepted risk {risk_id} lacks rationale, owner, or expiration/review condition")
        if gate.lower() in NON_WAIVABLE_GATES and non_waivable.upper() != "YES":
            errors.append(f"accepted risk {risk_id} lacks non-waivable gate confirmation")
    for gate in accepted - covered:
        errors.append(f"ACCEPTED_RISK gate lacks accepted-risk register entry: {gate}")
    return errors


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
        "review_input": base / "handoffs" / "REVIEW-TO-RELEASE.md",
        "waived_input": base / "handoffs" / "IMPLEMENTATION-TO-RELEASE.md",
    }
    if not paths["progress"].is_file():
        report.error(f"missing required document: {paths['progress']}")

    progress, _ = frontmatter(paths["progress"], report) if paths["progress"].is_file() else ({}, "")
    status = progress.get("status")

    needs_decision = status in {"RELEASE_REVIEW_IN_PROGRESS", "RELEASE_READY", "RELEASE_BLOCKED"}
    if needs_decision and not paths["decision"].is_file():
        report.error(f"missing required document: {paths['decision']}")
    decision, decision_body = frontmatter(paths["decision"], report) if paths["decision"].is_file() else ({}, "")
    inputs = [path for path in (paths["review_input"], paths["waived_input"]) if path.is_file()]
    if status in {"RELEASE_REVIEW_REQUIRED", "RELEASE_REVIEW_IN_PROGRESS"}:
        if len(inputs) != 1:
            report.error("release evaluation requires exactly one review-to-release or implementation-to-release handoff")
        else:
            handoff, _ = frontmatter(inputs[0], report)
            _, handoff_body = frontmatter(inputs[0], report)
            report.errors.extend(validate_shared_handoff({key: "null" if value is None else str(value) for key, value in handoff.items()}, handoff_body))
            expected_type = "review-to-release" if inputs[0] == paths["review_input"] else "implementation-to-release"
            if handoff.get("workflow_contract") != CONTRACT or handoff.get("handoff_type") != expected_type:
                report.error("release input handoff has an invalid contract or type")
            if handoff.get("consumer_skill") != SKILL or handoff.get("handoff_status") != "READY" or handoff.get("validation_result") != "PASS":
                report.error("release input handoff must target release validation and be READY with PASS")
            if inputs[0] == paths["review_input"]:
                if handoff.get("output_revision") != progress.get("review_revision"):
                    report.error("REVIEW-TO-RELEASE.md is stale for review_revision")
                if handoff.get("input_revision") != progress.get("implementation_revision"):
                    report.error("REVIEW-TO-RELEASE.md is stale for implementation_revision")
            elif handoff.get("output_revision") != progress.get("implementation_revision") or handoff.get("input_revision") != progress.get("routing_revision"):
                report.error("IMPLEMENTATION-TO-RELEASE.md has stale routing or implementation revision")
            routing = base / "routing" / "ROUTING.md"
            if not routing.is_file():
                report.error("missing strict routing policy for release input")
            else:
                routes = table_records(routing, {"Task", "Review mode"})
                if not routes:
                    report.error("ROUTING.md lacks canonical review policy")
                elif any(row["Review mode"] != "NONE" for row in routes) != (inputs[0] == paths["review_input"]):
                    report.error("release input does not match routing review-required or review-waived policy")

    if progress:
        report.errors.extend(validate_shared_progress({key: "null" if value is None else str(value) for key, value in progress.items()}))
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
        if progress.get("stage_owner") != SKILL:
            report.error("PROGRESS.md stage_owner must be validate-release-readiness")
        if status not in ALLOWED_STATUSES:
            report.error(f"invalid release status: {status}")
        if status == "RELEASE_READY" and progress.get("required_skill") != "NONE":
            report.error("required_skill must be 'NONE' when RELEASE_READY (a human deploys)")
        if status in {"RELEASE_REVIEW_REQUIRED", "RELEASE_REVIEW_IN_PROGRESS", "RELEASE_BLOCKED"} and progress.get("required_skill") != SKILL:
            report.error(f"required_skill must be '{SKILL}' during release evaluation")
        if status == "RELEASE_BLOCKED" and progress.get("required_skill") in (None, "", "NONE"):
            report.error("RELEASE_BLOCKED must name a required_skill to resolve the blocker")
        if status == "RELEASE_REVIEW_IN_PROGRESS":
            if progress.get("writer_skill") != SKILL or progress.get("writer_task") is not None:
                report.error("RELEASE_REVIEW_IN_PROGRESS requires only the release validator writer lock")
        elif progress.get("writer_skill") is not None or progress.get("writer_task") is not None:
            report.error("only RELEASE_REVIEW_IN_PROGRESS may hold a release writer lock")

    if decision:
        require_keys(decision, (
            "workflow_contract", "project_id", "project_slug", "release_revision",
            "workflow_profile", "decision", "updated_at",
        ), paths["decision"], report)
        if decision.get("workflow_contract") != CONTRACT:
            report.error(f"RELEASE-READINESS.md uses the wrong workflow contract: {paths['decision']}")
        if decision.get("release_revision") != progress.get("release_revision"):
            report.error("RELEASE-READINESS.md is stale for release_revision")
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
        unresolved = [g["gate"] for g in gates if g["result"] in {"PASS", "ACCEPTED_RISK"} and g["evidence"] and not evidence_resolves(g["evidence"], base, paths["decision"])]
        if unresolved:
            report.error(f"gate evidence does not resolve to a local artifact or recorded command: {unresolved}")
        for error in validate_accepted_risks(decision_body, gates):
            report.error(error)
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
