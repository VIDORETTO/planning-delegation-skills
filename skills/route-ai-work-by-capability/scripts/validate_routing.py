#!/usr/bin/env python3
"""Validate that plan tasks and model routing have one matching owner."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

TASK_RE = re.compile(
    r"^###\s+\[[ xX~!]\]\s+"
    r"(?P<id>[A-Z][A-Z0-9]*-\d{3})\s+[—-]\s+(?P<title>.+)$"
)
EXECUTOR_RE = re.compile(
    r"(?:^|\|\s*)(?:Executor|Owner):\s*([^|]+?)(?=\s*\||$)",
    re.IGNORECASE,
)
QUEUE_HEADER_RE = re.compile(
    r"^#{2,6}\s+.*(?:Fila|Queue)\s+"
    r"(?P<tier>[A-Z][A-Z0-9_.-]+)(?:\s|$)",
    re.IGNORECASE,
)
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d{3}$")


@dataclass(frozen=True)
class TaskOwner:
    task_id: str
    executor: str | None
    file: str
    line: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks_directory", type=Path)
    parser.add_argument("routing_document", type=Path)
    parser.add_argument(
        "--tiers",
        help="Comma-separated allowed executor names; inferred when omitted.",
    )
    return parser.parse_args()


def parse_tasks(root: Path) -> list[TaskOwner]:
    records: list[TaskOwner] = []
    for path in sorted(root.rglob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            match = TASK_RE.match(line)
            if not match:
                continue
            executor: str | None = None
            for candidate in lines[index + 1 : index + 13]:
                if TASK_RE.match(candidate):
                    break
                owner_match = EXECUTOR_RE.search(candidate)
                if owner_match:
                    executor = owner_match.group(1).strip()
                    break
            records.append(
                TaskOwner(
                    task_id=match.group("id"),
                    executor=executor,
                    file=path.relative_to(root).as_posix(),
                    line=index + 1,
                )
            )
    return records


def parse_table_cells(line: str) -> list[str]:
    if not line.lstrip().startswith("|"):
        return []
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_routes(path: Path, allowed: set[str] | None) -> list[tuple[str, str, int]]:
    routes: list[tuple[str, str, int]] = []
    active_queue: str | None = None
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        header = QUEUE_HEADER_RE.match(line)
        if header:
            candidate = header.group("tier")
            active_queue = candidate if allowed is None or candidate in allowed else None
            continue

        cells = parse_table_cells(line)
        if not cells or not ID_RE.match(cells[0]):
            continue

        executor: str | None = None
        if len(cells) >= 2 and (allowed is None or cells[1] in allowed):
            if cells[1] not in {"ID", "Task", "Tarefa", "Executor", "Owner"}:
                executor = cells[1]

        if executor is None:
            executor = active_queue

        if executor is not None:
            routes.append((cells[0], executor, number))

    return routes


def main() -> int:
    args = parse_args()
    tasks_root = args.tasks_directory.resolve()
    routing_path = args.routing_document.resolve()
    if not tasks_root.is_dir():
        print(f"error: tasks directory not found: {tasks_root}", file=sys.stderr)
        return 2
    if not routing_path.is_file():
        print(f"error: routing document not found: {routing_path}", file=sys.stderr)
        return 2

    allowed = (
        {item.strip() for item in args.tiers.split(",") if item.strip()}
        if args.tiers
        else None
    )
    task_records = parse_tasks(tasks_root)
    route_records = parse_routes(routing_path, allowed)
    errors: list[str] = []

    task_counts = Counter(record.task_id for record in task_records)
    route_counts = Counter(task_id for task_id, _, _ in route_records)
    task_map = {record.task_id: record for record in task_records}
    route_map = {task_id: executor for task_id, executor, _ in route_records}

    for task_id, count in sorted(task_counts.items()):
        if count != 1:
            errors.append(f"task heading occurs {count} times: {task_id}")
    for task_id, count in sorted(route_counts.items()):
        if count != 1:
            errors.append(f"routing entry occurs {count} times: {task_id}")

    for task_id in sorted(task_map.keys() - route_map.keys()):
        errors.append(f"task missing from routing: {task_id}")
    for task_id in sorted(route_map.keys() - task_map.keys()):
        errors.append(f"routing contains unknown task: {task_id}")

    for task_id in sorted(task_map.keys() & route_map.keys()):
        record = task_map[task_id]
        routed = route_map[task_id]
        if record.executor is None:
            errors.append(
                f"task has no embedded Executor: {task_id} "
                f"({record.file}:{record.line})"
            )
        elif record.executor != routed:
            errors.append(
                f"owner mismatch {task_id}: task={record.executor} routing={routed}"
            )
        if allowed is not None and routed not in allowed:
            errors.append(f"executor outside allowed tiers: {task_id} -> {routed}")

    owner_counts = Counter(route_map.values())
    print(f"tasks={len(task_records)} routed={len(route_records)}")
    print(
        "owners: "
        + " ".join(
            f"{executor}={count}"
            for executor, count in sorted(owner_counts.items())
        )
    )
    for error in errors:
        print(f"error: {error}")
    print("VALID" if not errors else "INVALID")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
