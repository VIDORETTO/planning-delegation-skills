#!/usr/bin/env python3
"""Deterministically analyze planning artifacts and render their consistency report."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote

TASK_RE = re.compile(r"^###\s+\[[ xX~!]\]\s+(?P<id>[A-Z][A-Z0-9]*-\d{3})\s+[—-]", re.MULTILINE)
REQ_RE = re.compile(r"\bREQ-\d{3}\b")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
VAGUE_RE = re.compile(r"\b(?:fast|secure|intuitive|robust)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    finding_id: str
    severity: str
    category: str
    location: str
    detail: str
    disposition: str


def _location(path: Path, root: Path, offset: int = 0) -> str:
    text = path.read_text(encoding="utf-8")
    return f"{path.relative_to(root).as_posix()}:{text[:offset].count(chr(10)) + 1}"


def _finding(severity: str, category: str, location: str, detail: str) -> Finding:
    key = f"{category}|{location}|{detail}".encode("utf-8")
    finding_id = "ANA-" + hashlib.sha256(key).hexdigest()[:12].upper()
    return Finding(finding_id, severity, category, location, detail, "REMEDIATE" if severity == "BLOCKING" else "REVIEW")


def _frontmatter(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    return {key.strip(): value.strip().strip('"\'') for line in lines[1:end] if ":" in line for key, value in [line.split(":", 1)]}


def _section(text: str, title: str) -> str:
    match = re.search(rf"(?ms)^##\s+{re.escape(title)}\s*$\n(.*?)(?=^##\s+|\Z)", text)
    return match.group(1) if match else ""


def _requirements(spec: Path) -> dict[str, str]:
    if not spec.is_file():
        return {}
    text = spec.read_text(encoding="utf-8")
    records: dict[str, str] = {}
    for section in ("Functional requirements", "Quality requirements"):
        body = _section(text, section)
        matches = list(re.finditer(r"(?m)^-\s+(REQ-\d{3}):\s*(.+)$", body))
        for index, match in enumerate(matches):
            block = body[match.start():matches[index + 1].start() if index + 1 < len(matches) else len(body)]
            state = re.search(r"(?im)^\s*-?\s*State:\s*(\S+)", block)
            if not state or state.group(1).upper() == "ACTIVE":
                records[match.group(1)] = block
    return records


def _tasks(project: Path) -> tuple[dict[str, tuple[Path, int, set[str]]], list[Finding]]:
    records: dict[str, tuple[Path, int, set[str]]] = {}
    findings: list[Finding] = []
    phases = sorted((project / "plan" / "phases").glob("*.md")) if (project / "plan" / "phases").is_dir() else []
    for path in phases:
        text = path.read_text(encoding="utf-8")
        matches = list(TASK_RE.finditer(text))
        for index, match in enumerate(matches):
            task_id = match.group("id")
            block = text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)]
            requirement_line = re.search(r"(?im)^Requirement IDs:\s*(.*)$", block)
            requirements = set(REQ_RE.findall(requirement_line.group(1) if requirement_line else ""))
            line = text[:match.start()].count("\n") + 1
            if task_id in records:
                findings.append(_finding("BLOCKING", "DUPLICATE_TASK", f"{path.relative_to(project).as_posix()}:{line}", f"task ID {task_id} occurs more than once"))
            records[task_id] = (path, line, requirements)
    return records, findings


def _dependencies(project: Path, tasks: dict[str, tuple[Path, int, set[str]]]) -> list[Finding]:
    graph: dict[str, list[str]] = {}
    findings: list[Finding] = []
    for task_id, (path, line, _) in tasks.items():
        text = path.read_text(encoding="utf-8")
        start = next(match.end() for match in TASK_RE.finditer(text) if match.group("id") == task_id)
        after = text[start:]
        next_task = TASK_RE.search(after)
        block = after[:next_task.start() if next_task else len(after)]
        dependencies = re.search(r"(?ims)^####\s+Dependencies\s*$\n(.*?)(?=^####\s+|\Z)", block)
        graph[task_id] = re.findall(r"\b[A-Z][A-Z0-9]*-\d{3}\b", dependencies.group(1) if dependencies else "")
        for dependency in graph[task_id]:
            if dependency not in tasks:
                findings.append(_finding("BLOCKING", "INVALID_DEPENDENCY", f"{path.relative_to(project).as_posix()}:{line}", f"{task_id} depends on unknown task {dependency}"))
    visited: set[str] = set()
    visiting: list[str] = []
    def visit(task_id: str) -> None:
        if task_id in visiting:
            cycle = visiting[visiting.index(task_id):] + [task_id]
            path, line, _ = tasks[task_id]
            findings.append(_finding("BLOCKING", "DEPENDENCY_CYCLE", f"{path.relative_to(project).as_posix()}:{line}", " -> ".join(cycle)))
            return
        if task_id in visited:
            return
        visiting.append(task_id)
        for dependency in graph.get(task_id, []):
            if dependency in tasks:
                visit(dependency)
        visiting.pop()
        visited.add(task_id)
    for task_id in sorted(tasks):
        visit(task_id)
    return findings


def analyze(project: Path) -> dict:
    """Return a stable analysis result for a workflow root without writing it."""
    project = project.resolve()
    progress = _frontmatter(project / "PROGRESS.md")
    requirements = _requirements(project / "plan" / "SPEC.md")
    tasks, findings = _tasks(project)
    task_requirements = {req for _, _, reqs in tasks.values() for req in reqs}
    for requirement in sorted(requirements):
        if requirement not in task_requirements:
            findings.append(_finding("BLOCKING", "UNCOVERED_REQUIREMENT", "plan/SPEC.md", f"active requirement {requirement} has no task"))
    for task_id, (path, line, reqs) in sorted(tasks.items()):
        if not reqs or not reqs.intersection(requirements):
            findings.append(_finding("BLOCKING", "ORPHAN_TASK", f"{path.relative_to(project).as_posix()}:{line}", f"task {task_id} has no active requirement"))
    findings.extend(_dependencies(project, tasks))

    for path in sorted(project.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = unquote(match.group(1).strip().strip("<>").split("#", 1)[0])
            if target and not target.startswith(("http://", "https://", "mailto:")) and not (path.parent / target).resolve().exists():
                findings.append(_finding("BLOCKING", "INVALID_PATH", _location(path, project, match.start()), f"local link target does not exist: {target}"))
        if path.name in {"SPEC.md", "GLOSSARY.md"}:
            for match in VAGUE_RE.finditer(text):
                findings.append(_finding("ADVISORY", "AMBIGUITY", _location(path, project, match.start()), f"unquantified term: {match.group(0).lower()}"))

    assertions: dict[str, tuple[bool, Path, int]] = {}
    for path in sorted((project / "plan").rglob("*.md")) if (project / "plan").is_dir() else []:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"(?im)^.*?\bmust\s+(not\s+)?([^.!\n]+)", text):
            subject = re.sub(r"\s+", " ", match.group(2).lower()).strip()
            negative = bool(match.group(1))
            if subject in assertions and assertions[subject][0] != negative:
                _, prior_path, prior_offset = assertions[subject]
                detail = f"contradictory MUST statements for: {subject}"
                findings.append(_finding("ADVISORY", "CONTRADICTION", _location(prior_path, project, prior_offset), detail))
                findings.append(_finding("ADVISORY", "CONTRADICTION", _location(path, project, match.start()), detail))
            else:
                assertions[subject] = (negative, path, match.start())

    glossary = project / "GLOSSARY.md"
    if glossary.is_file():
        for line in glossary.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*-\s*([^:]+):.*\b(?:deprecated|use)\s+`?([^`.,]+)", line, re.IGNORECASE)
            if not match:
                continue
            deprecated = match.group(1).strip()
            for path in sorted((project / "plan").rglob("*.md")):
                for occurrence in re.finditer(rf"\b{re.escape(deprecated)}\b", path.read_text(encoding="utf-8"), re.IGNORECASE):
                    findings.append(_finding("ADVISORY", "TERMINOLOGY_DRIFT", _location(path, project, occurrence.start()), f"deprecated term: {deprecated}"))

    check = project / "plan" / "GOVERNANCE-CHECK.md"
    if check.is_file():
        text = check.read_text(encoding="utf-8")
        governance_text = (project / "GOVERNANCE.md").read_text(encoding="utf-8") if (project / "GOVERNANCE.md").is_file() else ""
        for match in re.finditer(r"(?ms)^###\s+(GOV-\d{3}).*?^Result:\s*CONFLICT\s*$.*?^Confirmed:\s*true\s*$", text):
            principle = re.search(rf"(?ms)^###\s+{re.escape(match.group(1))}\b.*?^Classification:\s*(\S+)\s*$", governance_text)
            severity = "BLOCKING" if principle and principle.group(1) == "MUST" else "ADVISORY"
            findings.append(_finding(severity, "GOVERNANCE_VIOLATION", _location(check, project, match.start()), f"confirmed governance conflict: {match.group(1)}"))

    expected_revision = str(progress.get("plan_revision", ""))
    for path in sorted((project / "plan").rglob("*.md")) if (project / "plan").is_dir() else []:
        if path.name == "CONSISTENCY-REPORT.md":
            continue
        match = re.search(r"(?im)^Specification revision:\s*(\d+)\s*$", path.read_text(encoding="utf-8"))
        if match and match.group(1) != expected_revision:
            findings.append(_finding("BLOCKING", "STALE_REVISION", _location(path, project, match.start()), f"specification revision {match.group(1)} does not match plan revision {expected_revision}"))

    findings = sorted(set(findings), key=lambda item: (item.location, item.category, item.finding_id))
    metrics = {
        "active_requirements": len(requirements), "tasks": len(tasks),
        "covered_requirements": len(set(requirements).intersection(task_requirements)),
        "orphan_tasks": sum(f.category == "ORPHAN_TASK" for f in findings),
        "blocking_findings": sum(f.severity == "BLOCKING" for f in findings),
        "advisory_findings": sum(f.severity == "ADVISORY" for f in findings),
    }
    return {"analysis_version": "1", "plan_revision": expected_revision, "metrics": metrics, "findings": [asdict(item) for item in findings]}


def render_report(result: dict) -> str:
    lines = ["# Plan Consistency Report", "", f"- Analysis version: {result['analysis_version']}", f"- Plan revision: {result['plan_revision']}", "- Deterministic: true", "", "## Metrics", "", "| Metric | Value |", "|---|---:|"]
    lines.extend(f"| {name.replace('_', ' ')} | {result['metrics'][name]} |" for name in sorted(result["metrics"]))
    lines.extend(["", "## Findings", ""])
    if not result["findings"]:
        lines.append("No findings.")
    for finding in result["findings"]:
        lines.extend([f"### {finding['finding_id']} - {finding['category']}", "", f"- Severity: {finding['severity']}", f"- Location: {finding['location']}", f"- Detail: {finding['detail']}", f"- Disposition: {finding['disposition']}", ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("planning_dir", type=Path)
    parser.add_argument("--write", action="store_true", help="write plan/CONSISTENCY-REPORT.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = analyze(args.planning_dir)
    if args.write:
        report = args.planning_dir / "plan" / "CONSISTENCY-REPORT.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(render_report(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else render_report(result), end="")
    return 1 if result["metrics"]["blocking_findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
