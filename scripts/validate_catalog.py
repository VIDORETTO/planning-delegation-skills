#!/usr/bin/env python3
"""Validate catalog/skills.json against the skills/ folder tree.

Checks:
  1. catalog/skills.json is well-formed JSON with schema_version == 1.
  2. Every skills/*/SKILL.md folder is registered in the catalog, except
     skills/advisor-planner, which is expected-legacy (absorbed, pending
     removal, deliberately excluded from the active catalog).
  3. Every catalog entry has a matching skills/<name>/ folder.
  4. Catalog names are unique.
  5. When SKILL.md exists, its frontmatter `name` matches both the folder
     name and the catalog entry name.
  6. Each catalog entry has the required fields with sane types/values.
   7. Each entry's `category` exists in catalog/categories.json.
   8. Each entry's produced artifact paths match its canonical v3 contract.

Usage:
    python scripts/validate_catalog.py [--repo-root PATH] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress_contract import parse_frontmatter  # noqa: E402

EXPECTED_LEGACY_SKILLS: set[str] = set()  # advisor-planner removed after absorption
REQUIRED_ENTRY_FIELDS = {
    "name": str,
    "category": str,
    "status": str,
    "workflow_contracts": list,
    "accepts": list,
    "produces": list,
    "standalone": bool,
    "platform_neutral": bool,
}
ALLOWED_STATUSES = {"draft", "stable", "deprecated"}
CANONICAL_PRODUCES = {
    "brainstorm-idea-with-user": {
        "docs/ai/<slug>/discovery/brainstorm/BRAINSTORM.md",
        "docs/ai/<slug>/handoffs/BRAINSTORM-TO-PLAN.md",
    },
    "investigate-existing-codebase": {
        "docs/ai/<slug>/discovery/codebase/INVESTIGATION.md",
        "docs/ai/<slug>/discovery/codebase/EVIDENCE.md",
        "docs/ai/<slug>/handoffs/CODEBASE-TO-PLAN.md",
    },
    "product-ux-audit": {
        "docs/ai/<slug>/discovery/ux/SITEMAP.md",
        "docs/ai/<slug>/discovery/ux/COVERAGE.md",
        "docs/ai/<slug>/discovery/ux/UX-AUDIT.md",
        "docs/ai/<slug>/handoffs/UX-AUDIT-TO-PLAN.md",
    },
    "create-spec-driven-plan": {
        "docs/ai/<slug>/plan/**",
        "docs/ai/<slug>/handoffs/PLAN-TO-ROUTING.md",
    },
    "route-ai-work-by-capability": {
        "docs/ai/<slug>/routing/ROUTING.md",
        "docs/ai/<slug>/routing/MODEL-CAPABILITIES.md",
        "docs/ai/<slug>/handoffs/ROUTING-TO-IMPLEMENTATION.md",
    },
    "execute-routed-task": {
        "docs/ai/<slug>/execution/EVIDENCE.md",
        "docs/ai/<slug>/execution/HISTORY.md",
        "docs/ai/<slug>/blockers/<TASK-ID>.md",
        "docs/ai/<slug>/handoffs/IMPLEMENTATION-TO-REVIEW.md",
        "docs/ai/<slug>/handoffs/IMPLEMENTATION-TO-RELEASE.md",
    },
    "review-implementation-evidence": {
        "docs/ai/<slug>/review/REVIEW-REPORT.md",
        "docs/ai/<slug>/handoffs/REVIEW-TO-RELEASE.md",
        "docs/ai/<slug>/handoffs/REVIEW-TO-IMPLEMENTATION.md",
    },
    "validate-release-readiness": {
        "docs/ai/<slug>/release/RELEASE-READINESS.md",
        "docs/ai/<slug>/PROGRESS.md#release_revision",
    },
    "author-repository-skill": {
        "skills/<name>/SKILL.md",
        "skills/<name>/agents/openai.yaml",
        "catalog/skills.json#entry",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", help="emit a JSON report instead of plain text")
    return parser.parse_args()


def load_json(path: Path, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"missing required file: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
        return {}


def validate(repo_root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []

    catalog_path = repo_root / "catalog" / "skills.json"
    categories_path = repo_root / "catalog" / "categories.json"

    catalog = load_json(catalog_path, errors)
    categories = load_json(categories_path, errors)
    if errors:
        return errors, {"warnings": warnings}

    if catalog.get("schema_version") != 1:
        errors.append(f"catalog/skills.json: expected schema_version 1, got {catalog.get('schema_version')!r}")
    if categories.get("schema_version") != 1:
        errors.append(f"catalog/categories.json: expected schema_version 1, got {categories.get('schema_version')!r}")

    known_categories = set(categories.get("categories", {}).keys())
    entries = catalog.get("skills", [])
    if not isinstance(entries, list):
        errors.append("catalog/skills.json: 'skills' must be a list")
        entries = []

    seen_names: dict[str, int] = {}
    catalog_names: set[str] = set()

    for index, entry in enumerate(entries):
        location = f"catalog/skills.json:skills[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{location}: entry must be an object")
            continue

        name = entry.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"{location}: missing or invalid 'name'")
            continue

        seen_names[name] = seen_names.get(name, 0) + 1
        catalog_names.add(name)

        for field_name, expected_type in REQUIRED_ENTRY_FIELDS.items():
            if field_name not in entry:
                errors.append(f"{location} ({name}): missing field '{field_name}'")
            elif not isinstance(entry[field_name], expected_type):
                errors.append(
                    f"{location} ({name}): field '{field_name}' must be {expected_type.__name__}, "
                    f"got {type(entry[field_name]).__name__}"
                )

        status = entry.get("status")
        if isinstance(status, str) and status not in ALLOWED_STATUSES:
            errors.append(f"{location} ({name}): invalid status {status!r}; expected one of {sorted(ALLOWED_STATUSES)}")

        contracts = entry.get("workflow_contracts")
        if isinstance(contracts, list) and "skill-team/v3" not in contracts:
            errors.append(f"{location} ({name}): workflow_contracts must include 'skill-team/v3'")

        produces = entry.get("produces")
        expected_produces = CANONICAL_PRODUCES.get(name)
        if isinstance(produces, list) and expected_produces is not None:
            actual_produces = set(produces)
            if actual_produces != expected_produces or len(actual_produces) != len(produces):
                errors.append(
                    f"{location} ({name}): produces must match canonical paths; "
                    f"expected {sorted(expected_produces)!r}, got {sorted(actual_produces)!r}"
                )

        category = entry.get("category")
        if isinstance(category, str) and known_categories and category not in known_categories:
            errors.append(f"{location} ({name}): unknown category {category!r}; known: {sorted(known_categories)}")

        folder = repo_root / "skills" / name
        if not folder.is_dir():
            errors.append(f"{location} ({name}): no matching folder skills/{name}/")
            continue

        skill_md = folder / "SKILL.md"
        if skill_md.is_file():
            frontmatter = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            fm_name = frontmatter.data.get("name")
            if fm_name != name:
                errors.append(
                    f"{location}: SKILL.md frontmatter name {fm_name!r} does not match catalog/folder name {name!r}"
                )
        else:
            if status == "stable":
                errors.append(f"{location} ({name}): status is 'stable' but skills/{name}/SKILL.md does not exist")
            else:
                warnings.append(f"{name}: no SKILL.md yet (status={status!r}); folder scaffold only")

    for name, count in seen_names.items():
        if count > 1:
            errors.append(f"catalog/skills.json: duplicate skill name {name!r} appears {count} times")

    skills_dir = repo_root / "skills"
    if skills_dir.is_dir():
        for folder in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            name = folder.name
            skill_md = folder / "SKILL.md"
            if name in catalog_names:
                continue
            if name in EXPECTED_LEGACY_SKILLS:
                if skill_md.is_file():
                    warnings.append(f"{name}: expected-legacy skill, correctly excluded from active catalog")
                continue
            if skill_md.is_file():
                errors.append(f"skills/{name}/SKILL.md exists but is not registered in catalog/skills.json")
            else:
                errors.append(
                    f"skills/{name}/ exists with no SKILL.md and is not registered in catalog/skills.json "
                    "(register it as status: draft)"
                )

    return errors, {"warnings": warnings, "skill_count": len(entries)}


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    errors, meta = validate(repo_root)

    if args.json:
        print(json.dumps({"errors": errors, **meta, "valid": not errors}, indent=2))
    else:
        for warning in meta.get("warnings", []):
            print(f"warning: {warning}")
        for error in errors:
            print(f"error: {error}")
        print(f"skills registered: {meta.get('skill_count', 0)}")
        print("CATALOG VALID" if not errors else "CATALOG INVALID")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
