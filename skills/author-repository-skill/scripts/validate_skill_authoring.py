#!/usr/bin/env python3
"""Validate author-repository-skill structural expectations for a target skill folder."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    args = parser.parse_args()
    root = args.skill_dir
    errors: list[str] = []
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        errors.append("missing SKILL.md")
    else:
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---") or "name:" not in text.split("---", 2)[1]:
            errors.append("SKILL.md must declare name and description")
    if not (root / "agents" / "openai.yaml").is_file():
        errors.append("missing agents/openai.yaml")
    if (root / "README.md").exists():
        errors.append("skill-local README.md is forbidden")
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
