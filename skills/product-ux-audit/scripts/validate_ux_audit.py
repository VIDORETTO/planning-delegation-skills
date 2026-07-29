#!/usr/bin/env python3
"""Validate skill-team/v3 UX audit artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPOSITORY_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(REPOSITORY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_SCRIPTS))
from workflow_contract import validate_handoff as validate_shared_handoff, validate_progress as validate_shared_progress

CONTRACT = "skill-team/v3"
SKILL = "product-ux-audit"
SUCCESSOR = "create-spec-driven-plan"
NATURE = {"OBSERVED_DEFECT", "EVIDENCE_BASED_RECOMMENDATION", "PRODUCT_DECISION_REQUIRED"}
IMPACT = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
BANNED = ("spec-driven-dev", "next_skill:", "--break-system-packages")
HANDOFF_SECTIONS = ("Identification", "Summary", "Artifact inventory", "Preserved decisions", "Allowed open questions", "Blockers", "Consumer write scope", "Forbidden files", "Commands and results", "Stop instruction")


def frontmatter(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", line)
        if match:
            data[match.group(1)] = match.group(2).strip("\"'")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--allow-in-progress", action="store_true")
    args = parser.parse_args()
    root = args.project_dir
    errors: list[str] = []

    progress_path = root / "PROGRESS.md"
    if not progress_path.is_file():
        errors.append("missing PROGRESS.md")
    else:
        progress = frontmatter(progress_path)
        errors.extend(validate_shared_progress(progress))
        if progress.get("workflow_contract") != CONTRACT:
            errors.append("workflow_contract must be skill-team/v3")
        status = progress.get("status")
        if progress.get("stage") != "DISCOVERY" or status not in {"UX_AUDIT_IN_PROGRESS", "DISCOVERY_READY", "DISCOVERY_BLOCKED"}:
            errors.append("UX audit requires canonical DISCOVERY stage and status")
        expected_required = SUCCESSOR if status == "DISCOVERY_READY" else SKILL
        if progress.get("required_skill") != expected_required:
            errors.append("required_skill does not match UX audit state")
        expected_writer = "null" if status != "UX_AUDIT_IN_PROGRESS" else SKILL
        if progress.get("writer_skill") != expected_writer:
            errors.append("writer_skill does not match UX audit state")

    ux = root / "discovery" / "ux"
    for name in ("SITEMAP.md", "COVERAGE.md", "UX-AUDIT.md"):
        path = ux / name
        if not path.is_file():
            if args.allow_in_progress and name == "UX-AUDIT.md":
                continue
            errors.append(f"missing {path.as_posix()}")
        else:
            text = path.read_text(encoding="utf-8")
            for banned in BANNED:
                if banned in text:
                    errors.append(f"banned token '{banned}' in {path}")
            if name == "UX-AUDIT.md" and not args.allow_in_progress:
                if PLACEHOLDER_RE.search(text):
                    errors.append("placeholders remain in UX-AUDIT.md")

    handoff = root / "handoffs" / "UX-AUDIT-TO-PLAN.md"
    if handoff.is_file():
        data = frontmatter(handoff)
        handoff_body = handoff.read_text(encoding="utf-8").split("---", 2)[-1]
        errors.extend(validate_shared_handoff(data, handoff_body))
        if data.get("workflow_contract") != CONTRACT:
            errors.append("handoff workflow_contract invalid")
        if data.get("handoff_status") == "READY" and data.get("validation_result") != "PASS":
            errors.append("READY handoff requires validation_result PASS")
        expected = {"handoff_type": "ux-audit-to-plan", "producer_skill": SKILL, "consumer_skill": SUCCESSOR}
        for field, value in expected.items():
            if data.get(field) != value:
                errors.append(f"handoff {field} must be {value}")
        text = handoff.read_text(encoding="utf-8")
        for heading in HANDOFF_SECTIONS:
            if f"## {heading}" not in text:
                errors.append(f"handoff missing section: {heading}")
        if "APPROVED" not in text.upper() and data.get("handoff_status") == "READY":
            errors.append("ready UX handoff must list approved findings")
    elif not args.allow_in_progress:
        errors.append("missing canonical UX-AUDIT-TO-PLAN handoff")

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    print(f"workflow_contract={CONTRACT}")
    print(f"skill={SKILL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
