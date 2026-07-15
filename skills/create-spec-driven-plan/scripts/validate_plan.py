#!/usr/bin/env python3
"""Validate the planning stage of a planning-delegation/v2 project."""

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


def validate() -> tuple[dict, int]:
    args = parse_args(); supplied = args.planning_dir.resolve()
    project, plan = locate(supplied)
    errors: list[str] = []; warnings: list[str] = []
    if not project.is_dir():
        return {"planning_dir": str(project), "errors": ["planning directory not found"], "warnings": []}, 2
    progress, fm_errors = parse_frontmatter(project / "PROGRESS.md"); errors.extend(fm_errors)
    required_progress = {"workflow_contract", "project_id", "project_slug", "stage", "status", "active_skill", "next_skill", "handoff_status", "brainstorm_revision", "plan_revision", "routing_revision", "plan_based_on_brainstorm_revision", "active_artifact", "current_task", "next_action", "blockers", "last_validation", "updated_at"}
    errors.extend(f"PROGRESS.md missing field: {key}" for key in sorted(required_progress - progress.keys()))
    if progress.get("workflow_contract") != "planning-delegation/v2": errors.append("unsupported workflow_contract")
    if not args.artifact_only and progress.get("stage") not in {"BRAINSTORM", "PLAN"}: errors.append("planning skill received incompatible stage")
    status = progress.get("status"); validated = status == "PLAN_VALIDATED"
    allowed_status = {"BRAINSTORM_READY", "PLAN_IN_PROGRESS", "PLAN_VALIDATED", "REPLAN_REQUIRED"}
    if not args.artifact_only and status not in allowed_status: errors.append(f"incompatible planning status: {status}")
    if progress.get("updated_at"):
        try: datetime.fromisoformat(str(progress["updated_at"]))
        except ValueError: errors.append("updated_at is not valid ISO-8601")

    required_docs = ["00-MASTER.md", "ANALYSIS.md", "PRODUCT-SCOPE.md", "USER-JOURNEYS.md", "BUSINESS-RULES.md", "ARCHITECTURE.md", "DOMAIN-DATA.md", "API-CONTRACTS.md", "SECURITY.md", "OPERATIONS.md", "QUALITY-EVALUATION.md", "ROADMAP.md", "TRACEABILITY.md", "DECISIONS-RISKS.md", "REFERENCES.md", "HISTORY.md"]
    for name in required_docs:
        if not (plan / name).is_file(): errors.append(f"missing core document: plan/{name}")
    for name in ["SOURCE-REGISTER.md", "CONTEXT-INDEX.md", "GLOSSARY.md"]:
        if not (project / name).is_file(): errors.append(f"missing shared document: {name}")

    md_files = sorted(project.rglob("*.md")); phase_files = sorted((plan / "phases").glob("*.md")) if (plan / "phases").is_dir() else []
    tasks = parse_tasks(phase_files, project); errors.extend(local_link_errors(md_files, project)); errors.extend(graph_errors(tasks))
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

    trace, trace_errors = parse_traceability(plan / "TRACEABILITY.md"); errors.extend(trace_errors)
    task_ids = set(task_by_id); traced_tasks = set().union(*trace.values()) if trace else set()
    for req, mapped in trace.items():
        if not mapped: errors.append(f"requirement has no task: {req}")
        for task_id in mapped:
            if task_id not in task_ids: errors.append(f"traceability references unknown task: {req} -> {task_id}")
    for task in tasks:
        if task.task_id not in traced_tasks: errors.append(f"task missing from traceability: {task.task_id}")
        for req in task.requirements:
            if req not in trace: errors.append(f"task references requirement absent from traceability: {task.task_id} -> {req}")

    current = progress.get("current_task")
    if current and current not in task_ids: errors.append(f"PROGRESS.md current_task does not exist: {current}")
    next_task = None
    match = re.search(r"\b[A-Z][A-Z0-9]*-\d{3}\b", str(progress.get("next_action") or ""))
    if match: next_task = match.group(0)
    if next_task:
        if next_task not in task_by_id: errors.append(f"PROGRESS.md next task does not exist: {next_task}")
        else:
            incomplete = [dep for dep in task_by_id[next_task].dependencies if task_by_id.get(dep) and task_by_id[dep].state != "COMPLETE"]
            if incomplete: errors.append(f"next task has incomplete dependencies: {next_task} -> {', '.join(incomplete)}")

    incoming = project / "handoffs" / "BRAINSTORM-TO-PLAN.md"
    incoming_rev = handoff_revision(incoming, "Brainstorm revision")
    if not incoming.is_file(): errors.append("missing input handoff: handoffs/BRAINSTORM-TO-PLAN.md")
    elif incoming_rev != progress.get("brainstorm_revision"): errors.append("brainstorm revision mismatch between progress and input handoff")
    if progress.get("plan_based_on_brainstorm_revision") not in {None, progress.get("brainstorm_revision")}:
        errors.append("plan_based_on_brainstorm_revision is stale")

    output = project / "handoffs" / "PLAN-TO-ROUTING.md"
    if validated:
        if progress.get("stage") != "PLAN" or progress.get("active_skill") != "create-spec-driven-plan" or progress.get("next_skill") != "route-ai-work-by-capability" or progress.get("handoff_status") != "READY": errors.append("PLAN_VALIDATED transition fields are incompatible")
        if progress.get("plan_based_on_brainstorm_revision") != progress.get("brainstorm_revision"): errors.append("validated plan is not based on current brainstorm revision")
        out_plan_rev = handoff_revision(output, "Plan revision")
        out_brain_rev = handoff_revision(output, "Brainstorm revision used")
        if not output.is_file(): errors.append("missing output handoff: handoffs/PLAN-TO-ROUTING.md")
        elif out_plan_rev != progress.get("plan_revision") or out_brain_rev != progress.get("brainstorm_revision"): errors.append("output handoff revisions do not match PROGRESS.md")
        for path in md_files:
            for match in PLACEHOLDER_RE.finditer(path.read_text(encoding="utf-8")):
                errors.append(f"placeholder in validated plan: {path.relative_to(project)}:{path.read_text(encoding='utf-8')[:match.start()].count(chr(10))+1}")
    elif output.is_file() and progress.get("handoff_status") == "READY" and not args.artifact_only: warnings.append("output handoff exists before PLAN_VALIDATED")

    report = {
        "workflow_contract": progress.get("workflow_contract"), "stage": progress.get("stage"), "status": status,
        "planning_dir": str(project), "brainstorm_revision": progress.get("brainstorm_revision"), "plan_revision": progress.get("plan_revision"),
        "markdown_files": len(md_files), "phases": len(phase_files), "tasks": len(tasks), "requirements": len(trace),
        "dependency_graph": "VALID" if not graph_errors(tasks) else "INVALID", "errors": list(dict.fromkeys(errors)), "warnings": warnings,
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
