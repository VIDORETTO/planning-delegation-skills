#!/usr/bin/env python3
"""Detect orphaned skill resource files.

For every skill, every file under references/, assets/, templates/, and
scripts/ must be mentioned (by filename) from at least one of:
  - the skill's own SKILL.md
  - another resource file in the same skill
  - a script anywhere under scripts/ (top-level or the skill's own scripts/)
  - a test anywhere under tests/

A file can be exempted by listing its skill-relative path under
`resource_allowlist` on that skill's catalog/skills.json entry, e.g.:

    {"name": "my-skill", ..., "resource_allowlist": ["assets/DRAFT.template.md"]}

Usage:
    python scripts/detect_orphan_resources.py [--repo-root PATH] [--json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RESOURCE_DIRS = ("references", "assets", "templates", "scripts")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_resource_allowlist(repo_root: Path) -> dict[str, set[str]]:
    catalog_path = repo_root / "catalog" / "skills.json"
    if not catalog_path.is_file():
        return {}
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    result: dict[str, set[str]] = {}
    for entry in catalog.get("skills", []):
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        allowlist = entry.get("resource_allowlist")
        if isinstance(name, str) and isinstance(allowlist, list):
            result[name] = {item for item in allowlist if isinstance(item, str)}
    return result


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def build_corpus(repo_root: Path, skill_dir: Path) -> str:
    parts: list[str] = []

    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        parts.append(read_text_safe(skill_md))

    agents_dir = skill_dir / "agents"
    if agents_dir.is_dir():
        for path in agents_dir.rglob("*"):
            if path.is_file():
                parts.append(read_text_safe(path))

    for dir_name in RESOURCE_DIRS:
        directory = skill_dir / dir_name
        if directory.is_dir():
            for path in directory.rglob("*"):
                if path.is_file():
                    parts.append(read_text_safe(path))

    top_scripts = repo_root / "scripts"
    if top_scripts.is_dir():
        for path in top_scripts.rglob("*.py"):
            parts.append(read_text_safe(path))

    tests_dir = repo_root / "tests"
    if tests_dir.is_dir():
        for path in tests_dir.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".json"}:
                parts.append(read_text_safe(path))

    return "\n".join(parts)


def iter_resource_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for dir_name in RESOURCE_DIRS:
        directory = skill_dir / dir_name
        if directory.is_dir():
            files.extend(sorted(
                p for p in directory.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
            ))
    return files


def is_referenced(resource: Path, skill_dir: Path, corpus: str) -> bool:
    name = resource.name
    rel_posix = resource.relative_to(skill_dir).as_posix()
    if name in corpus:
        return True
    if rel_posix in corpus:
        return True
    # Also accept a match against the filename without its final extension,
    # for prose that references "the ROUTING template" style names loosely
    # tied to a stem shared with another already-matched form is intentionally
    # not accepted here to avoid weakening the check.
    return False


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    skills_dir = repo_root / "skills"

    allowlists = load_resource_allowlist(repo_root)
    errors: list[str] = []
    exempted: list[str] = []
    checked = 0

    if not skills_dir.is_dir():
        print(f"error: skills directory not found: {skills_dir}")
        return 1

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_name = skill_dir.name
        corpus = build_corpus(repo_root, skill_dir)
        allowlist = allowlists.get(skill_name, set())

        for resource in iter_resource_files(skill_dir):
            checked += 1
            rel = resource.relative_to(repo_root)
            skill_rel = resource.relative_to(skill_dir).as_posix()
            if is_referenced(resource, skill_dir, corpus):
                continue
            if skill_rel in allowlist:
                exempted.append(f"{rel} (allowlisted for {skill_name})")
                continue
            errors.append(
                f"orphan resource: {rel} is not referenced from SKILL.md, another resource, "
                f"a script, or a test; add a reference or list '{skill_rel}' under "
                f"resource_allowlist for '{skill_name}' in catalog/skills.json"
            )

    if args.json:
        print(json.dumps({
            "errors": errors,
            "exempted": exempted,
            "files_checked": checked,
            "valid": not errors,
        }, indent=2))
    else:
        for note in exempted:
            print(f"info: exempted {note}")
        for error in errors:
            print(f"error: {error}")
        print(f"resource files checked: {checked}")
        print("ORPHAN RESOURCES VALID" if not errors else "ORPHAN RESOURCES INVALID")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
