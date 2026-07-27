#!/usr/bin/env python3
"""Validate the standard anatomy of a skill in this repository (stdlib only).

Usage:
    python validate_skill.py skills/<skill-name> [skills/<other-skill> ...]
    python validate_skill.py --all

Note: unlike the pipeline validators, this script does not accept a
docs/ai/<project-slug> path — author-repository-skill operates on the skills/
catalog itself, which has no product workflow root.

Exit code 0 on PASS, non-zero on FAIL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = REPO_ROOT / "skills"
KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FORBIDDEN_FIELD_RE = re.compile(r"(?m)^next_skill\s*:")
BRAND_RE = re.compile(r"\b(Claude|ChatGPT|Anthropic|OpenAI|GPT-\d)\b")
ALLOWED_FRONTMATTER_KEYS = {"name", "description"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def scalar(value: str) -> Any:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    """Parse flat YAML frontmatter, including '>' / '|' block scalars, without a YAML dependency."""
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", text, re.DOTALL)
    if not match:
        return {}, text, []
    data: dict[str, Any] = {}
    order: list[str] = []
    block_key: str | None = None
    block_lines: list[str] = []
    block_folded = True

    def flush() -> None:
        nonlocal block_key, block_lines
        if block_key is not None:
            joiner = " " if block_folded else "\n"
            data[block_key] = joiner.join(line.strip() for line in block_lines).strip()
            block_key = None
            block_lines = []

    for raw in match.group(1).splitlines():
        if block_key is not None and (raw.startswith((" ", "\t")) or not raw.strip()):
            block_lines.append(raw)
            continue
        flush()
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if not item:
            continue
        key, value = item.groups()
        order.append(key)
        if value in (">", "|", ">-", "|-"):
            block_key = key
            block_lines = []
            block_folded = value.startswith(">")
        else:
            data[key] = scalar(value) if value else ""
    flush()
    return data, text[match.end():], order


def validate_links(text: str, path: Path, report: Report) -> None:
    for raw in LINK_RE.findall(text):
        target = raw.strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if "<" in target or ">" in target:
            continue  # illustrative placeholder path inside a template, not a real link
        if not (path.parent / target).resolve().exists():
            report.error(f"broken local link '{raw}': {path}")


def validate_no_next_skill(text: str, path: Path, report: Report) -> None:
    if FORBIDDEN_FIELD_RE.search(text):
        report.error(f"'next_skill' used as a literal field key (forbidden in skill-team/v3 artifacts): {path}")


def validate_no_brand_hardcode(text: str, path: Path, report: Report) -> None:
    matches = sorted(set(BRAND_RE.findall(text)))
    if matches:
        report.warn(f"hardcoded assistant brand name(s) {matches} found; keep method text vendor-neutral: {path}")


def validate_skill(skill_dir: Path) -> Report:
    report = Report()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        report.error(f"missing SKILL.md: {skill_dir}")
        return report

    text = skill_md.read_text(encoding="utf-8")
    data, body, order = parse_frontmatter(text)
    if not order:
        report.error(f"SKILL.md has no YAML frontmatter: {skill_md}")
    extra_keys = set(order) - ALLOWED_FRONTMATTER_KEYS
    if extra_keys:
        report.error(f"SKILL.md frontmatter must contain only name+description, found extra keys {sorted(extra_keys)}: {skill_md}")
    missing_keys = ALLOWED_FRONTMATTER_KEYS - set(order)
    if missing_keys:
        report.error(f"SKILL.md frontmatter missing keys {sorted(missing_keys)}: {skill_md}")

    name = data.get("name", "")
    if name and not KEBAB_RE.match(name):
        report.error(f"skill 'name' must be kebab-case: '{name}'")
    if name and name != skill_dir.name:
        report.error(f"skill 'name' ('{name}') does not match directory ('{skill_dir.name}')")
    description = data.get("description", "")
    if not description or len(description.strip()) < 20:
        report.error(f"SKILL.md 'description' is missing or too short to serve as a trigger: {skill_md}")

    body_lines = [line for line in body.splitlines() if line.strip()]
    line_count = len(body.splitlines())
    if line_count > 500:
        report.error(f"SKILL.md body exceeds the 500-line maximum ({line_count} lines): {skill_md}")
    elif line_count > 220:
        report.warn(f"SKILL.md body is {line_count} lines; 100-220 is preferred: {skill_md}")
    if not body_lines:
        report.error(f"SKILL.md body is empty: {skill_md}")

    validate_links(body, skill_md, report)
    validate_no_next_skill(text, skill_md, report)
    validate_no_brand_hardcode(body, skill_md, report)

    agents_yaml = skill_dir / "agents" / "openai.yaml"
    if not agents_yaml.is_file():
        report.error(f"missing agents/openai.yaml: {skill_dir}")
    else:
        agents_text = agents_yaml.read_text(encoding="utf-8")
        for key in ("display_name", "short_description", "default_prompt"):
            if f"{key}:" not in agents_text:
                report.error(f"agents/openai.yaml missing '{key}': {agents_yaml}")

    for subdir_name in ("references", "assets", "templates", "scripts"):
        subdir = skill_dir / subdir_name
        if not subdir.is_dir():
            continue
        for path in sorted(subdir.rglob("*.md")):
            sub_text = path.read_text(encoding="utf-8")
            validate_links(sub_text, path, report)
            validate_no_next_skill(sub_text, path, report)
            validate_no_brand_hardcode(sub_text, path, report)
            non_ascii_name = any(ord(ch) > 127 for ch in path.stem)
            if non_ascii_name:
                report.warn(f"non-ASCII file name may not be portable: {path}")

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for path in sorted(scripts_dir.glob("validate_*.py")):
            content = path.read_text(encoding="utf-8")
            if "import " not in content:
                continue
            for match in re.finditer(r"(?m)^\s*(?:import|from)\s+([a-zA-Z0-9_.]+)", content):
                module = match.group(1).split(".")[0]
                if module in {"requests", "yaml", "pandas", "numpy", "click"}:
                    report.error(f"validator script imports a third-party package '{module}' (stdlib only): {path}")

    return report


def discover_skills() -> list[Path]:
    if not SKILLS_ROOT.is_dir():
        return []
    return sorted(p for p in SKILLS_ROOT.iterdir() if p.is_dir())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dirs", nargs="*", type=Path, help="one or more skills/<name> directories")
    parser.add_argument("--all", action="store_true", help="validate every skill under skills/")
    args = parser.parse_args(argv)

    targets = discover_skills() if args.all else [p.resolve() for p in args.skill_dirs]
    if not targets:
        print("error: no skill directory given (use --all or pass skills/<name>)", file=sys.stderr)
        return 2

    total_errors = 0
    for skill_dir in targets:
        report = validate_skill(skill_dir)
        print(f"skill={skill_dir.name}")
        for warning in report.warnings:
            print(f"  WARNING: {warning}")
        for error in report.errors:
            print(f"  ERROR: {error}")
        status = "VALID" if not report.errors else f"INVALID ({len(report.errors)} errors)"
        print(f"  {status}")
        total_errors += len(report.errors)

    print(f"skills_checked={len(targets)} total_errors={total_errors}")
    print("SKILL AUDIT VALID" if not total_errors else "SKILL AUDIT INVALID")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
