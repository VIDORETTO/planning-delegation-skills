#!/usr/bin/env python3
"""Validate skill-team/v3 codebase-investigation artifacts (stdlib only).

Usage:
    python validate_investigation.py docs/ai/<project-slug>

Exit code 0 on PASS, non-zero on FAIL.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any

REPOSITORY_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(REPOSITORY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_SCRIPTS))
from workflow_contract import validate_handoff as validate_shared_handoff, validate_progress as validate_shared_progress

CONTRACT = "skill-team/v3"
SKILL = "investigate-existing-codebase"
SUCCESSOR = "create-spec-driven-plan"
READY_STATUS = "DISCOVERY_READY"
ALLOWED_STATUSES = {READY_STATUS, "CODEBASE_INVESTIGATION_IN_PROGRESS", "DISCOVERY_BLOCKED"}
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?)?$")
FORBIDDEN_FIELD_RE = re.compile(r"(?m)^next_skill\s*:")
EVIDENCE_ID_RE = re.compile(r"\bEV-\d{3}\b")

REQUIRED_INVESTIGATION_HEADINGS = (
    "Identification", "Stack and structure", "Root cause / pattern to follow",
    "Change impact map", "Relevant existing patterns", "Open technical questions",
    "Assumptions (not independently confirmed)",
    "Contradictions with prior product assumptions", "Readiness checklist",
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


def section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$\r?\n(.*?)(?=^##\s+|\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def validate_links(text: str, path: Path, report: Report) -> None:
    for raw in LINK_RE.findall(text):
        target = raw.strip().strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).resolve().exists():
            report.error(f"broken local link '{raw}': {path}")


def validate_dates(data: dict[str, Any], path: Path, report: Report) -> None:
    value = data.get("updated_at")
    if value is None:
        return
    if not isinstance(value, str) or not ISO_RE.match(value):
        report.error(f"'updated_at' must be ISO-8601: {path}")


def validate_no_next_skill(text: str, path: Path, report: Report) -> None:
    if FORBIDDEN_FIELD_RE.search(text):
        report.error(f"'next_skill' is forbidden in skill-team/v3 artifacts: {path}")


def project_root(project_dir: Path) -> Path | None:
    if project_dir.parent.name == "ai" and project_dir.parent.parent.name == "docs":
        return project_dir.parent.parent.parent
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path, help="docs/ai/<project-slug>")
    parser.add_argument("--allow-in-progress", action="store_true", help="validate an unfinished investigation")
    args = parser.parse_args(argv)
    report = Report()
    base = args.project_dir.resolve()

    paths = {
        "progress": base / "PROGRESS.md",
        "investigation": base / "discovery" / "codebase" / "INVESTIGATION.md",
        "evidence": base / "discovery" / "codebase" / "EVIDENCE.md",
        "handoff": base / "handoffs" / "CODEBASE-TO-PLAN.md",
    }
    for name in ("progress", "investigation", "evidence"):
        if not paths[name].is_file():
            report.error(f"missing required document: {paths[name]}")

    progress, _ = frontmatter(paths["progress"], report) if paths["progress"].is_file() else ({}, "")
    investigation, investigation_body = frontmatter(paths["investigation"], report) if paths["investigation"].is_file() else ({}, "")
    evidence, evidence_body = frontmatter(paths["evidence"], report) if paths["evidence"].is_file() else ({}, "")

    status = progress.get("status")
    ready = status == READY_STATUS
    if ready or not args.allow_in_progress:
        if not paths["handoff"].is_file():
            report.error(f"missing required READY handoff: {paths['handoff']}")
    handoff, handoff_body = frontmatter(paths["handoff"], report) if paths["handoff"].is_file() else ({}, "")

    if progress:
        report.errors.extend(validate_shared_progress({key: "null" if value is None else str(value) for key, value in progress.items()}))
        require_keys(progress, (
            "workflow_contract", "project_id", "project_slug", "stage", "status", "stage_owner",
            "required_skill", "successor_skill", "handoff_status", "discovery_revision",
            "active_artifact", "writer_skill", "next_action", "blockers",
            "last_validation_command", "last_validation_result", "updated_at",
        ), paths["progress"], report)
        if progress.get("workflow_contract") != CONTRACT:
            report.error(f"PROGRESS.md workflow_contract must be '{CONTRACT}'")
        if progress.get("stage") != "DISCOVERY":
            report.error(f"PROGRESS.md stage must be 'DISCOVERY' while this skill owns it, got '{progress.get('stage')}'")
        if status not in ALLOWED_STATUSES:
            report.error(f"invalid investigation status: {status}")
        if not args.allow_in_progress and status == "CODEBASE_INVESTIGATION_IN_PROGRESS":
            report.error("status is still IN_PROGRESS; pass --allow-in-progress to validate a partial investigation")
        expected_required = SKILL if not ready else SUCCESSOR
        if progress.get("required_skill") != expected_required:
            report.error(f"required_skill must be '{expected_required}' for status '{status}', got '{progress.get('required_skill')}'")
        if progress.get("successor_skill") != SUCCESSOR:
            report.error(f"successor_skill must be '{SUCCESSOR}', got '{progress.get('successor_skill')}'")
        expected_handoff = "READY" if ready else "NOT_READY"
        if progress.get("handoff_status") != expected_handoff:
            report.error(f"handoff_status must be '{expected_handoff}' when status is '{status}'")
        expected_artifact = f"docs/ai/{progress.get('project_slug')}/discovery/codebase/INVESTIGATION.md"
        if progress.get("active_artifact") != expected_artifact:
            report.error(f"active_artifact must be '{expected_artifact}'")
        validate_dates(progress, paths["progress"], report)

    if investigation:
        require_keys(investigation, (
            "workflow_contract", "project_id", "project_slug", "discovery_revision",
            "investigation_type", "updated_at",
        ), paths["investigation"], report)
        if investigation.get("workflow_contract") != CONTRACT:
            report.error(f"INVESTIGATION.md uses the wrong workflow contract: {paths['investigation']}")
        validate_dates(investigation, paths["investigation"], report)
        validate_headings(investigation_body, REQUIRED_INVESTIGATION_HEADINGS, paths["investigation"], report)
        validate_links(investigation_body, paths["investigation"], report)
        if PLACEHOLDER_RE.search(investigation_body):
            report.error(f"placeholder remains in {paths['investigation']}")
        cited = set(EVIDENCE_ID_RE.findall(investigation_body))
        declared = set(EVIDENCE_ID_RE.findall(evidence_body)) if evidence_body else set()
        missing = cited - declared
        if missing:
            report.error(f"INVESTIGATION.md cites evidence IDs absent from EVIDENCE.md: {sorted(missing)}")
        if ready:
            unchecked = re.findall(r"^- \[ \] .+$", section(investigation_body, "Readiness checklist"), re.MULTILINE)
            if unchecked:
                report.error("DISCOVERY_READY has an incomplete readiness checklist")
            root_cause = section(investigation_body, "Root cause / pattern to follow")
            if not root_cause or not EVIDENCE_ID_RE.search(root_cause):
                report.error("DISCOVERY_READY requires root cause / pattern evidence with an EV-* reference")

    if handoff:
        report.errors.extend(validate_shared_handoff({key: "null" if value is None else str(value) for key, value in handoff.items()}, handoff_body))
        require_keys(handoff, (
            "workflow_contract", "handoff_type", "project_id", "producer_skill", "consumer_skill",
            "input_revision", "output_revision", "handoff_status", "validation_command",
            "validation_result", "generated_at",
        ), paths["handoff"], report)
        expected = {
            "workflow_contract": CONTRACT, "handoff_type": "codebase-to-plan",
            "producer_skill": SKILL, "consumer_skill": SUCCESSOR,
        }
        for key, value in expected.items():
            if handoff.get(key) != value:
                report.error(f"handoff {key} must be '{value}', got '{handoff.get(key)}'")
        if ready and handoff.get("handoff_status") != "READY":
            report.error("handoff_status must be READY when investigation status is DISCOVERY_READY")
        if ready and handoff.get("output_revision") != investigation.get("discovery_revision"):
            report.error("handoff output_revision does not match INVESTIGATION.md discovery_revision")
        if ready and handoff.get("validation_result") != "PASS":
            report.error("READY handoff must record validation_result: PASS")
        validate_headings(handoff_body, REQUIRED_HANDOFF_HEADINGS, paths["handoff"], report)
        validate_links(handoff_body, paths["handoff"], report)
        if PLACEHOLDER_RE.search(handoff_body):
            report.error(f"placeholder remains in {paths['handoff']}")

    revisions = {str(v) for v in (progress.get("discovery_revision"), investigation.get("discovery_revision")) if v is not None}
    if handoff:
        revisions.add(str(handoff.get("output_revision")))
    if len(revisions) > 1:
        report.error(f"discovery_revision is not synchronized across artifacts: {sorted(revisions)}")

    for path in paths.values():
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            validate_no_next_skill(text, path, report)

    root = project_root(base)
    if root is None:
        report.error(f"project directory must follow <root>/docs/ai/<slug>: {base}")
    elif ready:
        agents = root / "AGENTS.md"
        if not agents.is_file():
            report.error(f"missing project discovery index: {agents}")
        else:
            agents_text = agents.read_text(encoding="utf-8")
            if agents_text.count("## AI workflow") != 1:
                report.error("AGENTS.md must contain exactly one '## AI workflow' section")
            pointer = f"docs/ai/{base.name}/PROGRESS.md"
            if pointer not in agents_text:
                report.error(f"AGENTS.md does not point to '{pointer}'")
            validate_no_next_skill(agents_text, agents, report)

    print(f"workflow_contract={CONTRACT}")
    print(f"skill={SKILL}")
    print(f"status={status or 'UNKNOWN'}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.errors:
        print(f"INVESTIGATION INVALID ({len(report.errors)} errors)")
        return 1
    print("INVESTIGATION VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
