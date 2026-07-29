#!/usr/bin/env python3
"""Orchestrate every repository-level validator for skill-team/v3.

Steps:
    1.  discover skills (skills/*/)
    2.  parse SKILL.md frontmatter name/description where present
    3.  check name uniqueness and folder/frontmatter-name match
    4.  check agents/openai.yaml presence (informational; adapters are optional)
    5.  check local Markdown links (scripts/check_local_links.py)
    6.  py_compile every repository Python script
    7.  check for nonexistent skill references (scripts/check_skill_references.py)
    8.  check for overlapping skill trigger descriptions (scripts/detect_trigger_overlap.py)
    9.  check for orphaned skill resources (scripts/detect_orphan_resources.py)
    10. validate catalog/skills.json against skills/ (scripts/validate_catalog.py)
    11. run unittest discovery over tests/
    12. print a summary and return a single pass/fail exit code

Usage:
    python scripts/validate_repository.py [--repo-root PATH]

Every sub-check is stdlib-only. Exit code is 0 only if every blocking step
passes; agents/openai.yaml presence never blocks (adapters are optional per
catalog/compatibility.json).
"""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress_contract import parse_frontmatter  # noqa: E402
from workflow_contract import validate_handoff, validate_progress  # noqa: E402

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser.parse_args()


class StepResult:
    def __init__(self, name: str, ok: bool, blocking: bool, details: list[str]):
        self.name = name
        self.ok = ok
        self.blocking = blocking
        self.details = details


def step_discover_and_frontmatter(repo_root: Path) -> StepResult:
    """Steps 1-3: discover skills, parse frontmatter, check uniqueness/match."""

    details: list[str] = []
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        return StepResult("discover skills", False, True, [f"missing directory: {skills_dir}"])

    folders = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    details.append(f"discovered {len(folders)} skill folder(s): {', '.join(p.name for p in folders)}")

    seen_names: dict[str, list[str]] = {}
    for folder in folders:
        skill_md = folder / "SKILL.md"
        if not skill_md.is_file():
            details.append(f"{folder.name}: no SKILL.md (scaffold only)")
            continue
        frontmatter = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if not frontmatter.found:
            details.append(f"error: {folder.name}/SKILL.md: missing frontmatter fence")
            continue
        if not frontmatter.terminated:
            details.append(f"error: {folder.name}/SKILL.md: unterminated frontmatter fence")
            continue
        name = frontmatter.data.get("name")
        description = frontmatter.data.get("description")
        if not name:
            details.append(f"error: {folder.name}/SKILL.md: missing frontmatter 'name'")
            continue
        if not description:
            details.append(f"error: {folder.name}/SKILL.md: missing frontmatter 'description'")
        if name != folder.name:
            details.append(f"error: {folder.name}/SKILL.md: frontmatter name '{name}' != folder name '{folder.name}'")
        seen_names.setdefault(name, []).append(folder.name)

    for name, owners in seen_names.items():
        if len(owners) > 1:
            details.append(f"error: duplicate skill name '{name}' claimed by folders: {', '.join(owners)}")

    ok = not any(line.startswith("error:") for line in details)
    return StepResult("discover skills + frontmatter + uniqueness", ok, True, details)


def step_adapter_presence(repo_root: Path) -> StepResult:
    """Step 4: agents/openai.yaml presence. Informational only (optional adapter)."""

    details: list[str] = []
    skills_dir = repo_root / "skills"
    if skills_dir.is_dir():
        for folder in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            if not (folder / "SKILL.md").is_file():
                continue
            adapter = folder / "agents" / "openai.yaml"
            if not adapter.is_file():
                details.append(f"warning: {folder.name}: no agents/openai.yaml (optional adapter, not required)")
    return StepResult("agents/openai.yaml presence", True, False, details)


def run_subprocess_check(name: str, script: Path, repo_root: Path, blocking: bool = True) -> StepResult:
    if not script.is_file():
        return StepResult(name, False, blocking, [f"missing validator script: {script}"])
    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(repo_root)],
        capture_output=True,
        text=True,
    )
    details = [line for line in (result.stdout + result.stderr).splitlines() if line.strip()]
    return StepResult(name, result.returncode == 0, blocking, details)


def step_py_compile(repo_root: Path) -> StepResult:
    """Step 6: byte-compile every repository .py file to catch syntax errors."""

    details: list[str] = []
    targets: list[Path] = []
    scripts_dir = repo_root / "scripts"
    if scripts_dir.is_dir():
        targets.extend(sorted(scripts_dir.glob("*.py")))
    skills_dir = repo_root / "skills"
    if skills_dir.is_dir():
        targets.extend(sorted(skills_dir.glob("*/scripts/*.py")))
    tests_dir = repo_root / "tests"
    if tests_dir.is_dir():
        targets.extend(sorted(tests_dir.rglob("*.py")))

    ok = True
    for target in targets:
        try:
            py_compile.compile(str(target), doraise=True)
        except py_compile.PyCompileError as exc:
            ok = False
            details.append(f"error: {target.relative_to(repo_root)}: {exc.msg}")
    details.insert(0, f"compiled {len(targets)} file(s)")
    return StepResult("py_compile all scripts", ok, True, details)


def step_contract_schemas(repo_root: Path) -> StepResult:
    """Parse every canonical JSON schema and enforce strict object schemas."""
    contracts = repo_root / "contracts"
    names = ("progress-schema.json", "handoff-schema.json", "task-schema.json", "routing-schema.json")
    details: list[str] = []
    ok = True
    for name in names:
        path = contracts / name
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("type") != "object" or data.get("additionalProperties") is not False:
                raise ValueError("must be a strict object schema")
            details.append(f"validated {name}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            ok = False
            details.append(f"error: {name}: {exc}")
    return StepResult("validate canonical contract schemas", ok, True, details)


def step_canonical_template_instances(repo_root: Path) -> StepResult:
    """Instantiate canonical handoff templates and validate their shared contract."""
    templates = (
        "skills/brainstorm-idea-with-user/assets/BRAINSTORM-TO-PLAN.template.md",
        "skills/investigate-existing-codebase/assets/CODEBASE-TO-PLAN.template.md",
        "skills/product-ux-audit/assets/UX-AUDIT-TO-PLAN.template.md",
        "skills/create-spec-driven-plan/assets/PLAN-TO-ROUTING.template.md",
        "skills/route-ai-work-by-capability/assets/ROUTING-TO-IMPLEMENTATION.template.md",
        "skills/execute-routed-task/assets/IMPLEMENTATION-TO-REVIEW.template.md",
        "skills/execute-routed-task/assets/IMPLEMENTATION-TO-RELEASE.template.md",
        "skills/review-implementation-evidence/assets/REVIEW-TO-IMPLEMENTATION.template.md",
        "skills/review-implementation-evidence/assets/REVIEW-TO-RELEASE.template.md",
    )
    details: list[str] = []
    ok = True
    for relative in templates:
        path = repo_root / relative
        try:
            # Replace template tokens before validation; templates themselves must remain reusable.
            text = re.sub(r"<[^>\n]+>", "example", path.read_text(encoding="utf-8"))
            text = re.sub(r"(?m)^(input_revision|output_revision): example$", r"\1: 1", text)
            text = re.sub(r"(?m)^generated_at: example$", "generated_at: 2026-01-01T00:00:00Z", text)
            frontmatter = parse_frontmatter(text)
            errors = validate_handoff(frontmatter.data, text)
            if not frontmatter.found or not frontmatter.terminated:
                errors.append("frontmatter is missing or unterminated")
            if errors:
                raise ValueError("; ".join(errors))
            details.append(f"validated {relative}")
        except (OSError, ValueError) as exc:
            ok = False
            details.append(f"error: {relative}: {exc}")
    return StepResult("instantiate canonical handoff templates", ok, True, details)


def step_workflow_fixtures(repo_root: Path) -> StepResult:
    """Validate canonical valid fixtures and assert deterministic invalid failures."""
    fixtures = repo_root / "tests" / "fixtures"
    valid = ("greenfield-product", "existing-code-bug", "ux-audit-to-plan", "compact-plan")
    invalid = {
        "two-writers": "STV3-E009-WRITER-LOCK",
        "stale-revision": "STV3-E010-REVISION",
        "legacy-alias": "STV3-E001-CONTRACT",
    }
    details: list[str] = []
    ok = True
    for name in valid:
        path = fixtures / name / "PROGRESS.md"
        data = parse_frontmatter(path.read_text(encoding="utf-8")).data if path.is_file() else {}
        errors = validate_progress(data)
        if errors:
            ok = False
            details.append(f"error: valid fixture {name}: {'; '.join(errors)}")
        else:
            details.append(f"validated valid fixture {name}")
    for name, expected_error in invalid.items():
        path = fixtures / "invalid-workflows" / name / "PROGRESS.md"
        data = parse_frontmatter(path.read_text(encoding="utf-8")).data if path.is_file() else {}
        errors = validate_progress(data)
        if expected_error not in "\n".join(errors):
            ok = False
            details.append(f"error: invalid fixture {name}: expected {expected_error}, got {errors!r}")
        else:
            details.append(f"rejected invalid fixture {name}: {expected_error}")
    placeholder = fixtures / "invalid-workflows" / "placeholder-handoff" / "PLAN-TO-ROUTING.md"
    if not placeholder.is_file():
        ok = False
        details.append("error: invalid fixture placeholder-handoff: missing PLAN-TO-ROUTING.md")
    else:
        text = placeholder.read_text(encoding="utf-8")
        errors = validate_handoff(parse_frontmatter(text).data, text)
        if "<" not in text or not errors:
            ok = False
            details.append("error: invalid fixture placeholder-handoff: expected placeholder contract failure")
        else:
            details.append("rejected invalid fixture placeholder-handoff: STV3-E012-HANDOFF-CONTRACT")
    return StepResult("validate workflow fixtures", ok, True, details)


def step_unittest(repo_root: Path) -> StepResult:
    """Step 11: run unittest discovery over tests/."""

    tests_dir = repo_root / "tests"
    if not tests_dir.is_dir():
        return StepResult("unittest discovery", True, False, ["no tests/ directory found; skipped"])

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(tests_dir), pattern="test_*.py", top_level_dir=str(repo_root))
    stream = sys.stderr
    runner = unittest.TextTestRunner(stream=stream, verbosity=1)
    result = runner.run(suite)
    details = [f"ran {result.testsRun} test(s)"]
    for test, err in result.errors:
        details.append(f"ERROR: {test}: {err.splitlines()[-1] if err else 'unknown error'}")
    for test, err in result.failures:
        details.append(f"FAIL: {test}: {err.splitlines()[-1] if err else 'unknown failure'}")
    ok = result.wasSuccessful()
    return StepResult("unittest discovery (tests/)", ok, True, details)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    scripts_dir = repo_root / "scripts"

    steps: list[StepResult] = []
    steps.append(step_discover_and_frontmatter(repo_root))
    steps.append(step_adapter_presence(repo_root))
    steps.append(run_subprocess_check("check local links", scripts_dir / "check_local_links.py", repo_root))
    steps.append(step_py_compile(repo_root))
    steps.append(step_contract_schemas(repo_root))
    steps.append(step_canonical_template_instances(repo_root))
    steps.append(run_subprocess_check("check skill references", scripts_dir / "check_skill_references.py", repo_root))
    steps.append(run_subprocess_check("detect trigger overlap", scripts_dir / "detect_trigger_overlap.py", repo_root))
    steps.append(run_subprocess_check("detect orphan resources", scripts_dir / "detect_orphan_resources.py", repo_root))
    steps.append(run_subprocess_check("validate catalog", scripts_dir / "validate_catalog.py", repo_root))
    steps.append(step_workflow_fixtures(repo_root))
    steps.append(step_unittest(repo_root))

    print("=" * 72)
    print("skill-team/v3 repository validation")
    print("=" * 72)

    any_blocking_failure = False
    for step in steps:
        status = "PASS" if step.ok else ("FAIL" if step.blocking else "WARN")
        print(f"\n[{status}] {step.name}")
        for line in step.details:
            print(f"    {line}")
        if not step.ok and step.blocking:
            any_blocking_failure = True

    print("\n" + "=" * 72)
    print("REPOSITORY VALID" if not any_blocking_failure else "REPOSITORY INVALID")
    print("=" * 72)

    return 1 if any_blocking_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
