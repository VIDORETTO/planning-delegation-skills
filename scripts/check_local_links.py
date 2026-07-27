#!/usr/bin/env python3
"""Check relative Markdown links under the repository."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
SCAN_ROOTS = ("skills", "contracts", "adapters", "catalog", "docs")
ROOT_FILES = ("README.md", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md")


def iter_markdown(repo: Path):
    for name in ROOT_FILES:
        path = repo / name
        if path.is_file():
            yield path
    for root_name in SCAN_ROOTS:
        root = repo / root_name
        if root.is_dir():
            yield from root.rglob("*.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", "--repo-root", dest="repo", type=Path, default=REPO)
    args = parser.parse_args()
    errors: list[str] = []
    for path in iter_markdown(args.repo):
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip().strip("<>").split()[0]
            target = unquote(target.split("#", 1)[0])
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(args.repo)} -> {target}")
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- broken link: {error}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
