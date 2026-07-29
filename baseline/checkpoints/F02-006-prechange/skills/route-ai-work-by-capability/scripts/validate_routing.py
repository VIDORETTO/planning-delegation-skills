#!/usr/bin/env python3
"""Validate strict skill-team/v3 routing semantics and ownership.

Usage:
    python validate_routing.py docs/ai/<project-slug>
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

REPOSITORY_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(REPOSITORY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_SCRIPTS))
from workflow_contract import validate_handoff as validate_shared_handoff, validate_progress as validate_shared_progress

TASK_RE = re.compile(r"^###\s+\[[ xX~!]\]\s+(?P<id>[A-Z][A-Z0-9]*-\d{3})\s+[—-]\s+(?P<title>.+)$")
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d{3}$")
MODEL_RE = re.compile(r"^MODEL-[A-Z0-9_.-]+$")
BATCH_RE = re.compile(r"^[A-Z][A-Z0-9_.-]*-B\d{2,3}$")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
REVIEW_MODES = {"NONE", "SAMPLE", "REQUIRED_BEFORE_COMPLETE", "REQUIRED_BEFORE_RELEASE", "ADVERSARIAL_REVIEW"}
REQUIRED_REVIEW = REVIEW_MODES - {"NONE"}
HARD_GATE_NONE = {"", "NONE", "NO", "N/A", "FALSE"}
SCORE_HEADERS = ["Ambiguity", "Coupling", "Irreversibility", "State/concurrency", "Data correctness", "Verification difficulty", "External variability", "Specification incompleteness"]


@dataclass
class Task:
    task_id: str
    executor: str | None
    reviewer: str | None
    dependencies: list[str]
    state: str | None
    files: set[str]
    components: set[str]
    global_state: str | None
    migration: str | None
    file: str
    line: int


@dataclass
class Route:
    task_id: str
    executor: str
    tier: str
    hard_gate: str
    score: int | None
    confidence: str
    reviewer: str
    review_mode: str
    batch: str
    locks: set[str]
    parallel_eligible: bool | None
    parallel_rationale: str
    isolation_strategy: str
    rationale: str
    line: int


@dataclass
class Batch:
    batch_id: str
    executor: str = ""
    dependencies: list[str] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)
    locks: set[str] = field(default_factory=set)
    execution: str = "SEQUENTIAL"
    isolation_strategy: str = ""
    validation: str = ""
    line: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Workflow root")
    return parser.parse_args()


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


def cells(line: str) -> list[str]:
    if not line.lstrip().startswith("|"):
        return []
    return [item.strip() for item in line.strip().strip("|").split("|")]


def csv_ids(value: str) -> list[str]:
    if value.upper() in {"", "NONE", "N/A"}:
        return []
    return re.findall(r"[A-Z][A-Z0-9]*-\d{3}", value)


def find_field(block: list[str], label: str) -> str | None:
    pattern = re.compile(rf"^(?:[-*]\s*)?(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*:\s*(.+?)\s*$", re.IGNORECASE)
    for line in block:
        match = pattern.match(line.strip())
        if match:
            return match.group(1).strip().strip("`")
    return None


def section_body(block: list[str], title: str) -> str:
    """Extract #### <title> body until the next #### heading."""
    text = "\n".join(block)
    pattern = rf"(?ims)^####\s+{re.escape(title)}\s*$\n(.*?)(?=^####\s+|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def parse_dependencies(block: list[str], task_id: str) -> list[str]:
    """Prefer #### Dependencies / #### Dependências; fall back to inline field."""
    body = section_body(block, "Dependencies") or section_body(block, "Dependências")
    if body:
        deps = [x for x in re.findall(r"[A-Z][A-Z0-9]*-\d{3}", body) if x != task_id]
        if re.search(rf"(?im)^\s*-\s*{re.escape(task_id)}\s*$", body):
            deps.append(task_id)
        if body.upper().strip() in {"NONE", "- NONE", "N/A"} or (
            not deps and re.search(r"(?im)\bNONE\b", body)
        ):
            return []
        return deps
    dep_value = find_field(block, "Dependencies") or find_field(block, "Dependências") or "NONE"
    return csv_ids(dep_value)


def parse_tasks(root: Path) -> list[Task]:
    result: list[Task] = []
    for path in sorted(root.rglob("*.md")):
        if path.name.upper() == "ROUTING.MD" or "handoffs" in {p.lower() for p in path.parts}:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        headings = [(i, TASK_RE.match(line)) for i, line in enumerate(lines)]
        headings = [(i, m) for i, m in headings if m]
        for pos, (index, match) in enumerate(headings):
            end = headings[pos + 1][0] if pos + 1 < len(headings) else len(lines)
            block = lines[index + 1:end]
            task_id = match.group("id")
            executor = find_field(block, "Executor") or find_field(block, "Owner")
            reviewer = find_field(block, "Reviewer")
            deps = parse_dependencies(block, task_id)
            files = set(csv_scope(find_field(block, "Allowed files") or ""))
            components = set(csv_scope(find_field(block, "Allowed components") or ""))
            result.append(Task(
                task_id, executor, reviewer, deps, find_field(block, "State"), files, components,
                find_field(block, "Global state"), find_field(block, "Migration"),
                path.relative_to(root).as_posix(), index + 1,
            ))
    return result


def csv_scope(value: str) -> list[str]:
    if value.upper() in {"", "NONE", "N/A"}:
        return []
    return [item.strip().strip("`") for item in re.split(r"[,;]", value) if item.strip()]


def table_records(path: Path, required_headers: set[str]) -> tuple[list[str], list[tuple[dict[str, str], int]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        header = cells(line)
        if required_headers.issubset(set(header)):
            records: list[tuple[dict[str, str], int]] = []
            for number, row_line in enumerate(lines[index + 2:], start=index + 3):
                row = cells(row_line)
                if not row:
                    break
                if len(row) != len(header):
                    continue
                records.append((dict(zip(header, row)), number))
            return header, records
    return [], []


def parse_routes(path: Path) -> tuple[list[Route], list[str]]:
    required = {"Task", "Executor", "Tier", "Hard gate", "Score", "Confidence", "Reviewer", "Review mode", "Batch", "Locks", "Parallel eligible", "Parallel rationale", "Isolation strategy", "Rationale"}
    header, records = table_records(path, required)
    errors: list[str] = []
    if not header:
        return [], ["routing assignments table missing required headers"]
    routes: list[Route] = []
    for row, line in records:
        task_id = row["Task"]
        if not ID_RE.match(task_id):
            continue
        try:
            score = int(row["Score"])
        except ValueError:
            score = None
        locks = {v.strip().strip("`") for v in re.split(r"[,;]", row["Locks"]) if v.strip() and v.strip().upper() != "NONE"}
        eligible = {"TRUE": True, "FALSE": False}.get(row["Parallel eligible"].upper())
        routes.append(Route(task_id, row["Executor"], row["Tier"].upper(), row["Hard gate"], score, row["Confidence"].upper(), row["Reviewer"], row["Review mode"].upper(), row["Batch"], locks, eligible, row["Parallel rationale"], row["Isolation strategy"].upper(), row["Rationale"], line))
    return routes, errors


def parse_scores(path: Path) -> tuple[dict[str, list[int]], list[str]]:
    required = {"Task", "Total", *SCORE_HEADERS}
    header, records = table_records(path, required)
    if not header:
        return {}, ["score table missing or incomplete"]
    scores: dict[str, list[int]] = {}
    errors: list[str] = []
    for row, line in records:
        task_id = row["Task"]
        if not ID_RE.match(task_id):
            continue
        try:
            values = [int(row[name]) for name in SCORE_HEADERS]
            total = int(row["Total"])
        except ValueError:
            errors.append(f"non-numeric score at routing:{line}: {task_id}")
            continue
        if any(value < 0 or value > 3 for value in values):
            errors.append(f"score dimension outside 0-3: {task_id}")
        if sum(values) != total:
            errors.append(f"score total mismatch {task_id}: declared={total} calculated={sum(values)}")
        scores[task_id] = values
    return scores, errors


def parse_models(path: Path) -> tuple[dict[str, str], list[str]]:
    required = {"Model ID", "Real name/version", "Tier", "Tools", "Assessed at"}
    header, records = table_records(path, required)
    if not header:
        return {}, ["model registry table missing required headers"]
    models: dict[str, str] = {}
    errors: list[str] = []
    for row, line in records:
        model_id = row["Model ID"]
        if not MODEL_RE.match(model_id):
            continue
        if model_id in models:
            errors.append(f"duplicate model registration: {model_id}")
        models[model_id] = row["Tier"].upper()
        if not row["Real name/version"] or not row["Tools"] or not re.match(r"^\d{4}-\d{2}-\d{2}(?:T.*)?$", row["Assessed at"]):
            errors.append(f"incomplete or invalid model registration at line {line}: {model_id}")
    return models, errors


def parse_batches(path: Path) -> list[Batch]:
    lines = path.read_text(encoding="utf-8").splitlines()
    result: list[Batch] = []
    current: Batch | None = None
    for number, line in enumerate(lines, start=1):
        match = re.match(r"^###\s+Batch\s+([A-Z][A-Z0-9_.-]*-B\d{2,3})\s*$", line)
        if match:
            current = Batch(match.group(1), line=number)
            result.append(current)
            continue
        if current is None:
            continue
        field_match = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if not field_match:
            continue
        key, value = field_match.group(1).strip().lower(), field_match.group(2).strip().strip("`")
        if key == "executor": current.executor = value
        elif key == "entry dependencies": current.dependencies = csv_ids(value)
        elif key == "tasks": current.tasks = csv_ids(value)
        elif key == "locks": current.locks = {v.strip().strip("`") for v in re.split(r"[,;]", value) if v.strip() and v.strip().upper() != "NONE"}
        elif key == "execution": current.execution = value.upper()
        elif key == "isolation and merge strategy": current.isolation_strategy = value.upper()
        elif key == "validation command": current.validation = value
    return result


def task_locks(task: Task, route: Route) -> set[str]:
    """Normalize declared task scope into locks before comparing parallel work."""
    return route.locks | {f"file:{path}" for path in task.files} | {f"component:{name}" for name in task.components}


def uses_global_state(value: str | None) -> bool:
    return value is None or value.upper() not in {"", "NONE", "N/A", "NOT_APPLICABLE"}


def validate_parallel_eligibility(tasks: dict[str, Task], routes: dict[str, Route], batches: list[Batch]) -> list[str]:
    errors: list[str] = []
    eligible = [task_id for task_id, route in routes.items() if route.parallel_eligible is True and task_id in tasks]
    for task_id, route in routes.items():
        task = tasks.get(task_id)
        if route.parallel_eligible is None:
            errors.append(f"invalid parallel eligibility value: {task_id}")
            continue
        if not route.parallel_rationale or PLACEHOLDER_RE.search(route.parallel_rationale):
            errors.append(f"missing/placeholder parallel rationale: {task_id}")
        if route.parallel_eligible is False:
            continue
        if route.isolation_strategy != "ISOLATED_WORKTREE_SEQUENTIAL_MERGE_REVIEW":
            errors.append(f"parallel task missing isolation/merge strategy: {task_id}")
        if task is None:
            continue
        unresolved = [dep for dep in task.dependencies if dep not in tasks or tasks[dep].state != "COMPLETE"]
        if unresolved:
            errors.append(f"parallel task has unresolved dependencies {task_id}: {', '.join(sorted(unresolved))}")
        if uses_global_state(task.global_state):
            errors.append(f"parallel task changes global state: {task_id}")
        if uses_global_state(task.migration):
            errors.append(f"parallel task includes migration: {task_id}")
    for index, left_id in enumerate(eligible):
        for right_id in eligible[index + 1:]:
            conflict = task_locks(tasks[left_id], routes[left_id]) & task_locks(tasks[right_id], routes[right_id])
            if conflict:
                errors.append(f"parallel task lock conflict {left_id}/{right_id}: {', '.join(sorted(conflict))}")
    for batch in batches:
        if batch.execution != "PARALLEL":
            continue
        if batch.isolation_strategy != "ISOLATED_WORKTREE_SEQUENTIAL_MERGE_REVIEW":
            errors.append(f"parallel batch missing isolation/merge strategy: {batch.batch_id}")
        for task_id in batch.tasks:
            if task_id in routes and routes[task_id].parallel_eligible is not True:
                errors.append(f"parallel batch task is not eligible: {batch.batch_id}/{task_id}")
    return errors


def dependency_cycle(tasks: dict[str, Task]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    trail: list[str] = []
    def visit(node: str) -> list[str] | None:
        if node in visiting:
            return trail[trail.index(node):] + [node]
        if node in visited:
            return None
        visiting.add(node); trail.append(node)
        for dep in tasks[node].dependencies:
            if dep in tasks:
                found = visit(dep)
                if found: return found
        trail.pop(); visiting.remove(node); visited.add(node)
        return None
    for task_id in tasks:
        found = visit(task_id)
        if found: return found
    return None


def report(errors: list[str], task_count: int, route_count: int) -> int:
    print("workflow_contract=skill-team/v3")
    print(f"tasks={task_count} routed={route_count}")
    for error in errors: print(f"error: {error}")
    print("ROUTING VALID" if not errors else "ROUTING INVALID")
    return 1 if errors else 0


def validate_workflow(root: Path) -> int:
    progress = root / "PROGRESS.md"
    routing = root / "routing" / "ROUTING.md"
    models_path = root / "routing" / "MODEL-CAPABILITIES.md"
    handoff = root / "handoffs" / "ROUTING-TO-IMPLEMENTATION.md"
    tasks_root = root / "plan"
    errors: list[str] = []
    for path in (progress, routing, models_path, handoff, tasks_root):
        if not path.exists(): errors.append(f"required path missing: {path.relative_to(root) if path.is_absolute() or root in path.parents else path}")
    if errors: return report(errors, 0, 0)

    pf, rf, hf, mf = frontmatter(progress), frontmatter(routing), frontmatter(handoff), frontmatter(models_path)
    errors.extend(validate_shared_progress(pf))
    errors.extend(validate_shared_handoff(hf, handoff.read_text(encoding="utf-8").split("---", 2)[-1]))
    for name, data in (("PROGRESS.md", pf), ("ROUTING.md", rf), ("handoff", hf), ("MODEL-CAPABILITIES.md", mf)):
        if data.get("workflow_contract") != "skill-team/v3":
            errors.append(f"{name}: invalid workflow_contract")
    plan_rev = pf.get("plan_revision")
    routing_rev = pf.get("routing_revision")
    for name, data in (("routing", rf), ("handoff", hf)):
        if data.get("plan_revision") and data.get("plan_revision") != plan_rev:
            errors.append(f"{name}: plan revision mismatch")
        if data.get("routing_revision") and data.get("routing_revision") != routing_rev:
            errors.append(f"{name}: routing revision mismatch")
        if data.get("routing_based_on_plan_revision") and data.get("routing_based_on_plan_revision") != plan_rev:
            errors.append(f"{name}: routing_based_on_plan_revision mismatch")
    required_skill = pf.get("required_skill")
    stage_owner = pf.get("stage_owner")
    expected = {
        "stage": pf.get("stage") == "ROUTING",
        "status": pf.get("status") == "IMPLEMENTATION_READY",
        "owner": stage_owner == "route-ai-work-by-capability",
        "required": required_skill == "execute-routed-task",
        "handoff": pf.get("handoff_status") == "READY",
    }
    if not expected["stage"]:
        errors.append(f"PROGRESS.md: unexpected stage={pf.get('stage')!r}")
    if not expected["status"]:
        errors.append(f"PROGRESS.md: expected status=IMPLEMENTATION_READY, got {pf.get('status')!r}")
    if not expected["owner"]:
        errors.append(f"PROGRESS.md: expected stage_owner=route-ai-work-by-capability, got {stage_owner!r}")
    if not expected["required"]:
        errors.append(f"PROGRESS.md: expected required_skill=execute-routed-task, got {required_skill!r}")
    if not expected["handoff"]:
        errors.append(f"PROGRESS.md: expected handoff_status=READY, got {pf.get('handoff_status')!r}")
    active_artifact = pf.get("active_artifact", "").replace("\\", "/")
    if not active_artifact.endswith("handoffs/ROUTING-TO-IMPLEMENTATION.md"):
        errors.append("PROGRESS.md: active_artifact must point to ROUTING-TO-IMPLEMENTATION.md")
    if hf.get("handoff_status") != "READY": errors.append("implementation handoff is not READY")
    handoff_text = handoff.read_text(encoding="utf-8")
    for heading in ("## Registered models", "## Initial execution", "## Gate status", "## Required reading", "## Validation commands", "## Escalation", "## Start protocol", "## Continue protocol", "## Scope-change protocol"):
        if heading not in handoff_text: errors.append(f"handoff missing section: {heading}")

    tasks = parse_tasks(tasks_root)
    routes, route_errors = parse_routes(routing)
    scores, score_errors = parse_scores(routing)
    models, model_errors = parse_models(models_path)
    batches = parse_batches(routing)
    errors.extend(route_errors + score_errors + model_errors)
    task_counts, route_counts = Counter(t.task_id for t in tasks), Counter(r.task_id for r in routes)
    task_map, route_map = {t.task_id: t for t in tasks}, {r.task_id: r for r in routes}
    for task_id, count in task_counts.items():
        if count != 1: errors.append(f"task heading occurs {count} times: {task_id}")
    for task_id, count in route_counts.items():
        if count != 1: errors.append(f"routing entry occurs {count} times: {task_id}")
    for task_id in sorted(task_map.keys() - route_map.keys()): errors.append(f"task missing from routing: {task_id}")
    for task_id in sorted(route_map.keys() - task_map.keys()): errors.append(f"routing contains unknown task: {task_id}")

    for task_id, route in route_map.items():
        if route.executor not in models: errors.append(f"unregistered executor {task_id}: {route.executor}")
        elif models[route.executor] != route.tier: errors.append(f"tier mismatch {task_id}: route={route.tier} registry={models[route.executor]}")
        if route.hard_gate.upper() not in HARD_GATE_NONE and route.tier != "STRONG": errors.append(f"hard gate must route STRONG: {task_id}")
        if task_id not in scores: errors.append(f"missing complete score: {task_id}")
        elif route.score != sum(scores[task_id]): errors.append(f"assignment/score table mismatch: {task_id}")
        if route.score is None or not 0 <= route.score <= 24: errors.append(f"invalid score: {task_id}")
        elif route.hard_gate.upper() in HARD_GATE_NONE and route.score >= 12 and route.tier != "STRONG": errors.append(f"score requires STRONG executor: {task_id}")
        elif route.hard_gate.upper() in HARD_GATE_NONE and 7 <= route.score <= 11 and route.tier == "ECONOMY" and route.review_mode == "NONE": errors.append(f"mid-band ECONOMY task requires review: {task_id}")
        if route.confidence not in {"HIGH", "MEDIUM"}: errors.append(f"unroutable confidence for {task_id}: {route.confidence}")
        if route.review_mode not in REVIEW_MODES: errors.append(f"invalid review mode {task_id}: {route.review_mode}")
        if route.review_mode in REQUIRED_REVIEW:
            if route.reviewer in {"", "NONE"}: errors.append(f"reviewer required: {task_id}")
            elif route.reviewer == route.executor: errors.append(f"executor and reviewer must differ: {task_id}")
            elif route.reviewer not in models: errors.append(f"unregistered reviewer {task_id}: {route.reviewer}")
            elif models[route.reviewer] != "STRONG" and route.review_mode == "ADVERSARIAL_REVIEW": errors.append(f"adversarial review requires STRONG reviewer: {task_id}")
        elif route.reviewer not in {"", "NONE"} and route.reviewer not in models: errors.append(f"unregistered reviewer {task_id}: {route.reviewer}")
        if not route.rationale or PLACEHOLDER_RE.search(route.rationale): errors.append(f"missing/placeholder rationale: {task_id}")
        task = task_map.get(task_id)
        if task and task.executor != route.executor: errors.append(f"owner mismatch {task_id}: task={task.executor!r} routing={route.executor}")
        if task and task.reviewer and task.reviewer != route.reviewer: errors.append(f"reviewer mismatch {task_id}: task={task.reviewer} routing={route.reviewer}")

    for task in tasks:
        for dep in task.dependencies:
            if dep == task.task_id: errors.append(f"self dependency: {task.task_id}")
            elif dep not in task_map: errors.append(f"unknown dependency {task.task_id} -> {dep}")
    cycle = dependency_cycle(task_map)
    if cycle: errors.append("dependency cycle: " + " -> ".join(cycle))

    batch_counts = Counter(task_id for batch in batches for task_id in batch.tasks)
    batch_map = {batch.batch_id: batch for batch in batches}
    for task_id in task_map:
        if batch_counts[task_id] != 1: errors.append(f"task must appear in exactly one batch: {task_id} count={batch_counts[task_id]}")
    for route in routes:
        if route.batch not in batch_map: errors.append(f"unknown batch for {route.task_id}: {route.batch}")
        elif route.task_id not in batch_map[route.batch].tasks: errors.append(f"batch membership mismatch: {route.task_id}")
    for batch in batches:
        if batch.executor not in models: errors.append(f"unregistered batch executor: {batch.batch_id} -> {batch.executor}")
        if batch.execution not in {"SEQUENTIAL", "PARALLEL"}: errors.append(f"invalid batch execution mode: {batch.batch_id}")
        if not batch.validation or PLACEHOLDER_RE.search(batch.validation): errors.append(f"missing batch validation command: {batch.batch_id}")
        for dep in batch.dependencies:
            if dep not in task_map: errors.append(f"unknown batch entry dependency {batch.batch_id} -> {dep}")
        for task_id in batch.tasks:
            if task_id in route_map and route_map[task_id].executor != batch.executor: errors.append(f"batch executor mismatch: {batch.batch_id}/{task_id}")
            if task_id in route_map and not route_map[task_id].locks.issubset(batch.locks):
                errors.append(f"batch/task lock mismatch: {batch.batch_id}/{task_id}")
            if task_id in task_map:
                for dependency in task_map[task_id].dependencies:
                    if dependency not in batch.tasks and dependency not in batch.dependencies:
                        errors.append(f"batch entry dependency missing: {batch.batch_id}/{task_id} -> {dependency}")
                    if batch.execution == "PARALLEL" and dependency in batch.tasks:
                        errors.append(f"parallel batch has internal dependency: {batch.batch_id}/{task_id} -> {dependency}")
    parallel = [batch for batch in batches if batch.execution == "PARALLEL"]
    for i, left in enumerate(parallel):
        for right in parallel[i + 1:]:
            conflict = left.locks & right.locks
            if conflict: errors.append(f"parallel batch lock conflict {left.batch_id}/{right.batch_id}: {', '.join(sorted(conflict))}")
    errors.extend(validate_parallel_eligibility(task_map, route_map, batches))

    for path in (routing, models_path, handoff):
        content = path.read_text(encoding="utf-8")
        matches = [m.group(0) for m in PLACEHOLDER_RE.finditer(content)]
        if matches: errors.append(f"placeholders remain in {path.relative_to(root)}: {', '.join(sorted(set(matches))[:5])}")
    return report(errors, len(tasks), len(routes))


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: workflow root not found: {root}", file=sys.stderr)
        return 2
    return validate_workflow(root)


if __name__ == "__main__":
    raise SystemExit(main())
