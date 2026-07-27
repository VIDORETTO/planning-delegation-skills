#!/usr/bin/env python3
"""Detect overlapping trigger intent between skill descriptions.

Compares the frontmatter `description` of every skill that already has a
SKILL.md, extracts intent keywords, and flags any pair whose keyword overlap
exceeds a threshold. Pairs listed in catalog/overlap-allowlist.json are
reported as known/intentional coexistence (e.g. the three discovery modes)
and never fail the check. Only unclassified overlaps fail.

Usage:
    python scripts/detect_trigger_overlap.py [--repo-root PATH] [--threshold 0.35] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress_contract import parse_frontmatter  # noqa: E402

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "while",
    "use", "used", "using", "only", "not", "do", "does", "this", "that", "these",
    "those", "for", "to", "of", "in", "on", "with", "without", "before", "after",
    "into", "from", "by", "at", "as", "is", "are", "be", "been", "being", "it",
    "its", "their", "them", "they", "you", "your", "must", "may", "should",
    "resume", "trigger", "skill", "workflow", "stage", "produce", "produces",
    "including", "instead", "than", "other", "own", "no", "never", "always",
    "any", "some", "each", "per", "such", "so", "also", "already", "still",
    "just", "will", "can", "cannot", "about", "over", "under", "between",
    "make", "made", "help", "needs", "need", "user", "agent", "codex",
}
WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z-]{2,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--threshold", type=float, default=0.35, help="Jaccard overlap ratio that triggers a flag")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def keywords(description: str) -> set[str]:
    words = {w.lower() for w in WORD_RE.findall(description)}
    return {w for w in words if w not in STOPWORDS}


def load_descriptions(repo_root: Path) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        return result
    for folder in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_md = folder / "SKILL.md"
        if not skill_md.is_file():
            continue
        frontmatter = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        description = frontmatter.data.get("description", "")
        if not description:
            continue
        result[folder.name] = keywords(description)
    return result


def load_allowlist(repo_root: Path) -> tuple[set[frozenset[str]], list[str]]:
    errors: list[str] = []
    pairs: set[frozenset[str]] = set()
    path = repo_root / "catalog" / "overlap-allowlist.json"
    if not path.is_file():
        return pairs, errors
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
        return pairs, errors
    for entry in data.get("allowed_overlaps", []):
        skills = entry.get("skills") if isinstance(entry, dict) else None
        if isinstance(skills, list) and len(skills) == 2:
            pairs.add(frozenset(skills))
        else:
            errors.append(f"{path}: malformed allowed_overlaps entry: {entry!r}")
    return pairs, errors


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()

    descriptions = load_descriptions(repo_root)
    allowlist, allowlist_errors = load_allowlist(repo_root)

    errors: list[str] = list(allowlist_errors)
    known_overlaps: list[str] = []
    unclassified: list[str] = []

    for left_name, right_name in combinations(sorted(descriptions), 2):
        ratio = jaccard(descriptions[left_name], descriptions[right_name])
        if ratio < args.threshold:
            continue
        pair_key = frozenset((left_name, right_name))
        shared = sorted(descriptions[left_name] & descriptions[right_name])
        message = f"{left_name} <-> {right_name}: overlap={ratio:.2f} shared={shared}"
        if pair_key in allowlist:
            known_overlaps.append(f"allowlisted: {message}")
        else:
            unclassified.append(f"unclassified overlap: {message}")

    errors.extend(unclassified)

    if args.json:
        print(json.dumps({
            "errors": errors,
            "known_overlaps": known_overlaps,
            "skills_compared": sorted(descriptions),
            "threshold": args.threshold,
            "valid": not errors,
        }, indent=2))
    else:
        for note in known_overlaps:
            print(f"info: {note}")
        for error in errors:
            print(f"error: {error}")
        print(f"skills compared: {len(descriptions)} (threshold={args.threshold})")
        print("TRIGGER OVERLAP VALID" if not errors else "TRIGGER OVERLAP INVALID")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
