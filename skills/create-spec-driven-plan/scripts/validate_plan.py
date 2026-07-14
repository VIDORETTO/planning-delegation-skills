#!/usr/bin/env python3
"""Validate a Markdown spec-driven planning directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote

TASK_RE = re.compile(
    r"^###\s+\[(?P<mark>[ xX~!])\]\s+"
    r"(?P<id>[A-Z][A-Z0-9]*-\d{3})\s+[—-]\s+(?P<title>.+)$"
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
STATE_RE = re.compile(
    r"(?:^|\|\s*)(?:State|Status|Estado):\s*"
    r"(PENDING|PENDENTE|IN_PROGRESS|EM_ANDAMENTO|BLOCKED|BLOQUEADA|"
    r"COMPLETE|COMPLETED|CONCLUIDA|CANCELLED|CANCELED|CANCELADA)"
    r"\s*(?=\||$)",
    re.IGNORECASE,
)
EXECUTOR_RE = re.compile(
    r"(?:^|\|\s*)(?:Executor|Owner):\s*([^|]+?)(?=\s*\||$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Task:
    task_id: str
    title: str
    file: str
    line: int
    state: str | None
    executor: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("planning_dir", type=Path)
    parser.add_argument(
        "--require-executor",
        action="store_true",
        help="Fail when a task has no Executor/Owner field.",
    )
    parser.add_argument(
        "--require-core",
        action="store_true",
        help="Require master, progress, roadmap and traceability files.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def find_tasks(markdown_files: list[Path], root: Path) -> list[Task]:
    tasks: list[Task] = []
    for path in markdown_files:
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            match = TASK_RE.match(line)
            if not match:
                continue
            state: str | None = None
            executor: str | None = None
            for candidate in lines[index + 1 : index + 13]:
                if TASK_RE.match(candidate):
                    break
                state_match = STATE_RE.search(candidate)
                executor_match = EXECUTOR_RE.search(candidate)
                if state is None and state_match:
                    state = state_match.group(1).upper()
                if executor is None and executor_match:
                    executor = executor_match.group(1).strip()
                if state is not None and executor is not None:
                    break
            tasks.append(
                Task(
                    task_id=match.group("id"),
                    title=match.group("title").strip(),
                    file=path.relative_to(root).as_posix(),
                    line=index + 1,
                    state=state,
                    executor=executor,
                )
            )
    return tasks


def normalize_local_target(raw_target: str) -> str | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target = unquote(target.split("#", 1)[0])
    return target or None


def validate_links(markdown_files: list[Path], root: Path) -> list[str]:
    errors: list[str] = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = normalize_local_target(match.group(1))
            if target is None:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(
                    f"broken local link: {path.relative_to(root)} -> {target}"
                )
    return errors


def find_core_file(root: Path, names: tuple[str, ...]) -> bool:
    lower_names = {name.lower() for name in names}
    return any(
        path.is_file() and path.name.lower() in lower_names
        for path in root.rglob("*.md")
    )


def main() -> int:
    args = parse_args()
    root = args.planning_dir.resolve()
    if not root.is_dir():
        print(f"error: planning directory not found: {root}", file=sys.stderr)
        return 2

    markdown_files = sorted(root.rglob("*.md"))
    tasks = find_tasks(markdown_files, root)
    errors = validate_links(markdown_files, root)
    warnings: list[str] = []

    counts = Counter(task.task_id for task in tasks)
    for task_id, count in sorted(counts.items()):
        if count != 1:
            errors.append(f"task ID occurs {count} times: {task_id}")

    for task in tasks:
        location = f"{task.file}:{task.line}"
        if task.state is None:
            errors.append(f"task has no valid state near heading: {location}")
        if args.require_executor and task.executor is None:
            errors.append(f"task has no executor near heading: {location}")

    if not tasks:
        warnings.append("no task headings were found")

    if args.require_core:
        required = {
            "master": ("00-master.md", "master.md"),
            "progress": ("progress.md", "progresso.md"),
            "roadmap": ("roadmap.md", "07-roadmap.md"),
            "traceability": ("traceability.md", "08-rastreabilidade.md"),
        }
        for label, names in required.items():
            if not find_core_file(root, names):
                errors.append(f"missing core document: {label}")

    executor_counts = Counter(
        task.executor for task in tasks if task.executor is not None
    )
    report = {
        "planning_dir": str(root),
        "markdown_files": len(markdown_files),
        "tasks": len(tasks),
        "unique_task_ids": len(counts),
        "executors": dict(sorted(executor_counts.items())),
        "errors": errors,
        "warnings": warnings,
        "task_records": [asdict(task) for task in tasks] if args.as_json else None,
    }

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"planning_dir={root}")
        print(f"markdown_files={len(markdown_files)}")
        print(f"tasks={len(tasks)} unique={len(counts)}")
        if executor_counts:
            summary = " ".join(
                f"{name}={count}" for name, count in sorted(executor_counts.items())
            )
            print(f"executors: {summary}")
        for warning in warnings:
            print(f"warning: {warning}")
        for error in errors:
            print(f"error: {error}")
        print("VALID" if not errors else "INVALID")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
