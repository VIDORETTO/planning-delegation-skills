#!/usr/bin/env python3
"""Validate skill-team/v3 brainstorm artifacts without third-party packages."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any

CONTRACT = "skill-team/v3"
LEGACY_CONTRACT = "planning-delegation/v2"
SKILL = "brainstorm-idea-with-user"
NEXT_SKILL = "create-spec-driven-plan"
READY = {"BRAINSTORM_READY", "DISCOVERY_READY"}
IN_PROGRESS = "BRAINSTORM_IN_PROGRESS"
ALLOWED_STATUSES = READY | {IN_PROGRESS, "REBRAINSTORM_REQUIRED", "DISCOVERY_BLOCKED"}
ID_PREFIXES = ("ACT", "DEC", "Q", "ASM", "RISK", "BR", "JRN", "CR", "REJ", "SRC")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})$")

REQUIRED_BRAINSTORM_HEADINGS = (
    "Identificação", "Ideia original", "Resumo atual", "Problema atual",
    "Resultado desejado", "Usuários e atores", "Cenários e jornadas", "Escopo",
    "Capacidades desejadas", "Regras de negócio conhecidas", "Dados",
    "Integrações externas", "Restrições", "Métricas e definição de sucesso",
    "Exemplos concretos", "Glossário inicial", "Decisões", "Suposições",
    "Questões em aberto", "Riscos", "Sugestões recusadas",
    "Prontidão para planejamento",
)
REQUIRED_HANDOFF_HEADINGS = (
    "Identificação", "Resultado consolidado", "Requisitos candidatos confirmados",
    "Decisões obrigatórias", "Decisões delegadas à IA", "Sugestões rejeitadas",
    "Suposições ainda ativas", "Questões menores que podem ser resolvidas no planejamento",
    "Questões estruturais", "Escopo do MVP", "Visão completa", "Fora de escopo",
    "Restrições", "Integrações", "Fontes obrigatórias", "Riscos prioritários",
    "Critérios de sucesso", "Instruções para a próxima skill",
)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)


def scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"null", "~"}:
        return None
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def frontmatter(path: Path, report: Report) -> tuple[dict[str, Any], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.error(f"cannot read {path}: {exc}")
        return {}, ""
    if not text.startswith("---"):
        report.error(f"missing YAML frontmatter: {path}")
        return {}, text
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", text, re.DOTALL)
    if not match:
        report.error(f"unterminated YAML frontmatter: {path}")
        return {}, text
    data: dict[str, Any] = {}
    for lineno, raw in enumerate(match.group(1).splitlines(), 2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if not item:
            report.error(f"unsupported frontmatter syntax {path}:{lineno}: {raw.strip()}")
            continue
        key, value = item.groups()
        data[key] = scalar(value)
    return data, text[match.end():]


def require_keys(data: dict[str, Any], keys: tuple[str, ...], path: Path, report: Report) -> None:
    for key in keys:
        if key not in data:
            report.error(f"missing frontmatter key '{key}': {path}")


def validate_headings(text: str, headings: tuple[str, ...], path: Path, report: Report) -> None:
    found = {m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)}
    for heading in headings:
        if heading not in found:
            report.error(f"missing section '## {heading}': {path}")


def section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$\r?\n(.*?)(?=^##\s+|\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def validate_declared_ids(text: str, path: Path, report: Report) -> None:
    declared: dict[str, int] = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s*(?:\|\s*|###\s+|[-*]\s+)(" + "|".join(ID_PREFIXES) + r"-\d{3,})\b", line)
        if not match:
            continue
        identifier = match.group(1)
        if identifier in declared:
            report.error(f"duplicate declared ID {identifier}: {path}:{declared[identifier]} and {lineno}")
        else:
            declared[identifier] = lineno
    for match in re.finditer(r"\b(?:" + "|".join(ID_PREFIXES) + r")-(\d{1,2})\b", text):
        report.error(f"ID must use at least three digits '{match.group(0)}': {path}")


def validate_links(text: str, path: Path, report: Report) -> None:
    for raw in LINK_RE.findall(text):
        target = raw.strip().strip("<>").split("#", 1)[0]
        if not target:
            continue
        if not (path.parent / target).resolve().exists():
            report.error(f"broken local link '{raw}': {path}")


def validate_dates(data: dict[str, Any], path: Path, report: Report) -> None:
    for key in ("updated_at", "generated_at"):
        value = data.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not ISO_RE.match(value):
            report.error(f"'{key}' must be ISO-8601 with timezone: {path}")
            continue
        try:
            dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            report.error(f"invalid date '{value}' for {key}: {path}")


def project_root(project_dir: Path) -> Path | None:
    if project_dir.parent.name == "ai" and project_dir.parent.parent.name == "docs":
        return project_dir.parent.parent.parent
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path, help="docs/ai/<project-slug>")
    parser.add_argument("--allow-in-progress", action="store_true")
    parser.add_argument("--artifact-only", action="store_true")
    args = parser.parse_args(argv)
    report = Report()
    base = args.project_dir.resolve()

    brainstorm_path = base / "discovery" / "brainstorm" / "BRAINSTORM.md"
    if not brainstorm_path.is_file():
        brainstorm_path = base / "brainstorm" / "BRAINSTORM.md"
    paths = {
        "progress": base / "PROGRESS.md",
        "brainstorm": brainstorm_path,
        "handoff": base / "handoffs" / "BRAINSTORM-TO-PLAN.md",
        "sources": base / "SOURCE-REGISTER.md",
        "glossary": base / "GLOSSARY.md",
        "context": base / "CONTEXT-INDEX.md",
    }
    for name in ("progress", "brainstorm", "sources", "glossary", "context"):
        if not paths[name].is_file():
            report.error(f"missing required document: {paths[name]}")

    progress, _ = frontmatter(paths["progress"], report) if paths["progress"].is_file() else ({}, "")
    brainstorm, brainstorm_body = frontmatter(paths["brainstorm"], report) if paths["brainstorm"].is_file() else ({}, "")
    status = progress.get("status")
    ready = status in READY
    if ready or not args.allow_in_progress:
        if not paths["handoff"].is_file():
            report.error(f"missing required READY handoff: {paths['handoff']}")
    handoff, handoff_body = frontmatter(paths["handoff"], report) if paths["handoff"].is_file() else ({}, "")

    if progress:
        require_keys(
            progress,
            (
                "workflow_contract", "project_id", "project_slug", "stage", "status",
                "handoff_status", "active_artifact", "next_action", "blockers", "updated_at",
            ),
            paths["progress"],
            report,
        )
        if progress.get("workflow_contract") not in {CONTRACT, LEGACY_CONTRACT}:
            report.error("PROGRESS.md uses unsupported workflow_contract")
        stage_owner = progress.get("stage_owner") or progress.get("active_skill")
        required_skill = progress.get("required_skill") or progress.get("next_skill")
        if not args.artifact_only and stage_owner != SKILL:
            report.error(f"PROGRESS.md stage_owner must be '{SKILL}', got '{stage_owner}'")
        if not args.artifact_only and required_skill not in {SKILL, NEXT_SKILL}:
            report.error(f"PROGRESS.md required_skill unexpected: '{required_skill}'")
        if not args.artifact_only and progress.get("stage") not in {"BRAINSTORM", "DISCOVERY"}:
            report.error(f"PROGRESS.md stage unexpected: '{progress.get('stage')}'")
        if not args.artifact_only and status not in ALLOWED_STATUSES:
            report.error(f"invalid brainstorm status in PROGRESS.md: {status}")
        expected_handoff = "READY" if ready else "NOT_READY"
        if not args.artifact_only and progress.get("handoff_status") != expected_handoff:
            report.error(f"handoff_status must be {expected_handoff} when status is {status}")
        slug = progress.get("project_slug")
        expected_artifacts = {
            f"docs/ai/{slug}/discovery/brainstorm/BRAINSTORM.md",
            f"docs/ai/{slug}/brainstorm/BRAINSTORM.md",
        }
        if not args.artifact_only and progress.get("active_artifact") not in expected_artifacts:
            report.error("active_artifact must point to BRAINSTORM.md")
        validate_dates(progress, paths["progress"], report)

    if brainstorm:
        require_keys(brainstorm, ("workflow_contract", "project_id", "project_slug", "updated_at"), paths["brainstorm"], report)
        if brainstorm.get("workflow_contract") not in {CONTRACT, LEGACY_CONTRACT}:
            report.error("BRAINSTORM.md uses the wrong workflow contract")
        validate_dates(brainstorm, paths["brainstorm"], report)
        validate_headings(brainstorm_body, REQUIRED_BRAINSTORM_HEADINGS, paths["brainstorm"], report)
        validate_declared_ids(brainstorm_body, paths["brainstorm"], report)
        validate_links(brainstorm_body, paths["brainstorm"], report)
        if PLACEHOLDER_RE.search(brainstorm_body):
            report.error(f"placeholder remains in {paths['brainstorm']}")
        if ready:
            unchecked = re.findall(r"^- \[ \] .+$", section(brainstorm_body, "Prontidão para planejamento"), re.MULTILINE)
            if unchecked:
                report.error("ready brainstorm has incomplete readiness checklist")
            questions = section(brainstorm_body, "Questões em aberto")
            if re.search(r"\|\s*STRUCTURAL\s*\|.*\|\s*OPEN\s*\|", questions, re.IGNORECASE):
                report.error("ready brainstorm has an open structural question")

    if handoff:
        require_keys(handoff, ("workflow_contract", "generated_at", "producer_skill", "consumer_skill", "handoff_status"), paths["handoff"], report)
        if handoff.get("workflow_contract") not in {CONTRACT, LEGACY_CONTRACT}:
            report.error("handoff uses the wrong workflow contract")
        if (
            handoff.get("producer_skill") != SKILL
            or handoff.get("consumer_skill") != NEXT_SKILL
            or handoff.get("handoff_status") != "READY"
        ):
            report.error("handoff producer/consumer/status fields are incompatible")
        validate_dates(handoff, paths["handoff"], report)
        validate_headings(handoff_body, REQUIRED_HANDOFF_HEADINGS, paths["handoff"], report)
        validate_links(handoff_body, paths["handoff"], report)
        if PLACEHOLDER_RE.search(handoff_body):
            report.error(f"placeholder remains in {paths['handoff']}")
        structural = section(handoff_body, "Questões estruturais")
        if ready and not re.fullmatch(r"(?:Nenhuma\.?|None\.?)", structural.strip(), re.IGNORECASE):
            report.error("READY handoff structural questions must contain only 'Nenhuma.' or 'None.'")

    revisions = [
        progress.get("discovery_revision") or progress.get("brainstorm_revision"),
        brainstorm.get("discovery_revision") or brainstorm.get("brainstorm_revision"),
    ]
    if handoff:
        revisions.append(
            handoff.get("discovery_revision")
            or handoff.get("brainstorm_revision")
            or handoff.get("input_revision")
        )
    if len({str(value) for value in revisions if value is not None}) > 1:
        report.error(f"discovery revisions are not synchronized: {revisions}")

    for doc in paths.values():
        if doc.is_file() and "spec-driven-dev" in doc.read_text(encoding="utf-8"):
            report.error(f"reference to nonexistent skill 'spec-driven-dev': {doc}")

    root = project_root(base)
    if root is None and not args.artifact_only:
        report.error(f"project directory must follow <root>/docs/ai/<slug>: {base}")
    elif root is not None:
        agents = root / "AGENTS.md"
        if not agents.is_file():
            report.error(f"missing project discovery index: {agents}")
        else:
            agents_text = agents.read_text(encoding="utf-8")
            pointer = f"docs/ai/{base.name}/PROGRESS.md"
            if pointer not in agents_text:
                report.error(f"AGENTS.md does not point to '{pointer}'")
            if "spec-driven-dev" in agents_text:
                report.error("AGENTS.md references nonexistent skill 'spec-driven-dev'")

    if report.errors:
        print(f"workflow_contract={CONTRACT}")
        for error in report.errors:
            print(f"ERROR: {error}")
        print(f"BRAINSTORM INVALID ({len(report.errors)} errors)")
        return 1
    print(f"workflow_contract={CONTRACT}")
    print(f"status={status}")
    print("BRAINSTORM VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
