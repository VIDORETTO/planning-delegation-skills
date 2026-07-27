#!/usr/bin/env python3
"""Shared, dependency-free helpers for the skill-team/v3 PROGRESS.md frontmatter contract.

This module intentionally uses only the standard library so it can be imported
from repository validators, migration tooling, and unit tests without adding a
runtime dependency to any skill.

See contracts/skill-team-v3.md for the authoritative field list.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

WORKFLOW_CONTRACT = "skill-team/v3"
FORBIDDEN_FIELDS = {"next_skill"}

REQUIRED_FIELDS: tuple[str, ...] = (
    "workflow_contract",
    "project_id",
    "project_slug",
    "workflow_profile",
    "stage",
    "status",
    "stage_owner",
    "required_skill",
    "successor_skill",
    "handoff_status",
    "discovery_revision",
    "plan_revision",
    "routing_revision",
    "implementation_revision",
    "review_revision",
    "release_revision",
    "active_artifact",
    "active_task",
    "active_batch",
    "active_executor_model",
    "active_reviewer_model",
    "writer_skill",
    "writer_task",
    "next_action",
    "blockers",
    "last_validation_command",
    "last_validation_result",
    "updated_at",
)

REVISION_FIELDS: tuple[str, ...] = tuple(
    name for name in REQUIRED_FIELDS if name.endswith("_revision")
)

ALLOWED_WORKFLOW_PROFILES = {"compact", "standard", "critical"}
ALLOWED_HANDOFF_STATUS = {"NOT_READY", "READY", "CONSUMED"}
ALLOWED_STAGES = {
    "DISCOVERY",
    "PLANNING",
    "ROUTING",
    "IMPLEMENTATION",
    "REVIEW",
    "RELEASE",
}
ALLOWED_VALIDATION_RESULT = {"PASS", "FAIL", "NOT_RUN"}

_FRONTMATTER_LINE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$")


@dataclass
class FrontmatterResult:
    """Result of parsing a flat YAML frontmatter block."""

    data: dict[str, str] = field(default_factory=dict)
    found: bool = False
    terminated: bool = True


def parse_frontmatter(text: str) -> FrontmatterResult:
    """Parse a flat (non-nested) YAML frontmatter block from Markdown text.

    Only simple ``key: value`` lines are supported, matching every artifact in
    this repository. Returns ``found=False`` when the text does not start with
    a ``---`` fence, and ``terminated=False`` when the opening fence is never
    closed.
    """

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return FrontmatterResult(data={}, found=False, terminated=True)

    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return FrontmatterResult(data=data, found=True, terminated=True)
        match = _FRONTMATTER_LINE.match(line)
        if match:
            data[match.group(1)] = match.group(2).strip().strip("\"'")
    return FrontmatterResult(data=data, found=True, terminated=False)


def load_frontmatter(path: Path) -> FrontmatterResult:
    if not path.is_file():
        return FrontmatterResult(data={}, found=False, terminated=True)
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def validate_progress_fields(data: dict[str, str]) -> list[str]:
    """Validate a parsed PROGRESS.md frontmatter dict against skill-team/v3.

    Returns a list of human-readable error strings; an empty list means the
    frontmatter satisfies the structural contract (this does not validate
    cross-file consistency such as matching revisions between handoffs).
    """

    errors: list[str] = []

    for name in FORBIDDEN_FIELDS:
        if name in data:
            errors.append(f"forbidden field present: {name}")

    for name in REQUIRED_FIELDS:
        if name not in data:
            errors.append(f"missing field: {name}")

    if data.get("workflow_contract") not in (None, "") and data.get("workflow_contract") != WORKFLOW_CONTRACT:
        errors.append(
            f"workflow_contract must be {WORKFLOW_CONTRACT!r}, got {data.get('workflow_contract')!r}"
        )

    profile = data.get("workflow_profile")
    if profile is not None and profile not in ALLOWED_WORKFLOW_PROFILES:
        errors.append(f"invalid workflow_profile: {profile!r}")

    stage = data.get("stage")
    if stage is not None and stage not in ALLOWED_STAGES:
        errors.append(f"invalid stage: {stage!r}")

    handoff_status = data.get("handoff_status")
    if handoff_status is not None and handoff_status not in ALLOWED_HANDOFF_STATUS:
        errors.append(f"invalid handoff_status: {handoff_status!r}")

    validation_result = data.get("last_validation_result")
    if validation_result is not None and validation_result not in ALLOWED_VALIDATION_RESULT:
        errors.append(f"invalid last_validation_result: {validation_result!r}")

    for name in REVISION_FIELDS:
        value = data.get(name)
        if value is None:
            continue
        if not re.match(r"^-?\d+$", value):
            errors.append(f"{name} must be an integer, got {value!r}")
        elif int(value) < 0:
            errors.append(f"{name} must not be negative, got {value!r}")

    return errors


__all__ = [
    "WORKFLOW_CONTRACT",
    "FORBIDDEN_FIELDS",
    "REQUIRED_FIELDS",
    "REVISION_FIELDS",
    "ALLOWED_WORKFLOW_PROFILES",
    "ALLOWED_HANDOFF_STATUS",
    "ALLOWED_STAGES",
    "ALLOWED_VALIDATION_RESULT",
    "FrontmatterResult",
    "parse_frontmatter",
    "load_frontmatter",
    "validate_progress_fields",
]
