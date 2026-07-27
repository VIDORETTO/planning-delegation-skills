#!/usr/bin/env python3
"""Detect references to nonexistent skill names."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KNOWN_FALSE_POSITIVES = {
    "implementation",  # English noun; skill is execute-routed-task
}
BANNED = {"spec-driven-dev", "implementation"}  # as skill invocations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", "--repo-root", dest="repo", type=Path, default=REPO)
    args = parser.parse_args()
    catalog = json.loads((args.repo / "catalog" / "skills.json").read_text(encoding="utf-8"))
    known = {item["name"] for item in catalog["skills"]}
    known |= set(catalog.get("legacy_pending_removal", []))
    errors: list[str] = []
    pattern = re.compile(r"(?i)\b(?:use\s+\$?|skill\s+`|required_skill:\s*|producer_skill:\s*|consumer_skill:\s*)([a-z0-9-]+)")
    for path in (args.repo / "skills").rglob("*.md"):
        if "advisor-planner" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "spec-driven-dev" in text:
            errors.append(f"{path.relative_to(args.repo)}: nonexistent skill spec-driven-dev")
        if re.search(r"(?m)^(?:required_skill|next_skill):\s*implementation\s*$", text):
            errors.append(f"{path.relative_to(args.repo)}: required_skill/next_skill implementation is not a skill")
        for match in pattern.finditer(text):
            name = match.group(1)
            if name in known or name in KNOWN_FALSE_POSITIVES:
                continue
            if name.endswith("-skill") or "-with-" in name or name.startswith(("create-", "route-", "execute-", "review-", "validate-", "author-", "investigate-", "brainstorm-", "product-")):
                if name not in known:
                    errors.append(f"{path.relative_to(args.repo)}: unknown skill reference '{name}'")
    if errors:
        print("INVALID")
        for error in sorted(set(errors)):
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
