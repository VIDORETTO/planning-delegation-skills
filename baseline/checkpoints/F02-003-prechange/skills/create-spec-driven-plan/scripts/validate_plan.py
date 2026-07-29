#!/usr/bin/env python3
"""Validate the planning stage of a skill-team/v3 project."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

REPOSITORY_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(REPOSITORY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_SCRIPTS))
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))
from workflow_contract import validate_handoff as validate_shared_handoff, validate_progress as validate_shared_progress
from analyze_plan import analyze as analyze_consistency, render_report

TASK_HEADING_RE = re.compile(
    r"^###\s+\[(?P<mark>[ xX~!])\]\s+(?P<id>[A-Z][A-Z0-9]*-\d{3})\s+[—-]\s+(?P<title>.+)$"
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ID_RE = re.compile(r"\b([A-Z][A-Z0-9]*-\d{3})\b")
REQ_RE = re.compile(r"\bREQ-\d{3}\b")
PLACEHOLDER_RE = re.compile(r"<(?!(?:https?://))[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
ALLOWED_STATES = {"PENDING", "IN_PROGRESS", "BLOCKED", "COMPLETE", "CANCELLED"}
REQUIRED_TASK_SECTIONS = {
    "why this task exists",
    "mandatory reading",
    "dependencies",
    "write scope",
    "outside scope",
    "observable objective",
    "inputs, outputs and errors",
    "invariants",
    "security and privacy",
    "expected implementation",
    "test cases",
    "acceptance criteria",
    "rollback",
    "required evidence",
    "escalation",
}


@dataclass
class Task:
    task_id: str
    title: str
    file: str
    line: int
    mark: str
    state: str | None = None
    executor: str | None = None
    reviewer: str | None = None
    requirements: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    sections: set[str] = field(default_factory=set)
    acceptance: str = ""
    evidence: str = ""
    blocker: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("planning_dir", type=Path, help="Project workflow root (docs/ai/<slug>)")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--artifact-only", action="store_true", help="validate archived plan artifacts inside a later workflow stage")
    return parser.parse_args()


def scalar(value: str):
    value = value.strip()
    if value in {"null", "~"}: return None
    if value == "[]": return []
    if value.lower() in {"true", "false"}: return value.lower() == "true"
    if re.fullmatch(r"-?\d+", value): return int(value)
    return value.strip('"\'')


def parse_frontmatter(path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    if not path.is_file(): return {}, [f"missing operational pointer: {path.name}"]
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---": return {}, ["PROGRESS.md has no YAML frontmatter"]
    try: end = lines.index("---", 1)
    except ValueError: return {}, ["PROGRESS.md frontmatter is not closed"]
    data: dict = {}
    parent: str | None = None
    for number, raw in enumerate(lines[1:end], 2):
        if not raw.strip() or raw.lstrip().startswith("#"): continue
        if raw.startswith("  ") and parent and ":" in raw:
            key, value = raw.strip().split(":", 1)
            data.setdefault(parent, {})[key] = scalar(value)
        elif ":" in raw:
            key, value = raw.split(":", 1)
            key = key.strip(); value = value.strip()
            data[key] = {} if not value else scalar(value)
            parent = key if not value else None
        else: errors.append(f"invalid frontmatter line {number}: {raw}")
    return data, errors


def locate(root: Path) -> tuple[Path, Path]:
    if (root / "PROGRESS.md").is_file(): return root, root / "plan"
    if root.name.lower() == "plan" and (root.parent / "PROGRESS.md").is_file(): return root.parent, root
    return root, root / "plan"


def field(block: str, label: str) -> str | None:
    match = re.search(rf"(?im)^{re.escape(label)}:\s*(.+?)\s*$", block)
    return match.group(1).strip() if match else None


def section_body(block: str, title: str) -> str:
    pattern = rf"(?ims)^####\s+{re.escape(title)}\s*$\n(.*?)(?=^####\s+|\Z)"
    match = re.search(pattern, block)
    return match.group(1).strip() if match else ""


def parse_tasks(files: list[Path], root: Path) -> list[Task]:
    tasks: list[Task] = []
    for path in files:
        lines = path.read_text(encoding="utf-8").splitlines()
        starts = [i for i, line in enumerate(lines) if TASK_HEADING_RE.match(line)]
        for pos, start in enumerate(starts):
            end = starts[pos + 1] if pos + 1 < len(starts) else len(lines)
            heading = TASK_HEADING_RE.match(lines[start]); assert heading
            block = "\n".join(lines[start + 1:end])
            sections = {m.group(1).strip().lower() for m in re.finditer(r"(?m)^####\s+(.+?)\s*$", block)}
            deps_body = section_body(block, "Dependencies")
            deps = [x for x in ID_RE.findall(deps_body) if x != heading.group("id")]
            task = Task(
                task_id=heading.group("id"), title=heading.group("title").strip(),
                file=path.relative_to(root).as_posix(), line=start + 1, mark=heading.group("mark"),
                state=field(block, "State"), executor=field(block, "Executor"), reviewer=field(block, "Reviewer"),
                requirements=REQ_RE.findall(field(block, "Requirement IDs") or ""),
                decisions=re.findall(r"\bDEC-\d{3}\b", field(block, "Decision IDs") or ""),
                dependencies=deps, sections=sections,
                acceptance=section_body(block, "Acceptance criteria"),
                evidence=section_body(block, "Required evidence"),
                blocker=section_body(block, "Blocker"),
            )
            if re.search(rf"(?im)^\s*-\s*{re.escape(task.task_id)}\s*$", deps_body):
                task.dependencies.append(task.task_id)
            tasks.append(task)
    return tasks


def local_link_errors(files: list[Path], root: Path) -> list[str]:
    errors: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")): continue
            target = unquote(target.split("#", 1)[0])
            if target and not (path.parent / target).resolve().exists():
                errors.append(f"broken local link: {path.relative_to(root)} -> {target}")
    return errors


def graph_errors(tasks: list[Task]) -> list[str]:
    errors: list[str] = []
    ids = {task.task_id for task in tasks}
    graph = {task.task_id: task.dependencies for task in tasks}
    for task in tasks:
        for dep in task.dependencies:
            if dep == task.task_id: errors.append(f"task depends on itself: {task.task_id}")
            elif dep not in ids: errors.append(f"unknown dependency: {task.task_id} -> {dep}")
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(node: str, trail: list[str]):
        if node in visiting:
            cycle = trail[trail.index(node):] + [node]
            errors.append("dependency cycle: " + " -> ".join(cycle)); return
        if node in visited: return
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep in graph: visit(dep, trail + [dep])
        visiting.remove(node); visited.add(node)
    for task_id in graph: visit(task_id, [task_id])
    return list(dict.fromkeys(errors))


def parse_traceability(path: Path) -> tuple[dict[str, set[str]], list[str]]:
    mapping: dict[str, set[str]] = {}; errors: list[str] = []
    if not path.is_file(): return mapping, ["missing core document: plan/TRACEABILITY.md"]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"): continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or not re.fullmatch(r"REQ-\d{3}", cells[0]): continue
        if len(cells) < 9: errors.append(f"traceability row has fewer than 9 columns: {cells[0]}"); continue
        mapping[cells[0]] = set(re.findall(r"\b[A-Z][A-Z0-9]*-\d{3}\b", cells[5]))
        if not cells[1] or not cells[6]: errors.append(f"traceability origin/oracle empty: {cells[0]}")
    return mapping, errors


def handoff_revision(path: Path, label: str) -> int | None:
    if not path.is_file(): return None
    match = re.search(rf"(?im)^-\s*{re.escape(label)}:\s*(\d+)\s*$", path.read_text(encoding="utf-8"))
    return int(match.group(1)) if match else None


DISCOVERY_HANDOFFS = {
    "BRAINSTORM-TO-PLAN.md": "brainstorm-to-plan",
    "CODEBASE-TO-PLAN.md": "codebase-to-plan",
    "UX-AUDIT-TO-PLAN.md": "ux-audit-to-plan",
}


def discover_input_handoffs(project: Path) -> list[Path]:
    """Return only canonical discovery inputs; no legacy filename is a fallback."""
    handoffs = project / "handoffs"
    return [handoffs / name for name in DISCOVERY_HANDOFFS if (handoffs / name).is_file()]


DISCOVERY_PRODUCERS = {
    "brainstorm-to-plan": "brainstorm-idea-with-user",
    "codebase-to-plan": "investigate-existing-codebase",
    "ux-audit-to-plan": "product-ux-audit",
}
COMPACT_BRIEF_PATH = Path("discovery/COMPACT-BRIEF.md")
COMPACT_BRIEF_HEADINGS = ("Problem", "Outcome", "Actors", "Requirements", "Structural questions")
GOVERNANCE_PROFILES = {"standard", "critical"}
GOVERNANCE_RESULT_VALUES = {"PASS", "CONFLICT", "EXCEPTION"}
SPEC_SECTIONS = (
    "Identification", "Problem and intended outcome", "Actors and authority",
    "Scope of the first usable release", "Non-goals", "Prioritized user journeys",
    "Functional requirements", "Quality requirements", "Key entities and lifecycle",
    "Edge, failure, and recovery cases", "Success criteria", "Assumptions",
    "Rejected and deferred options", "Open decisions", "Source and revision references",
)
TECHNICAL_DETAIL_RE = re.compile(
    r"\b(?:python|java(?:script)?|typescript|react|vue|angular|django|flask|fastapi|"
    r"postgres(?:ql)?|mysql|mongodb|redis|kubernetes|docker|aws|azure|gcp)\b", re.IGNORECASE
)
CHECKLIST_DOMAINS = {
    "requirements-completeness", "requirement-clarity", "internal-consistency",
    "acceptance-measurability", "scenario-coverage", "authorization-isolation",
    "data-retention-deletion", "integration-failure-retry", "migration-rollback",
    "observability-redaction", "assumptions-dependencies",
}
CHECKLIST_REQUIRED_DOMAINS = {
    "requirements-completeness", "requirement-clarity", "internal-consistency",
    "acceptance-measurability", "scenario-coverage", "assumptions-dependencies",
}
CHECKLIST_ITEM_RE = re.compile(
    r"(?m)^-\s+\[(?P<checked>[ xX])\]\s+(?P<id>CHK-\d{3})\s+-\s+(?P<question>.+?)\s+\[(?P<marker>REQ-\d{3}|Gap|Ambiguity|Conflict|Assumption)\]\s*$"
)
IMPLEMENTATION_CHECK_RE = re.compile(
    r"\b(?:test that|verify (?:the )?(?:button|endpoint|implementation)|returns? HTTP|button works)\b",
    re.IGNORECASE,
)


def governance_blocks(text: str) -> list[tuple[str, str]]:
    """Return numbered governance records split on their level-three headings."""
    matches = list(re.finditer(r"(?m)^###\s+((?:GOV|EXC)-\d{3})\b.*$", text))
    return [
        (match.group(1), text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)])
        for index, match in enumerate(matches)
    ]


def governance_value(block: str, label: str) -> str | None:
    return field(block, label)


def validate_governance(project: Path, profile: str) -> tuple[list[str], list[str]]:
    """Validate the deterministic governance gate without interpreting policy semantics."""
    errors: list[str] = []
    warnings: list[str] = []
    governance_path = project / "GOVERNANCE.md"
    check_path = project / "plan" / "GOVERNANCE-CHECK.md"
    required = profile in GOVERNANCE_PROFILES

    if not governance_path.is_file() and not check_path.is_file():
        if required:
            errors.append("missing governance records for profile=" + profile)
        return errors, warnings
    if not governance_path.is_file():
        errors.append("missing governance record: GOVERNANCE.md")
    if not check_path.is_file():
        errors.append("missing governance check: plan/GOVERNANCE-CHECK.md")
    if errors:
        return errors, warnings

    governance_text = governance_path.read_text(encoding="utf-8")
    check_text = check_path.read_text(encoding="utf-8")
    version = re.search(r"(?im)^Governance version:\s*(\S.*?)\s*$", governance_text)
    if not version:
        errors.append("GOVERNANCE.md missing Governance version")
    for required_heading in ("Authority and precedence", "Principles", "Amendment process", "Authorized exceptions"):
        if not re.search(rf"(?im)^##\s+{re.escape(required_heading)}\s*$", governance_text):
            errors.append(f"GOVERNANCE.md missing section: {required_heading}")
    authority_text = governance_text.lower()
    for term in ("applicable law", "stronger security controls", "explicit user decisions"):
        if term not in authority_text:
            errors.append(f"GOVERNANCE.md authority precedence does not document: {term}")

    principles: dict[str, str] = {}
    exceptions: dict[str, str] = {}
    for record_id, block in governance_blocks(governance_text):
        if record_id.startswith("GOV-"):
            classification = governance_value(block, "Classification")
            if classification not in {"MUST", "SHOULD", "MAY"}:
                errors.append(f"governance principle has invalid Classification: {record_id}")
            principles[record_id] = classification or ""
        else:
            principle = governance_value(block, "Principle")
            authorized_by = governance_value(block, "Authorized by")
            rationale = governance_value(block, "Rationale")
            if not principle or not authorized_by or not rationale:
                errors.append(f"governance exception is incomplete: {record_id}")
            else:
                exceptions[record_id] = principle

    if not principles:
        errors.append("GOVERNANCE.md contains no GOV-* principles")
    for required_heading in ("Check timing", "Results"):
        if not re.search(rf"(?im)^##\s+{re.escape(required_heading)}\s*$", check_text):
            errors.append(f"GOVERNANCE-CHECK.md missing section: {required_heading}")
    check_version = re.search(r"(?im)^Governance version:\s*(\S.*?)\s*$", check_text)
    if not check_version:
        errors.append("GOVERNANCE-CHECK.md missing Governance version")
    elif version and check_version.group(1) != version.group(1):
        errors.append("governance versions do not match")

    seen_phases: set[tuple[str, str]] = set()
    for principle_id, block in governance_blocks(check_text):
        if not principle_id.startswith("GOV-"):
            continue
        result = governance_value(block, "Result")
        confirmed = governance_value(block, "Confirmed")
        phase = governance_value(block, "Phase")
        exception_id = governance_value(block, "Exception ID")
        authorized_by = governance_value(block, "Authorized by")
        rationale = governance_value(block, "Rationale")
        if principle_id not in principles:
            errors.append(f"governance check references unknown principle: {principle_id}")
        if result not in GOVERNANCE_RESULT_VALUES:
            errors.append(f"governance check has invalid Result: {principle_id}")
        if confirmed not in {"true", "false"}:
            errors.append(f"governance check has invalid Confirmed value: {principle_id}")
        if phase not in {"BEFORE_DESIGN", "AFTER_DESIGN"}:
            errors.append(f"governance check has invalid Phase: {principle_id}")
        elif (principle_id, phase) in seen_phases:
            errors.append(f"governance check duplicates principle and phase: {principle_id} {phase}")
        elif phase:
            seen_phases.add((principle_id, phase))
        if result == "CONFLICT" and confirmed == "true" and principles.get(principle_id) == "MUST":
            errors.append(f"confirmed MUST conflict blocks plan validation: {principle_id}")
        if result == "EXCEPTION":
            if exception_id not in exceptions or exceptions.get(exception_id) != principle_id:
                errors.append(f"governance exception is not traceable: {principle_id}")
            if not authorized_by or authorized_by == "NONE" or not rationale or rationale == "NONE":
                errors.append(f"governance exception lacks authorization or rationale: {principle_id}")
        elif exception_id not in {None, "NONE"}:
            errors.append(f"governance check has exception without EXCEPTION result: {principle_id}")
        if result == "CONFLICT" and confirmed == "false":
            warnings.append(f"unconfirmed governance conflict: {principle_id}")

    for principle_id in principles:
        phases = {phase for item, phase in seen_phases if item == principle_id}
        if phases != {"BEFORE_DESIGN", "AFTER_DESIGN"}:
            errors.append(f"governance principle is not checked before and after design: {principle_id}")
    return errors, warnings


def validate_discovery_handoff(path: Path, discovery_revision: int | str) -> list[str]:
    """Validate a ready discovery input independently of unrelated inputs."""
    data, errors = parse_frontmatter(path)
    body = path.read_text(encoding="utf-8").split("---", 2)[-1] if path.is_file() else ""
    errors.extend(validate_shared_handoff({key: "null" if value is None else str(value) for key, value in data.items()}, body))
    required = {"workflow_contract", "handoff_type", "project_id", "producer_skill", "consumer_skill", "input_revision", "output_revision", "handoff_status", "validation_command", "validation_result", "generated_at"}
    errors.extend(f"{path.name} missing field: {field}" for field in sorted(required - data.keys()))
    handoff_type = data.get("handoff_type")
    if data.get("workflow_contract") != "skill-team/v3":
        errors.append(f"{path.name} has unsupported workflow_contract")
    if handoff_type not in DISCOVERY_PRODUCERS:
        errors.append(f"{path.name} has invalid discovery handoff_type")
    elif data.get("producer_skill") != DISCOVERY_PRODUCERS[handoff_type]:
        errors.append(f"{path.name} producer does not match handoff_type")
    if data.get("consumer_skill") != "create-spec-driven-plan":
        errors.append(f"{path.name} consumer must be create-spec-driven-plan")
    if data.get("handoff_status") != "READY" or data.get("validation_result") != "PASS":
        errors.append(f"{path.name} must be READY with validation_result PASS")
    for field in ("input_revision", "output_revision"):
        if str(data.get(field)) != str(discovery_revision):
            errors.append(f"{path.name} {field} does not match discovery_revision")
    return errors


def validate_compact_brief(path: Path) -> list[str]:
    """A compact brief is valid only when no structural question remains."""
    if not path.is_file():
        return ["compact brief is missing"]
    text = path.read_text(encoding="utf-8")
    errors = []
    for heading in COMPACT_BRIEF_HEADINGS:
        match = re.search(rf"^##\s+{re.escape(heading)}\s*$\r?\n(.*?)(?=^##\s+|\Z)", text, re.MULTILINE | re.DOTALL)
        if not match or not match.group(1).strip():
            errors.append(f"compact brief missing section: {heading}")
        elif heading == "Structural questions" and match.group(1).strip().upper() not in {"NONE", "- NONE"}:
            errors.append("compact brief contains unresolved structural questions")
    return errors


def spec_section(text: str, title: str) -> str:
    match = re.search(
        rf"(?ms)^##\s+{re.escape(title)}\s*$\n(.*?)(?=^##\s+|\Z)", text
    )
    return match.group(1).strip() if match else ""


def spec_records(section: str) -> list[tuple[str, str]]:
    """Return a requirement ID and its nested metadata without changing its stable identity."""
    matches = list(re.finditer(r"(?m)^-\s+(REQ-\d{3}):\s*(.+)$", section))
    return [
        (
            match.group(1),
            match.group(2) + "\n" + section[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(section)],
        )
        for index, match in enumerate(matches)
    ]


def nested_field(block: str, label: str) -> str:
    match = re.search(rf"(?im)^\s*-?\s*{re.escape(label)}:\s*(.+?)\s*$", block)
    return match.group(1).strip() if match else ""


def validate_spec(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Validate the compact product view, not the detailed discovery source of truth."""
    records: dict[str, dict[str, str]] = {}
    if not path.is_file():
        return records, ["missing core document: plan/SPEC.md"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not re.search(r"(?m)^# Product Specification:\s+\S", text):
        errors.append("SPEC.md missing product specification title")
    for title in SPEC_SECTIONS:
        if not spec_section(text, title):
            errors.append(f"SPEC.md missing section: {title}")

    journeys = spec_section(text, "Prioritized user journeys")
    story_matches = list(re.finditer(r"(?m)^###\s+(US-\d{3})\s+-\s+.+\s+\(P([1-9])\)\s*$", journeys))
    if not story_matches:
        errors.append("SPEC.md contains no prioritized user journeys")
    for index, match in enumerate(story_matches):
        story_id = match.group(1)
        block = journeys[match.end():story_matches[index + 1].start() if index + 1 < len(story_matches) else len(journeys)]
        for heading in ("Why this priority", "Independent value", "Acceptance scenarios"):
            if not section_body(block, heading):
                errors.append(f"SPEC.md story missing {heading}: {story_id}")
        scenarios = section_body(block, "Acceptance scenarios")
        if scenarios and not re.search(r"(?is)\bGiven\b.+\bWhen\b.+\bThen\b", scenarios):
            errors.append(f"SPEC.md story lacks Given/When/Then scenario: {story_id}")

    for title in ("Functional requirements", "Quality requirements"):
        for req_id, block in spec_records(spec_section(text, title)):
            if req_id in records:
                errors.append(f"SPEC.md requirement ID occurs more than once: {req_id}")
                continue
            metadata = {label: nested_field(block, label) for label in (
                "Origin", "Priority", "Release", "Oracle", "State", "Implementation constraint"
            )}
            records[req_id] = metadata
            for label in ("Origin", "Priority", "Release", "Oracle", "State"):
                if not metadata[label]:
                    errors.append(f"SPEC.md requirement missing {label}: {req_id}")
            if metadata["Origin"] and not re.search(r"\b(?:SRC|CR|EV|UX|ASM|DEC)-\d{3}\b", metadata["Origin"]):
                errors.append(f"SPEC.md requirement origin lacks stable source ID: {req_id}")
            if metadata["State"] and metadata["State"] not in ALLOWED_STATES | {"ACTIVE", "DEFERRED", "REJECTED"}:
                errors.append(f"SPEC.md requirement has invalid State: {req_id}")
            if TECHNICAL_DETAIL_RE.search(block) and metadata["Implementation constraint"].upper() != "EXPLICIT":
                errors.append(f"SPEC.md contains unapproved technical implementation detail: {req_id}")
    if not records:
        errors.append("SPEC.md contains no requirements")
    errors.extend(validate_clarification_records(text))
    return records, errors


def clarification_value(block: str, label: str) -> str:
    match = re.search(rf"(?im)^\s*-\s*{re.escape(label)}:\s*(.*?)\s*$", block)
    return match.group(1).strip() if match else ""


def validate_clarification_records(text: str) -> list[str]:
    """Validate optional planning records; no records means no planning clarification was needed."""
    records = spec_section(text, "Clarification records")
    if not records:
        return []
    matches = list(re.finditer(r"(?m)^###\s+(Q-\d{3})\s*$", records))
    errors: list[str] = []
    questions: dict[str, str] = {}
    decisions: dict[str, tuple[str, str]] = {}
    record_ids: set[str] = set()
    pending_records = 0
    for index, match in enumerate(matches):
        question_id = match.group(1)
        if question_id in record_ids:
            errors.append(f"SPEC.md duplicate clarification question ID: {question_id}")
        record_ids.add(question_id)
        block = records[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(records)]
        values = {label: clarification_value(block, label) for label in (
            "Question", "Decision key", "Scope", "Status", "Asked by", "Answer", "Source", "Authority",
            "Revision", "Recommendation", "Accepted", "Supersedes", "Readiness after answer",
        )}
        for label, value in values.items():
            if not value:
                errors.append(f"SPEC.md clarification record missing {label}: {question_id}")
        if values["Scope"] != "PLAN":
            errors.append(f"SPEC.md clarification record has invalid planning scope: {question_id}")
        status = values["Status"]
        if status not in {"PENDING", "ANSWERED", "SUPERSEDED", "RETURNED_TO_DISCOVERY"}:
            errors.append(f"SPEC.md clarification record has invalid status: {question_id}")
        if values["Asked by"] != "create-spec-driven-plan":
            errors.append(f"SPEC.md clarification record has invalid owner: {question_id}")
        if values["Accepted"] not in {"true", "false"}:
            errors.append(f"SPEC.md clarification record has invalid acceptance state: {question_id}")
        if values["Readiness after answer"] not in {"READY", "NOT_READY", "RETURN_TO_DISCOVERY"}:
            errors.append(f"SPEC.md clarification record has invalid readiness result: {question_id}")
        if not re.fullmatch(r"(?:SRC|DEC|CR|ASM|BR|REQ)-\d{3}", values["Source"]):
            errors.append(f"SPEC.md clarification record source lacks stable ID: {question_id}")
        if not values["Revision"].isdigit() or int(values["Revision"] or "0") < 1:
            errors.append(f"SPEC.md clarification record has invalid revision: {question_id}")
        if status == "PENDING" and (values["Answer"] != "NONE" or values["Accepted"] != "false"):
            errors.append(f"SPEC.md pending clarification cannot contain an accepted answer: {question_id}")
        if status == "PENDING":
            pending_records += 1
        if status == "ANSWERED" and (values["Answer"] == "NONE" or values["Accepted"] != "true"):
            errors.append(f"SPEC.md answered clarification lacks an accepted answer: {question_id}")
        if status == "SUPERSEDED" and not re.fullmatch(r"Q-\d{3}", values["Supersedes"]):
            errors.append(f"SPEC.md superseded clarification must identify its replacement: {question_id}")
        if status == "RETURNED_TO_DISCOVERY" and values["Readiness after answer"] != "RETURN_TO_DISCOVERY":
            errors.append(f"SPEC.md discovery return must recompute readiness: {question_id}")
        normalized_question = re.sub(r"\W+", " ", values["Question"].lower()).strip()
        if normalized_question in questions:
            errors.append(f"SPEC.md duplicate clarification question: {question_id} duplicates {questions[normalized_question]}")
        else:
            questions[normalized_question] = question_id
        if status == "ANSWERED":
            key = values["Decision key"].lower()
            answer = values["Answer"].lower()
            if key in decisions and decisions[key][0] != answer:
                errors.append(f"SPEC.md contradictory active clarification decisions: {question_id} conflicts with {decisions[key][1]}")
            else:
                decisions[key] = (answer, question_id)
    if pending_records > 1:
        errors.append("SPEC.md has more than one pending clarification question")
    return errors


def clarification_blocks_plan_validation(text: str) -> str | None:
    """Return the deterministic reason a pending clarification prevents plan handoff."""
    records = spec_section(text, "Clarification records")
    if re.search(r"(?im)^-\s*Status:\s*RETURNED_TO_DISCOVERY\s*$", records):
        return "PLAN_VALIDATED requires return to brainstorm-idea-with-user for product intent"
    if re.search(r"(?im)^-\s*Status:\s*PENDING\s*$", records):
        return "PLAN_VALIDATED has unresolved clarification records"
    return None


def checklist_value(block: str, label: str) -> str:
    return clarification_value(block, label)


def validate_requirements_checklists(
    project: Path, profile: str, plan_revision: int | str | None, active_requirements: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate requirement-writing checklists and their revision-aware blocking policy."""
    errors: list[str] = []
    warnings: list[str] = []
    directory = project / "plan" / "checklists"
    if not directory.is_dir():
        if profile in {"standard", "critical"}:
            errors.append("missing requirements checklist directory: plan/checklists")
        return errors, warnings

    files = sorted(directory.glob("*.md"))
    domains_seen: set[str] = set()
    item_ids: set[str] = set()
    for path in files:
        domain = path.stem
        prefix = f"checklist {path.relative_to(project).as_posix()}"
        if domain not in CHECKLIST_DOMAINS:
            errors.append(f"{prefix} has unsupported domain: {domain}")
        if domain in domains_seen:
            errors.append(f"{prefix} duplicates domain: {domain}")
        domains_seen.add(domain)
        text = path.read_text(encoding="utf-8")
        title = re.search(r"(?m)^# Requirements Quality Checklist:\s+(.+?)\s*$", text)
        if not title:
            errors.append(f"{prefix} missing checklist title")
        elif title.group(1).strip() != domain:
            errors.append(f"{prefix} title does not match filename domain")
        values = {label: checklist_value(text, label) for label in (
            "Workflow profile", "Applicable", "Applicability rationale", "Specification revision", "Re-evaluation state",
        )}
        if values["Workflow profile"] not in {"compact", "standard", "critical"}:
            errors.append(f"{prefix} has invalid Workflow profile")
        elif values["Workflow profile"] != profile:
            errors.append(f"{prefix} workflow profile does not match PROGRESS.md")
        if values["Applicable"] not in {"true", "false"}:
            errors.append(f"{prefix} has invalid Applicable value")
        if not values["Applicability rationale"] or values["Applicability rationale"].upper() == "NONE":
            errors.append(f"{prefix} lacks applicability rationale")
        if str(values["Specification revision"]) != str(plan_revision):
            errors.append(f"{prefix} is stale for plan_revision")
        if values["Re-evaluation state"] != "CURRENT":
            errors.append(f"{prefix} requires re-evaluation")

        matches = list(CHECKLIST_ITEM_RE.finditer(text))
        parsed_starts = {match.start() for match in matches}
        for candidate in re.finditer(r"(?m)^-\s+\[[ xX]\]\s+(CHK-\d{3})\b.*$", text):
            if candidate.start() not in parsed_starts:
                errors.append(f"{prefix} has malformed checklist item: {candidate.group(1)}")
        if values["Applicable"] == "true" and not matches:
            errors.append(f"{prefix} has no active checklist items")
        for index, match in enumerate(matches):
            item_id = match.group("id")
            if item_id in item_ids:
                errors.append(f"checklist item ID occurs more than once: {item_id}")
            item_ids.add(item_id)
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            block = text[match.end():end]
            severity = checklist_value(block, "Severity")
            state = checklist_value(block, "State")
            traceability = checklist_value(block, "Traceability")
            location = f"{prefix}: {item_id}"
            if IMPLEMENTATION_CHECK_RE.search(match.group("question")):
                errors.append(f"{location} tests implementation behavior instead of written requirements")
            if severity not in {"CRITICAL", "ADVISORY"}:
                errors.append(f"{location} has invalid Severity")
            if state not in {"PASS", "OPEN"}:
                errors.append(f"{location} has invalid State")
            checked = match.group("checked").lower() == "x"
            if (state == "PASS") != checked:
                errors.append(f"{location} checkbox and State disagree")
            marker = match.group("marker")
            if not traceability:
                errors.append(f"{location} lacks traceability")
            elif marker.startswith("REQ-"):
                if marker not in traceability:
                    errors.append(f"{location} requirement marker is not traceable")
                elif active_requirements is not None and marker not in active_requirements:
                    errors.append(f"{location} references inactive or unknown requirement: {marker}")
            if values["Applicable"] == "true" and not checked:
                if severity == "CRITICAL":
                    errors.append(f"unchecked critical checklist item blocks plan validation: {item_id}")
                elif severity == "ADVISORY":
                    warnings.append(f"unchecked advisory checklist item: {item_id}")
    if profile in {"standard", "critical"}:
        for domain in sorted(CHECKLIST_REQUIRED_DOMAINS - domains_seen):
            errors.append(f"missing applicable requirements checklist domain: {domain}")
    return errors, warnings


def validate() -> tuple[dict, int]:
    args = parse_args(); supplied = args.planning_dir.resolve()
    project, plan = locate(supplied)
    errors: list[str] = []; warnings: list[str] = []
    if not project.is_dir():
        return {"planning_dir": str(project), "errors": ["planning directory not found"], "warnings": []}, 2
    progress, fm_errors = parse_frontmatter(project / "PROGRESS.md"); errors.extend(fm_errors)
    if progress:
        normalized_progress = {key: "null" if value is None else str(value) for key, value in progress.items()}
        errors.extend(validate_shared_progress(normalized_progress))
    required_progress = {
        "workflow_contract", "project_id", "project_slug", "workflow_profile", "stage", "status",
        "stage_owner", "required_skill", "successor_skill", "handoff_status", "discovery_revision",
        "plan_revision", "routing_revision", "implementation_revision", "review_revision", "release_revision",
        "active_artifact", "active_task", "active_batch", "active_executor_model", "active_reviewer_model",
        "writer_skill", "writer_task", "next_action", "blockers", "last_validation_command",
        "last_validation_result", "updated_at",
    }
    errors.extend(f"PROGRESS.md missing field: {key}" for key in sorted(required_progress - progress.keys()))
    if progress.get("workflow_contract") != "skill-team/v3":
        errors.append("unsupported workflow_contract")
    if not args.artifact_only and progress.get("stage") not in {"DISCOVERY", "PLANNING"}:
        errors.append("planning skill received incompatible stage")
    status = progress.get("status"); validated = status == "PLAN_VALIDATED"
    allowed_status = {"DISCOVERY_READY", "PLAN_IN_PROGRESS", "PLAN_VALIDATED", "REPLAN_REQUIRED"}
    if not args.artifact_only and status not in allowed_status: errors.append(f"incompatible planning status: {status}")
    if progress.get("updated_at"):
        try: datetime.fromisoformat(str(progress["updated_at"]))
        except ValueError: errors.append("updated_at is not valid ISO-8601")

    profile = str(progress.get("workflow_profile") or "standard").lower()
    if profile not in {"compact", "standard", "critical"}:
        errors.append(f"invalid workflow_profile: {profile}")
        profile = "standard"

    governance_errors, governance_warnings = validate_governance(project, profile)
    errors.extend(governance_errors)
    warnings.extend(governance_warnings)

    compact_docs = ["00-MASTER.md", "SPEC.md", "TRACEABILITY.md", "PLAN-MANIFEST.md"]
    standard_docs = compact_docs + [
        "ANALYSIS.md", "PRODUCT-SCOPE.md", "USER-JOURNEYS.md", "BUSINESS-RULES.md",
        "ARCHITECTURE.md", "DOMAIN-DATA.md", "API-CONTRACTS.md", "SECURITY.md",
        "OPERATIONS.md", "QUALITY-EVALUATION.md", "ROADMAP.md", "DECISIONS-RISKS.md",
        "REFERENCES.md", "HISTORY.md",
    ]
    critical_docs = standard_docs + ["THREAT-MODEL.md", "MIGRATION.md", "ROLLBACK.md", "RELEASE-GATES.md"]
    if profile == "compact":
        required_docs = compact_docs
    elif profile == "critical":
        required_docs = critical_docs
    else:
        required_docs = standard_docs

    for name in required_docs:
        if not (plan / name).is_file():
            errors.append(f"missing core document for profile={profile}: plan/{name}")
    shared_required = ["SOURCE-REGISTER.md"]
    if profile != "compact":
        shared_required.extend(["CONTEXT-INDEX.md", "GLOSSARY.md"])
    for name in shared_required:
        if not (project / name).is_file():
            errors.append(f"missing shared document: {name}")
    if profile == "compact" and not (plan / "PLAN-MANIFEST.md").is_file() and (plan / "00-MASTER.md").is_file():
        warnings.append("compact profile should include plan/PLAN-MANIFEST.md")

    md_files = sorted(project.rglob("*.md")); phase_files = sorted((plan / "phases").glob("*.md")) if (plan / "phases").is_dir() else []
    if validated and not phase_files:
        errors.append("validated plan requires at least one phase file under plan/phases/")
    if "workflow_profile" not in progress:
        warnings.append("PROGRESS.md missing workflow_profile; defaulting to standard")

    tasks = parse_tasks(phase_files, project); errors.extend(local_link_errors(md_files, project)); errors.extend(graph_errors(tasks))
    if validated and progress.get("required_skill") == "route-ai-work-by-capability":
        for task in tasks:
            if (task.executor or "").upper() not in {"UNASSIGNED", ""}:
                warnings.append(f"plan ready for routing but task executor is not UNASSIGNED: {task.task_id}")

    counts = Counter(task.task_id for task in tasks)
    for task_id, count in counts.items():
        if count != 1: errors.append(f"task ID occurs {count} times: {task_id}")
    task_by_id = {task.task_id: task for task in tasks}
    for task in tasks:
        loc = f"{task.file}:{task.line}"
        if task.state not in ALLOWED_STATES: errors.append(f"task has invalid or missing state: {loc}")
        expected_checked = task.state == "COMPLETE"
        if expected_checked != (task.mark.lower() == "x"): errors.append(f"checkbox/state mismatch: {loc}")
        if not task.executor: errors.append(f"task has no Executor: {loc}")
        if not task.reviewer: errors.append(f"task has no Reviewer: {loc}")
        if not task.requirements: errors.append(f"task has no Requirement IDs: {loc}")
        missing = REQUIRED_TASK_SECTIONS - task.sections
        if missing: errors.append(f"task missing sections ({', '.join(sorted(missing))}): {loc}")
        if not task.acceptance or not re.search(r"-\s*\[[ xX]\]\s*\S", task.acceptance): errors.append(f"task acceptance is empty: {loc}")
        if task.state == "COMPLETE" and (not task.evidence or re.search(r"\b(?:none|not_run)\b", task.evidence, re.I)): errors.append(f"COMPLETE task has no evidence: {loc}")
        if task.state == "BLOCKED" and not task.blocker: errors.append(f"BLOCKED task has no Blocker section: {loc}")
    if not tasks: errors.append("no task headings were found in plan/phases")
    if sum(task.state == "IN_PROGRESS" for task in tasks) > 1: errors.append("more than one task is IN_PROGRESS")

    spec, spec_errors = validate_spec(plan / "SPEC.md"); errors.extend(spec_errors)
    checklist_errors, checklist_warnings = validate_requirements_checklists(
        project, profile, progress.get("plan_revision"),
        {req for req, metadata in spec.items() if metadata.get("State") == "ACTIVE"},
    )
    errors.extend(checklist_errors); warnings.extend(checklist_warnings)
    if validated and (plan / "SPEC.md").is_file():
        clarification_blocker = clarification_blocks_plan_validation((plan / "SPEC.md").read_text(encoding="utf-8"))
        if clarification_blocker:
            errors.append(clarification_blocker)
    analysis = analyze_consistency(project)
    analysis_report = plan / "CONSISTENCY-REPORT.md"
    if validated:
        if not analysis_report.is_file():
            errors.append("missing consistency report: plan/CONSISTENCY-REPORT.md")
        elif analysis_report.read_text(encoding="utf-8") != render_report(analysis):
            errors.append("consistency report is stale or was not generated from current artifacts")
        for finding in analysis["findings"]:
            if finding["severity"] == "BLOCKING":
                errors.append(f"consistency analysis blocks routing: {finding['finding_id']} {finding['detail']}")
            else:
                warnings.append(f"consistency analysis advisory: {finding['finding_id']} {finding['detail']}")
    trace, trace_errors = parse_traceability(plan / "TRACEABILITY.md"); errors.extend(trace_errors)
    active_spec_requirements = {req for req, metadata in spec.items() if metadata.get("State") == "ACTIVE"}
    for req in active_spec_requirements:
        if req not in trace:
            errors.append(f"active SPEC requirement absent from traceability: {req}")
    for req in trace:
        if req not in spec:
            errors.append(f"traceability requirement absent from SPEC.md: {req}")
    task_ids = set(task_by_id); traced_tasks = set().union(*trace.values()) if trace else set()
    for req, mapped in trace.items():
        if not mapped: errors.append(f"requirement has no task: {req}")
        for task_id in mapped:
            if task_id not in task_ids: errors.append(f"traceability references unknown task: {req} -> {task_id}")
    for task in tasks:
        if task.task_id not in traced_tasks: errors.append(f"task missing from traceability: {task.task_id}")
        for req in task.requirements:
            if req not in trace: errors.append(f"task references requirement absent from traceability: {task.task_id} -> {req}")
            elif req not in active_spec_requirements:
                errors.append(f"task references inactive SPEC requirement: {task.task_id} -> {req}")

    current = progress.get("active_task")
    if current and current not in task_ids: errors.append(f"PROGRESS.md current_task does not exist: {current}")
    next_task = None
    match = re.search(r"\b[A-Z][A-Z0-9]*-\d{3}\b", str(progress.get("next_action") or ""))
    if match: next_task = match.group(0)
    if next_task:
        if next_task not in task_by_id: errors.append(f"PROGRESS.md next task does not exist: {next_task}")
        else:
            incomplete = [dep for dep in task_by_id[next_task].dependencies if task_by_id.get(dep) and task_by_id[dep].state != "COMPLETE"]
            if incomplete: errors.append(f"next task has incomplete dependencies: {next_task} -> {', '.join(incomplete)}")

    available_inputs = discover_input_handoffs(project)
    compact_brief = project / COMPACT_BRIEF_PATH
    if not available_inputs and not compact_brief.is_file() and progress.get("status") == "DISCOVERY_READY":
        errors.append("missing input handoff: expected a canonical discovery handoff")
    for incoming in available_inputs:
        errors.extend(validate_discovery_handoff(incoming, progress.get("discovery_revision")))
    if compact_brief.is_file():
        errors.extend(validate_compact_brief(compact_brief))

    output = project / "handoffs" / "PLAN-TO-ROUTING.md"
    if validated:
        stage_owner = progress.get("stage_owner")
        required_skill = progress.get("required_skill")
        stage_ok = progress.get("stage") == "PLANNING"
        if not stage_ok or stage_owner != "create-spec-driven-plan" or required_skill != "route-ai-work-by-capability" or progress.get("handoff_status") != "READY":
            errors.append("PLAN_VALIDATED transition fields are incompatible")
        out_plan_rev = handoff_revision(output, "Plan revision")
        out_brain_rev = handoff_revision(output, "Discovery revision used")
        if not output.is_file(): errors.append("missing output handoff: handoffs/PLAN-TO-ROUTING.md")
        elif out_plan_rev != progress.get("plan_revision") or out_brain_rev != progress.get("discovery_revision"): errors.append("output handoff revisions do not match PROGRESS.md")
        else:
            output_data, output_errors = parse_frontmatter(output)
            errors.extend(output_errors)
            errors.extend(validate_shared_handoff({key: "null" if value is None else str(value) for key, value in output_data.items()}, output.read_text(encoding="utf-8").split("---", 2)[-1]))
        for path in md_files:
            for match in PLACEHOLDER_RE.finditer(path.read_text(encoding="utf-8")):
                errors.append(f"placeholder in validated plan: {path.relative_to(project)}:{path.read_text(encoding='utf-8')[:match.start()].count(chr(10))+1}")
    elif output.is_file() and progress.get("handoff_status") == "READY" and not args.artifact_only: warnings.append("output handoff exists before PLAN_VALIDATED")

    report = {
        "workflow_contract": progress.get("workflow_contract"), "stage": progress.get("stage"), "status": status,
        "planning_dir": str(project), "brainstorm_revision": progress.get("brainstorm_revision"), "plan_revision": progress.get("plan_revision"),
        "markdown_files": len(md_files), "phases": len(phase_files), "tasks": len(tasks), "requirements": len(trace),
        "dependency_graph": "VALID" if not graph_errors(tasks) else "INVALID", "errors": list(dict.fromkeys(errors)), "warnings": warnings,
        "consistency_metrics": analysis["metrics"],
        "task_records": [asdict(task) for task in tasks] if args.as_json else None,
    }
    return report, 1 if report["errors"] else 0


def main() -> int:
    report, code = validate()
    if "--json" in sys.argv: print(json.dumps(report, indent=2, ensure_ascii=False, default=list))
    else:
        for key in ("workflow_contract", "stage", "status", "planning_dir", "brainstorm_revision", "plan_revision", "phases", "tasks", "requirements", "dependency_graph"):
            print(f"{key}={report.get(key)}")
        for warning in report.get("warnings", []): print(f"warning: {warning}")
        for error in report.get("errors", []): print(f"error: {error}")
        print("VALID" if not report.get("errors") else "INVALID")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
