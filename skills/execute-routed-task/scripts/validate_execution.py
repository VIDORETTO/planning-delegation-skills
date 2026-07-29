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

REPOSITORY_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(REPOSITORY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_SCRIPTS))
from workflow_contract import validate_handoff as validate_shared_handoff, validate_progress as validate_shared_progress

CONTRACT = "skill-team/v3"
SKILL = "execute-routed-task"
COMPLETE_STATUS = "IMPLEMENTATION_COMPLETE"
ALLOWED_STATUSES = {COMPLETE_STATUS, "TASK_IN_PROGRESS", "TASK_BLOCKED", "TASK_COMPLETE"}
ALLOWED_SUCCESSORS = {"review-implementation-evidence", "validate-release-readiness"}
BLOCKER_OWNERS = {
    SKILL, "route-ai-work-by-capability", "create-spec-driven-plan",
    "investigate-existing-codebase", "brainstorm-idea-with-user",
}
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?)?$")
FORBIDDEN_FIELD_RE = re.compile(r"(?m)^next_skill\s*:")
TASK_RE = re.compile(r"^###\s+\[(?P<state>[ xX~!])\]\s+(?P<task>[A-Z][A-Z0-9]*-\d{3})\b", re.MULTILINE)

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
    """Read one strict Markdown table without accepting alternate routing formats."""
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


def validate_routing_input(base: Path, progress: dict[str, Any], report: Report) -> tuple[dict[str, dict[str, str]], set[str]]:
    """Check the immutable v3 routing source consumed by implementation."""
    routing = base / "routing" / "ROUTING.md"
    models = base / "routing" / "MODEL-CAPABILITIES.md"
    input_handoff = base / "handoffs" / "ROUTING-TO-IMPLEMENTATION.md"
    plan = base / "plan"
    for path in (routing, models, input_handoff, plan):
        if not path.exists():
            report.error(f"missing strict routing input: {path}")
    if not all(path.exists() for path in (routing, models, input_handoff, plan)):
        return {}, set()
    handoff, handoff_body = frontmatter(input_handoff, report)
    report.errors.extend(validate_shared_handoff({key: "null" if value is None else str(value) for key, value in handoff.items()}, handoff_body))
    if (handoff.get("workflow_contract"), handoff.get("handoff_type"), handoff.get("producer_skill"), handoff.get("consumer_skill")) != (CONTRACT, "routing-to-implementation", "route-ai-work-by-capability", SKILL):
        report.error("ROUTING-TO-IMPLEMENTATION.md is not the canonical v3 execution handoff")
    if handoff.get("handoff_status") != "READY" or handoff.get("validation_result") != "PASS":
        report.error("ROUTING-TO-IMPLEMENTATION.md must be READY with PASS validation")
    if handoff.get("input_revision") != progress.get("plan_revision") or handoff.get("output_revision") != progress.get("routing_revision"):
        report.error("ROUTING-TO-IMPLEMENTATION.md has stale plan or routing revision")
    routes = table_records(routing, {"Task", "Executor", "Reviewer", "Review mode"})
    if not routes:
        report.error("ROUTING.md lacks canonical assignment table")
        return {}, set()
    route_map = {row["Task"]: row for row in routes}
    model_rows = table_records(models, {"Model ID", "Tier"})
    registered = {row["Model ID"] for row in model_rows}
    if not registered:
        report.error("MODEL-CAPABILITIES.md lacks canonical model registry")
    completed = set()
    for path in plan.rglob("*.md"):
        for match in TASK_RE.finditer(path.read_text(encoding="utf-8")):
            if match.group("state").lower() == "x":
                completed.add(match.group("task"))
    if set(route_map) - completed and progress.get("status") == COMPLETE_STATUS:
        report.error(f"IMPLEMENTATION_COMPLETE has unfinished routed tasks: {sorted(set(route_map) - completed)}")
    return route_map, registered


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
    }
    for name in ("progress", "evidence", "history"):
        if not paths[name].is_file():
            report.error(f"missing required document: {paths[name]}")

    progress, _ = frontmatter(paths["progress"], report) if paths["progress"].is_file() else ({}, "")
    status = progress.get("status")
    complete = status == COMPLETE_STATUS
    consumer = progress.get("required_skill")
    handoff_type = "implementation-to-release" if consumer == "validate-release-readiness" else "implementation-to-review"
    handoff_name = "IMPLEMENTATION-TO-RELEASE.md" if handoff_type == "implementation-to-release" else "IMPLEMENTATION-TO-REVIEW.md"
    paths["handoff"] = base / "handoffs" / handoff_name

    if complete and not paths["handoff"].is_file():
        report.error(f"missing required READY handoff: {paths['handoff']}")
    handoff, handoff_body = frontmatter(paths["handoff"], report) if paths["handoff"].is_file() else ({}, "")

    if progress:
        report.errors.extend(validate_shared_progress({key: "null" if value is None else str(value) for key, value in progress.items()}))
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
        if progress.get("stage_owner") != SKILL:
            report.error("PROGRESS.md stage_owner must be execute-routed-task")
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
        elif status in {"TASK_IN_PROGRESS", "TASK_COMPLETE"}:
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
            if progress.get("required_skill") not in BLOCKER_OWNERS:
                report.error("TASK_BLOCKED must name the classified owner of the return")

        routes, registered_models = validate_routing_input(base, progress, report)
        active_task = progress.get("active_task")
        active_model = progress.get("active_executor_model")
        if status == "TASK_IN_PROGRESS":
            if active_task not in routes:
                report.error("active_task must be a routed task")
            elif active_model != routes[active_task]["Executor"]:
                report.error("active_executor_model does not match routed executor")
            if active_model not in registered_models:
                report.error("active_executor_model is not registered")
            if progress.get("writer_skill") != SKILL or progress.get("writer_task") != active_task:
                report.error("TASK_IN_PROGRESS requires the executor writer lock for active_task")
        elif progress.get("writer_skill") is not None or progress.get("writer_task") is not None:
            report.error("only TASK_IN_PROGRESS may hold an implementation writer lock")
        if complete and routes:
            review_required = any(row["Review mode"] != "NONE" for row in routes.values())
            expected_consumer = "review-implementation-evidence" if review_required else "validate-release-readiness"
            if consumer != expected_consumer:
                report.error("required_skill does not match routing review policy")

    if handoff:
        report.errors.extend(validate_shared_handoff({key: "null" if value is None else str(value) for key, value in handoff.items()}, handoff_body))
        require_keys(handoff, (
            "workflow_contract", "handoff_type", "project_id", "producer_skill", "consumer_skill",
            "input_revision", "output_revision", "handoff_status", "validation_command",
            "validation_result", "generated_at",
        ), paths["handoff"], report)
        if handoff.get("workflow_contract") != CONTRACT:
            report.error(f"handoff workflow_contract must be '{CONTRACT}'")
        if handoff.get("handoff_type") != handoff_type:
            report.error(f"handoff_type must be '{handoff_type}'")
        if handoff.get("producer_skill") != SKILL:
            report.error(f"handoff producer_skill must be '{SKILL}'")
        if handoff.get("consumer_skill") != consumer:
            report.error(f"handoff consumer_skill must be '{consumer}'")
        if complete and handoff.get("handoff_status") != "READY":
            report.error("handoff_status must be READY when IMPLEMENTATION_COMPLETE")
        if complete and handoff.get("output_revision") != progress.get("implementation_revision"):
            report.error("handoff output_revision does not match PROGRESS.md implementation_revision")
        if complete and handoff.get("input_revision") != progress.get("routing_revision"):
            report.error("handoff input_revision does not match PROGRESS.md routing_revision")
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
