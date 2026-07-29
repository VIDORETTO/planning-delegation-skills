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

REPOSITORY_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(REPOSITORY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_SCRIPTS))
from workflow_contract import validate_handoff as validate_shared_handoff, validate_progress as validate_shared_progress

CONTRACT = "skill-team/v3"
SKILL = "review-implementation-evidence"
CLASSIFICATIONS = {"BLOCKING", "HIGH", "MEDIUM", "LOW", "QUESTION", "OUT_OF_SCOPE"}
BLOCKING_CLASS = {"BLOCKING", "HIGH"}
GAP_TYPES = {"missing", "partial", "contradicts", "unrequested"}
RETURN_DESTINATIONS = {
    "execute-routed-task": ("REVIEW", "CHANGES_REQUIRED", "execute-routed-task"),
    "route-ai-work-by-capability": ("ROUTING", "REROUTE_REQUIRED", "route-ai-work-by-capability"),
    "create-spec-driven-plan": ("PLANNING", "REPLAN_REQUIRED", "create-spec-driven-plan"),
    "investigate-existing-codebase": ("DISCOVERY", "CODEBASE_INVESTIGATION_IN_PROGRESS", "investigate-existing-codebase"),
    "brainstorm-idea-with-user": ("DISCOVERY", "BRAINSTORM_IN_PROGRESS", "brainstorm-idea-with-user"),
}
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


def validate_input_handoff(path: Path, progress: dict[str, Any], report: Report) -> None:
    handoff, body = frontmatter(path, report)
    report.errors.extend(validate_shared_handoff({key: "null" if value is None else str(value) for key, value in handoff.items()}, body))
    require_keys(handoff, ("workflow_contract", "handoff_type", "producer_skill", "consumer_skill", "input_revision", "output_revision", "handoff_status", "validation_result"), path, report)
    if (handoff.get("workflow_contract"), handoff.get("handoff_type"), handoff.get("producer_skill"), handoff.get("consumer_skill")) != (CONTRACT, "implementation-to-review", "execute-routed-task", SKILL):
        report.error("IMPLEMENTATION-TO-REVIEW.md is not the canonical v3 review handoff")
    if handoff.get("handoff_status") != "READY" or handoff.get("validation_result") != "PASS":
        report.error("IMPLEMENTATION-TO-REVIEW.md must be READY with PASS validation")
    if handoff.get("output_revision") != progress.get("implementation_revision"):
        report.error("IMPLEMENTATION-TO-REVIEW.md is stale for implementation_revision")
    validate_headings(body, REQUIRED_HANDOFF_HEADINGS, path, report)


def load_findings(findings_dir: Path, report: Report) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not findings_dir.is_dir():
        return records
    for path in sorted(findings_dir.glob("*.md")):
        data, body = frontmatter(path, report)
        data["_path"] = path
        classification = data.get("classification")
        if classification and classification not in CLASSIFICATIONS:
            report.error(f"invalid finding classification '{classification}': {path}")
        if "gap_type" in data:
            required = ("finding_id", "classification", "gap_type", "requirement_ids", "task_id", "evidence_path", "return_owner", "status")
            require_keys(data, required, path, report)
            if data.get("gap_type") not in GAP_TYPES:
                report.error(f"finding gap_type must be one of {sorted(GAP_TYPES)}: {path}")
            requirement_ids = str(data.get("requirement_ids", ""))
            if not requirement_ids or any(not re.fullmatch(r"REQ-\d{3}", item.strip()) for item in requirement_ids.split(",")):
                report.error(f"finding requirement_ids must contain stable REQ IDs: {path}")
            if not re.fullmatch(r"[A-Z]\d{2}-\d{3}", str(data.get("task_id", ""))):
                report.error(f"finding task_id must contain a stable task ID: {path}")
            evidence_path = str(data.get("evidence_path", ""))
            if not evidence_path or Path(evidence_path).is_absolute() or ".." in Path(evidence_path).parts:
                report.error(f"finding evidence_path must be a safe relative path: {path}")
            elif not (findings_dir.parent / evidence_path).is_file():
                report.error(f"finding evidence_path does not exist: {path}")
            if data.get("return_owner") not in RETURN_DESTINATIONS:
                report.error(f"finding return_owner is not a canonical corrective owner: {path}")
            if data.get("status") not in {"OPEN", "RESOLVED"}:
                report.error(f"finding status must be OPEN or RESOLVED: {path}")
            for heading in ("Location", "Traceability and evidence", "What is wrong", "Why it matters", "Suggested resolution", "Routed to"):
                if f"## {heading}" not in body:
                    report.error(f"finding missing section '## {heading}': {path}")
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
    return_owners = {f.get("return_owner") for f in open_blocking if f.get("return_owner") in RETURN_DESTINATIONS}

    if progress:
        report.errors.extend(validate_shared_progress({key: "null" if value is None else str(value) for key, value in progress.items()}))
        require_keys(progress, (
            "workflow_contract", "project_id", "project_slug", "stage", "status",
            "required_skill", "successor_skill", "handoff_status", "review_revision",
            "next_action", "blockers", "last_validation_command", "last_validation_result",
            "updated_at",
        ), paths["progress"], report)
        if progress.get("workflow_contract") != CONTRACT:
            report.error(f"PROGRESS.md workflow_contract must be '{CONTRACT}'")
        if status in {"REVIEW_REQUIRED", "REVIEW_IN_PROGRESS", "CHANGES_REQUIRED", "REVIEW_APPROVED"}:
            if progress.get("stage") != "REVIEW":
                report.error(f"PROGRESS.md stage must be 'REVIEW', got '{progress.get('stage')}'")
            if progress.get("stage_owner") != SKILL:
                report.error("PROGRESS.md stage_owner must be review-implementation-evidence")
        elif len(return_owners) == 1:
            owner = next(iter(return_owners))
            expected_stage, expected_status, expected_required = RETURN_DESTINATIONS[owner]
            if (progress.get("stage"), status, progress.get("required_skill")) != (expected_stage, expected_status, expected_required):
                report.error(f"review return for {owner} must set {expected_stage}/{expected_status} with required_skill {expected_required}")
            if owner in {"investigate-existing-codebase", "brainstorm-idea-with-user"} and progress.get("writer_skill") != owner:
                report.error(f"review return to {owner} must acquire that discovery writer lock")
        else:
            report.error(f"invalid review status or ambiguous return owners: {status}")
        if status == "REVIEW_APPROVED":
            if open_blocking:
                report.error(f"REVIEW_APPROVED with open BLOCKING/HIGH findings: {[f.get('finding_id') for f in open_blocking]}")
            if progress.get("required_skill") != "validate-release-readiness":
                report.error("required_skill must be 'validate-release-readiness' once REVIEW_APPROVED")
            if not paths["to_release"].is_file():
                report.error(f"missing required handoff: {paths['to_release']}")
            if paths["to_implementation"].is_file():
                report.error("both REVIEW-TO-IMPLEMENTATION.md and REVIEW-TO-RELEASE.md exist; only one may be current")
            if not findings and "No findings" not in report_body:
                report.error("clean REVIEW_APPROVED must state 'No findings' without creating an empty finding")
        elif status == "CHANGES_REQUIRED":
            if not open_blocking:
                report.error("CHANGES_REQUIRED requires at least one open BLOCKING/HIGH finding")
            if progress.get("required_skill") != "execute-routed-task":
                report.error("required_skill must be 'execute-routed-task' when CHANGES_REQUIRED")
            if not paths["to_implementation"].is_file():
                report.error(f"missing required handoff: {paths['to_implementation']}")
            if return_owners and return_owners != {"execute-routed-task"}:
                report.error("CHANGES_REQUIRED findings must return only to execute-routed-task")
        elif status in {"REVIEW_REQUIRED", "REVIEW_IN_PROGRESS"}:
            if not paths["input_handoff"].is_file():
                report.error(f"missing required handoff: {paths['input_handoff']}")
            else:
                validate_input_handoff(paths["input_handoff"], progress, report)
        if status == "REVIEW_IN_PROGRESS":
            if progress.get("writer_skill") != SKILL or progress.get("writer_task") is not None:
                report.error("REVIEW_IN_PROGRESS requires only the reviewer writer lock")
        elif status in {"REVIEW_REQUIRED", "CHANGES_REQUIRED", "REVIEW_APPROVED"} and (progress.get("writer_skill") is not None or progress.get("writer_task") is not None):
            report.error("only REVIEW_IN_PROGRESS may hold a review writer lock")

        registry = base / "routing" / "MODEL-CAPABILITIES.md"
        if status == "REVIEW_IN_PROGRESS":
            if not registry.is_file():
                report.error("missing strict routing model registry")
            else:
                models = {row["Model ID"] for row in table_records(registry, {"Model ID", "Tier"})}
                if progress.get("active_reviewer_model") not in models:
                    report.error("active_reviewer_model is not registered")

    if review_report:
        require_keys(review_report, (
            "workflow_contract", "project_id", "project_slug", "review_revision",
            "implementation_revision_reviewed", "outcome", "updated_at",
        ), paths["report"], report)
        if review_report.get("workflow_contract") != CONTRACT:
            report.error(f"REVIEW-REPORT.md uses the wrong workflow contract: {paths['report']}")
        if review_report.get("implementation_revision_reviewed") != progress.get("implementation_revision"):
            report.error("REVIEW-REPORT.md is stale for implementation_revision")
        validate_headings(report_body, REQUIRED_REPORT_HEADINGS, paths["report"], report)
        validate_links(report_body, paths["report"], report)
        if PLACEHOLDER_RE.search(report_body):
            report.error(f"placeholder remains in {paths['report']}")
        cited = set(FINDING_ID_RE.findall(report_body))
        declared = {f.get("finding_id") for f in findings if f.get("finding_id") and f.get("gap_type") in GAP_TYPES}
        missing = cited - declared
        if missing:
            report.error(f"REVIEW-REPORT.md cites findings absent from findings/: {sorted(missing)}")
        uncited = declared - cited
        if uncited:
            report.error(f"REVIEW-REPORT.md omits findings present in findings/: {sorted(uncited)}")

        expected_outcomes = {
            "execute-routed-task": "CHANGES_REQUIRED",
            "route-ai-work-by-capability": "REROUTE_REQUIRED",
            "create-spec-driven-plan": "REPLAN_REQUIRED",
            "investigate-existing-codebase": "CODEBASE_INVESTIGATION_IN_PROGRESS",
            "brainstorm-idea-with-user": "BRAINSTORM_IN_PROGRESS",
        }
        if len(return_owners) == 1:
            owner = next(iter(return_owners))
            if review_report.get("outcome") != expected_outcomes[owner]:
                report.error(f"review outcome must be {expected_outcomes[owner]} for return owner {owner}")
        elif status == "REVIEW_APPROVED" and not open_blocking and review_report.get("outcome") != "REVIEW_APPROVED":
            report.error("review without open BLOCKING/HIGH findings must use REVIEW_APPROVED outcome")

    for name, handoff_path in (("to_implementation", paths["to_implementation"]), ("to_release", paths["to_release"])):
        if not handoff_path.is_file():
            continue
        handoff, handoff_body = frontmatter(handoff_path, report)
        report.errors.extend(validate_shared_handoff({key: "null" if value is None else str(value) for key, value in handoff.items()}, handoff_body))
        require_keys(handoff, (
            "workflow_contract", "handoff_type", "project_id", "producer_skill", "consumer_skill",
            "input_revision", "output_revision", "handoff_status", "validation_command",
            "validation_result", "generated_at",
        ), handoff_path, report)
        if handoff.get("producer_skill") != SKILL:
            report.error(f"handoff producer_skill must be '{SKILL}': {handoff_path}")
        expected_type = "review-to-implementation" if name == "to_implementation" else "review-to-release"
        expected_consumer = "execute-routed-task" if name == "to_implementation" else "validate-release-readiness"
        if handoff.get("workflow_contract") != CONTRACT:
            report.error(f"handoff workflow_contract must be '{CONTRACT}': {handoff_path}")
        if handoff.get("handoff_type") != expected_type:
            report.error(f"handoff_type must be '{expected_type}': {handoff_path}")
        if handoff.get("consumer_skill") != expected_consumer:
            report.error(f"handoff consumer_skill must be '{expected_consumer}': {handoff_path}")
        if handoff.get("handoff_status") != "READY" or handoff.get("validation_result") != "PASS":
            report.error(f"outgoing review handoff must be READY with PASS validation: {handoff_path}")
        if handoff.get("input_revision") != progress.get("implementation_revision"):
            report.error(f"outgoing review handoff has stale implementation revision: {handoff_path}")
        if handoff.get("output_revision") != progress.get("review_revision"):
            report.error(f"outgoing review handoff does not match review_revision: {handoff_path}")
        validate_headings(handoff_body, REQUIRED_HANDOFF_HEADINGS, handoff_path, report)
        validate_links(handoff_body, handoff_path, report)
        if PLACEHOLDER_RE.search(handoff_body) and handoff.get("handoff_status") == "READY":
            report.error(f"placeholder remains in READY handoff: {handoff_path}")

    if status not in {"CHANGES_REQUIRED", "REVIEW_APPROVED"} and (paths["to_implementation"].is_file() or paths["to_release"].is_file()):
        report.error("only implementation corrections and approvals may produce outgoing review handoffs")

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
