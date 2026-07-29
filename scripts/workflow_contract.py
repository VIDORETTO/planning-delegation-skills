"""Strict cross-record validation for the skill-team/v3 workflow."""
from __future__ import annotations

import datetime as dt
import re
from typing import Mapping

from progress_contract import REQUIRED_FIELDS, WORKFLOW_CONTRACT, validate_progress_fields

STATES = {
    ("DISCOVERY", "BRAINSTORM_IN_PROGRESS"): ("brainstorm-idea-with-user", "brainstorm-idea-with-user", "brainstorm-idea-with-user", "NOT_READY"),
    ("DISCOVERY", "CODEBASE_INVESTIGATION_IN_PROGRESS"): ("investigate-existing-codebase", "investigate-existing-codebase", "investigate-existing-codebase", "NOT_READY"),
    ("DISCOVERY", "UX_AUDIT_IN_PROGRESS"): ("product-ux-audit", "product-ux-audit", "product-ux-audit", "NOT_READY"),
    ("DISCOVERY", "DISCOVERY_READY"): (None, "create-spec-driven-plan", None, "READY"),
    ("DISCOVERY", "DISCOVERY_BLOCKED"): (None, None, None, "NOT_READY"),
    ("PLANNING", "PLAN_IN_PROGRESS"): ("create-spec-driven-plan", "create-spec-driven-plan", "create-spec-driven-plan", "NOT_READY"),
    ("PLANNING", "PLAN_VALIDATED"): ("create-spec-driven-plan", "route-ai-work-by-capability", None, "READY"),
    ("PLANNING", "REPLAN_REQUIRED"): ("create-spec-driven-plan", "create-spec-driven-plan", None, "NOT_READY"),
    ("ROUTING", "ROUTING_IN_PROGRESS"): ("route-ai-work-by-capability", "route-ai-work-by-capability", "route-ai-work-by-capability", "NOT_READY"),
    ("ROUTING", "IMPLEMENTATION_READY"): ("route-ai-work-by-capability", "execute-routed-task", None, "READY"),
    ("ROUTING", "REROUTE_REQUIRED"): ("route-ai-work-by-capability", "route-ai-work-by-capability", None, "NOT_READY"),
    ("IMPLEMENTATION", "TASK_IN_PROGRESS"): ("execute-routed-task", "execute-routed-task", "execute-routed-task", "CONSUMED"),
    ("IMPLEMENTATION", "TASK_COMPLETE"): ("execute-routed-task", "execute-routed-task", None, "NOT_READY"),
    ("IMPLEMENTATION", "TASK_BLOCKED"): ("execute-routed-task", None, None, "NOT_READY"),
    ("IMPLEMENTATION", "IMPLEMENTATION_COMPLETE"): ("execute-routed-task", None, None, "READY"),
    ("REVIEW", "REVIEW_REQUIRED"): ("review-implementation-evidence", "review-implementation-evidence", None, "READY"),
    ("REVIEW", "REVIEW_IN_PROGRESS"): ("review-implementation-evidence", "review-implementation-evidence", "review-implementation-evidence", "CONSUMED"),
    ("REVIEW", "CHANGES_REQUIRED"): ("review-implementation-evidence", "execute-routed-task", None, "READY"),
    ("REVIEW", "REVIEW_APPROVED"): ("review-implementation-evidence", "validate-release-readiness", None, "READY"),
    ("RELEASE", "RELEASE_REVIEW_REQUIRED"): ("validate-release-readiness", "validate-release-readiness", None, "READY"),
    ("RELEASE", "RELEASE_REVIEW_IN_PROGRESS"): ("validate-release-readiness", "validate-release-readiness", "validate-release-readiness", "CONSUMED"),
    ("RELEASE", "RELEASE_BLOCKED"): ("validate-release-readiness", "validate-release-readiness", None, "NOT_READY"),
    ("RELEASE", "RELEASE_READY"): ("validate-release-readiness", "NONE", None, "CONSUMED"),
    ("RELEASE", "RELEASED"): ("validate-release-readiness", "NONE", None, "CONSUMED"),
    ("RELEASE", "POST_RELEASE_REVIEW_REQUIRED"): ("validate-release-readiness", "validate-release-readiness", None, "NOT_READY"),
    ("RELEASE", "POST_RELEASE_REVIEW_IN_PROGRESS"): ("validate-release-readiness", "validate-release-readiness", "validate-release-readiness", "CONSUMED"),
}
HANDOFF_TYPES = {"brainstorm-to-plan", "codebase-to-plan", "ux-audit-to-plan", "plan-to-routing", "routing-to-implementation", "implementation-to-review", "implementation-to-release", "review-to-implementation", "review-to-release"}
HANDOFF_SECTIONS = ("Identification", "Summary", "Artifact inventory", "Preserved decisions", "Allowed open questions", "Blockers", "Consumer write scope", "Forbidden files", "Commands and results", "Stop instruction")
HANDOFF_ROLES = {
    "brainstorm-to-plan": ("brainstorm-idea-with-user", "create-spec-driven-plan"),
    "codebase-to-plan": ("investigate-existing-codebase", "create-spec-driven-plan"),
    "ux-audit-to-plan": ("product-ux-audit", "create-spec-driven-plan"),
    "plan-to-routing": ("create-spec-driven-plan", "route-ai-work-by-capability"),
    "routing-to-implementation": ("route-ai-work-by-capability", "execute-routed-task"),
    "implementation-to-review": ("execute-routed-task", "review-implementation-evidence"),
    "implementation-to-release": ("execute-routed-task", "validate-release-readiness"),
    "review-to-implementation": ("review-implementation-evidence", "execute-routed-task"),
    "review-to-release": ("review-implementation-evidence", "validate-release-readiness"),
}
HANDOFF_FIELDS = {"workflow_contract", "handoff_type", "project_id", "producer_skill", "consumer_skill", "input_revision", "output_revision", "handoff_status", "validation_command", "validation_result", "generated_at"}
HANDOFF_STATUSES = {"NOT_READY", "READY", "CONSUMED"}
VALIDATION_RESULTS = {"PASS", "FAIL", "NOT_RUN"}
TASK_BLOCKED_REQUIRED_SKILLS = {
    "route-ai-work-by-capability",
    "create-spec-driven-plan",
    "investigate-existing-codebase",
    "brainstorm-idea-with-user",
}
IMPLEMENTATION_COMPLETE_REQUIRED_SKILLS = {
    "review-implementation-evidence",
    "validate-release-readiness",
}
ISO_8601_WITH_TIMEZONE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})$")

# A pointer may remain in the same state while its active artifact changes. A
# state change, however, must follow one of these canonical workflow edges.
TRANSITIONS = {
    ("DISCOVERY", "BRAINSTORM_IN_PROGRESS"): {("DISCOVERY", "DISCOVERY_READY"), ("DISCOVERY", "DISCOVERY_BLOCKED")},
    ("DISCOVERY", "CODEBASE_INVESTIGATION_IN_PROGRESS"): {("DISCOVERY", "DISCOVERY_READY"), ("DISCOVERY", "DISCOVERY_BLOCKED")},
    ("DISCOVERY", "UX_AUDIT_IN_PROGRESS"): {("DISCOVERY", "DISCOVERY_READY"), ("DISCOVERY", "DISCOVERY_BLOCKED")},
    ("DISCOVERY", "DISCOVERY_READY"): {("PLANNING", "PLAN_IN_PROGRESS")},
    ("DISCOVERY", "DISCOVERY_BLOCKED"): {("DISCOVERY", "BRAINSTORM_IN_PROGRESS"), ("DISCOVERY", "CODEBASE_INVESTIGATION_IN_PROGRESS"), ("DISCOVERY", "UX_AUDIT_IN_PROGRESS")},
    ("PLANNING", "PLAN_IN_PROGRESS"): {("PLANNING", "PLAN_VALIDATED"), ("PLANNING", "REPLAN_REQUIRED")},
    ("PLANNING", "PLAN_VALIDATED"): {("ROUTING", "ROUTING_IN_PROGRESS")},
    ("PLANNING", "REPLAN_REQUIRED"): {("PLANNING", "PLAN_IN_PROGRESS")},
    ("ROUTING", "ROUTING_IN_PROGRESS"): {("ROUTING", "IMPLEMENTATION_READY"), ("ROUTING", "REROUTE_REQUIRED")},
    ("ROUTING", "IMPLEMENTATION_READY"): {("IMPLEMENTATION", "TASK_IN_PROGRESS")},
    ("ROUTING", "REROUTE_REQUIRED"): {("ROUTING", "ROUTING_IN_PROGRESS")},
    ("IMPLEMENTATION", "TASK_IN_PROGRESS"): {("IMPLEMENTATION", "TASK_COMPLETE"), ("IMPLEMENTATION", "TASK_BLOCKED")},
    ("IMPLEMENTATION", "TASK_COMPLETE"): {("IMPLEMENTATION", "TASK_IN_PROGRESS"), ("IMPLEMENTATION", "IMPLEMENTATION_COMPLETE")},
    ("IMPLEMENTATION", "TASK_BLOCKED"): {("IMPLEMENTATION", "TASK_IN_PROGRESS")},
    ("IMPLEMENTATION", "IMPLEMENTATION_COMPLETE"): {("REVIEW", "REVIEW_REQUIRED"), ("RELEASE", "RELEASE_REVIEW_REQUIRED")},
    ("REVIEW", "REVIEW_REQUIRED"): {("REVIEW", "REVIEW_IN_PROGRESS")},
    ("REVIEW", "REVIEW_IN_PROGRESS"): {("REVIEW", "CHANGES_REQUIRED"), ("REVIEW", "REVIEW_APPROVED")},
    ("REVIEW", "CHANGES_REQUIRED"): {("IMPLEMENTATION", "TASK_IN_PROGRESS"), ("ROUTING", "REROUTE_REQUIRED"), ("PLANNING", "REPLAN_REQUIRED"), ("DISCOVERY", "BRAINSTORM_IN_PROGRESS"), ("DISCOVERY", "CODEBASE_INVESTIGATION_IN_PROGRESS")},
    ("REVIEW", "REVIEW_APPROVED"): {("RELEASE", "RELEASE_REVIEW_REQUIRED")},
    ("RELEASE", "RELEASE_REVIEW_REQUIRED"): {("RELEASE", "RELEASE_REVIEW_IN_PROGRESS")},
    ("RELEASE", "RELEASE_REVIEW_IN_PROGRESS"): {("RELEASE", "RELEASE_BLOCKED"), ("RELEASE", "RELEASE_READY")},
    ("RELEASE", "RELEASE_BLOCKED"): {("RELEASE", "RELEASE_REVIEW_IN_PROGRESS")},
    ("RELEASE", "RELEASE_READY"): {("RELEASE", "RELEASED")},
    ("RELEASE", "RELEASED"): {("RELEASE", "POST_RELEASE_REVIEW_REQUIRED")},
    ("RELEASE", "POST_RELEASE_REVIEW_REQUIRED"): {("RELEASE", "POST_RELEASE_REVIEW_IN_PROGRESS")},
}
REVISION_ON_ENTRY = {
    ("DISCOVERY", "DISCOVERY_READY"): "discovery_revision",
    ("PLANNING", "PLAN_VALIDATED"): "plan_revision",
    ("ROUTING", "IMPLEMENTATION_READY"): "routing_revision",
    ("IMPLEMENTATION", "IMPLEMENTATION_COMPLETE"): "implementation_revision",
    ("REVIEW", "CHANGES_REQUIRED"): "review_revision",
    ("REVIEW", "REVIEW_APPROVED"): "review_revision",
    ("RELEASE", "RELEASE_BLOCKED"): "release_revision",
    ("RELEASE", "RELEASE_READY"): "release_revision",
}


def _error(code: str, field: str, detail: str) -> str:
    return f"{code} {field}: {detail}"


def validate_progress(data: Mapping[str, str], previous: Mapping[str, str] | None = None) -> list[str]:
    errors: list[str] = []
    for error in validate_progress_fields(dict(data)):
        code = "STV3-E001-CONTRACT" if "workflow_contract" in error else "STV3-E002-FIELD-MISSING" if "missing" in error else "STV3-E005-ENUM"
        errors.append(_error(code, "PROGRESS.md", error))
    unknown = set(data) - set(REQUIRED_FIELDS)
    for field in sorted(unknown):
        errors.append(_error("STV3-E003-FIELD-UNKNOWN", field, "not in canonical PROGRESS.md fields"))
    state = (data.get("stage"), data.get("status"))
    expected = STATES.get(state)
    if not expected:
        errors.append(_error("STV3-E006-STAGE-STATUS", "status", f"{state!r} is not canonical"))
        return sorted(errors)
    owner, required, writer, handoff = expected
    if owner and data.get("stage_owner") != owner:
        errors.append(_error("STV3-E007-OWNER", "stage_owner", "does not own state"))
    if state == ("DISCOVERY", "DISCOVERY_READY") and data.get("stage_owner") not in {"brainstorm-idea-with-user", "investigate-existing-codebase", "product-ux-audit"}:
        errors.append(_error("STV3-E007-OWNER", "stage_owner", "must be the final discovery producer"))
    if required and data.get("required_skill") != required:
        errors.append(_error("STV3-E008-REQUIRED-SKILL", "required_skill", "does not match state"))
    if state == ("IMPLEMENTATION", "TASK_BLOCKED") and data.get("required_skill") not in TASK_BLOCKED_REQUIRED_SKILLS:
        errors.append(_error("STV3-E008-REQUIRED-SKILL", "required_skill", "must be the classified blocker owner"))
    if state == ("IMPLEMENTATION", "IMPLEMENTATION_COMPLETE") and data.get("required_skill") not in IMPLEMENTATION_COMPLETE_REQUIRED_SKILLS:
        errors.append(_error("STV3-E008-REQUIRED-SKILL", "required_skill", "must be the reviewer or release validator"))
    if data.get("writer_skill") != (writer or "null"):
        errors.append(_error("STV3-E009-WRITER-LOCK", "writer_skill", "does not match active state"))
    if data.get("handoff_status") != handoff:
        errors.append(_error("STV3-E012-HANDOFF-CONTRACT", "handoff_status", "does not match state"))
    if (state == ("IMPLEMENTATION", "TASK_IN_PROGRESS")) != (data.get("writer_task") not in (None, "null", "")):
        errors.append(_error("STV3-E009-WRITER-LOCK", "writer_task", "is required only for active implementation"))
    for field in (name for name in REQUIRED_FIELDS if name.endswith("_revision")):
        value = data.get(field, "")
        if not re.fullmatch(r"\d+", value):
            errors.append(_error("STV3-E010-REVISION", field, "must be a non-negative integer"))
        elif previous and int(value) < int(previous.get(field, "0")):
            errors.append(_error("STV3-E010-REVISION", field, "must not decrease"))
    if previous:
        errors.extend(validate_transition(previous, data))
    timestamp = data.get("updated_at")
    if not _valid_timestamp(timestamp):
        errors.append(_error("STV3-E011-TIMESTAMP", "updated_at", "must be ISO-8601 with timezone"))
    return sorted(set(errors))


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not ISO_8601_WITH_TIMEZONE.fullmatch(value):
        return False
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_transition(previous: Mapping[str, str], current: Mapping[str, str]) -> list[str]:
    """Validate a persisted PROGRESS.md update without interpreting artifacts."""
    errors: list[str] = []
    before = (previous.get("stage"), previous.get("status"))
    after = (current.get("stage"), current.get("status"))
    if before != after and after not in TRANSITIONS.get(before, set()):
        errors.append(_error("STV3-E014-TRANSITION", "status", f"{before!r} cannot transition to {after!r}"))
    changed: list[str] = []
    for field in (name for name in REQUIRED_FIELDS if name.endswith("_revision")):
        old, new = previous.get(field), current.get(field)
        if not re.fullmatch(r"\d+", str(old)) or not re.fullmatch(r"\d+", str(new)):
            continue
        delta = int(str(new)) - int(str(old))
        if delta < 0 or delta > 1:
            errors.append(_error("STV3-E010-REVISION", field, "must increase by at most one per transition"))
        if delta == 1:
            changed.append(field)
    if len(changed) > 1:
        errors.append(_error("STV3-E010-REVISION", "revisions", "only one revision may increment per transition"))
    required_revision = REVISION_ON_ENTRY.get(after) if before != after else None
    if before == ("DISCOVERY", "DISCOVERY_READY") and after == ("PLANNING", "PLAN_IN_PROGRESS"):
        required_revision = "plan_revision"
    if required_revision and current.get(required_revision) != str(int(str(previous.get(required_revision, "0"))) + 1):
        errors.append(_error("STV3-E010-REVISION", required_revision, f"must increment when entering {after[1]}"))
    return errors


def validate_handoff(frontmatter: Mapping[str, str], body: str) -> list[str]:
    errors = []
    for field in sorted(HANDOFF_FIELDS - set(frontmatter)):
        errors.append(_error("STV3-E002-FIELD-MISSING", field, "required handoff field is absent"))
    for field in sorted(set(frontmatter) - HANDOFF_FIELDS):
        errors.append(_error("STV3-E003-FIELD-UNKNOWN", field, "not in canonical handoff fields"))
    if frontmatter.get("workflow_contract") != WORKFLOW_CONTRACT:
        errors.append(_error("STV3-E001-CONTRACT", "workflow_contract", "must be skill-team/v3"))
    if frontmatter.get("handoff_type") not in HANDOFF_TYPES:
        errors.append(_error("STV3-E012-HANDOFF-CONTRACT", "handoff_type", "is not canonical"))
    else:
        producer, consumer = HANDOFF_ROLES[frontmatter["handoff_type"]]
        if frontmatter.get("producer_skill") != producer or frontmatter.get("consumer_skill") != consumer:
            errors.append(_error("STV3-E012-HANDOFF-CONTRACT", "producer_skill", "producer/consumer do not match handoff type"))
    for field in ("input_revision", "output_revision"):
        if not re.fullmatch(r"\d+", str(frontmatter.get(field, ""))):
            errors.append(_error("STV3-E010-REVISION", field, "must be a non-negative integer"))
    if frontmatter.get("handoff_status") not in HANDOFF_STATUSES:
        errors.append(_error("STV3-E005-ENUM", "handoff_status", "is not canonical"))
    if frontmatter.get("validation_result") not in VALIDATION_RESULTS:
        errors.append(_error("STV3-E005-ENUM", "validation_result", "is not canonical"))
    if frontmatter.get("handoff_status") == "READY" and frontmatter.get("validation_result") != "PASS":
        errors.append(_error("STV3-E012-HANDOFF-CONTRACT", "validation_result", "READY requires PASS"))
    if not _valid_timestamp(frontmatter.get("generated_at")):
        errors.append(_error("STV3-E011-TIMESTAMP", "generated_at", "must be ISO-8601 with timezone"))
    for field in ("project_id", "validation_command"):
        if not str(frontmatter.get(field, "")).strip():
            errors.append(_error("STV3-E004-VALUE", field, "must not be empty"))
    errors.extend(_validate_handoff_body(body))
    return sorted(errors)


def _validate_handoff_body(body: str) -> list[str]:
    if not body.strip():
        return [_error("STV3-E013-HANDOFF-BODY", "body", "must not be empty")]
    headings = list(re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", body))
    errors: list[str] = []
    for section in HANDOFF_SECTIONS:
        matches = [match for match in headings if match.group(1).strip() == section]
        if not matches:
            errors.append(_error("STV3-E013-HANDOFF-BODY", section, "required section is absent"))
            continue
        match = matches[0]
        next_heading = next((candidate for candidate in headings if candidate.start() > match.start()), None)
        content = body[match.end():next_heading.start() if next_heading else len(body)]
        if not content.strip():
            errors.append(_error("STV3-E013-HANDOFF-BODY", section, "section must not be empty"))
    return errors
