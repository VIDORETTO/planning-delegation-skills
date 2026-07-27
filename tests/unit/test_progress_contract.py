#!/usr/bin/env python3
"""Fixture-based tests for scripts/progress_contract.py frontmatter parsing."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROGRESS_CONTRACT_SCRIPT = REPO / "scripts" / "progress_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("progress_contract", PROGRESS_CONTRACT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALID_FRONTMATTER = """---
workflow_contract: skill-team/v3
project_id: proj-001
project_slug: proj
workflow_profile: standard
stage: DISCOVERY
status: BRAINSTORM_IN_PROGRESS
stage_owner: brainstorm-idea-with-user
required_skill: brainstorm-idea-with-user
successor_skill: create-spec-driven-plan
handoff_status: NOT_READY
discovery_revision: 1
plan_revision: 0
routing_revision: 0
implementation_revision: 0
review_revision: 0
release_revision: 0
active_artifact: docs/ai/proj/discovery/brainstorm/BRAINSTORM.md
active_task: null
active_batch: null
active_executor_model: null
active_reviewer_model: null
writer_skill: brainstorm-idea-with-user
writer_task: null
next_action: Answer pending structural questions
blockers: NONE
last_validation_command: NONE
last_validation_result: NOT_RUN
updated_at: 2026-07-27T00:00:00Z
---

# Body

Human-readable regenerated view.
"""

INVALID_FRONTMATTER_FORBIDDEN_FIELD = """---
workflow_contract: skill-team/v3
project_id: proj-001
project_slug: proj
workflow_profile: standard
stage: DISCOVERY
status: BRAINSTORM_IN_PROGRESS
stage_owner: brainstorm-idea-with-user
required_skill: brainstorm-idea-with-user
next_skill: create-spec-driven-plan
handoff_status: NOT_READY
---

Body.
"""

UNTERMINATED_FRONTMATTER = """---
workflow_contract: skill-team/v3
project_id: proj-001

Body without a closing fence.
"""

NO_FRONTMATTER = """# Just a document

No frontmatter fence at all.
"""


class ParseFrontmatterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_parses_valid_flat_frontmatter(self) -> None:
        result = self.module.parse_frontmatter(VALID_FRONTMATTER)
        self.assertTrue(result.found)
        self.assertTrue(result.terminated)
        self.assertEqual(result.data["workflow_contract"], "skill-team/v3")
        self.assertEqual(result.data["stage"], "DISCOVERY")
        self.assertEqual(result.data["discovery_revision"], "1")

    def test_detects_missing_frontmatter(self) -> None:
        result = self.module.parse_frontmatter(NO_FRONTMATTER)
        self.assertFalse(result.found)

    def test_detects_unterminated_frontmatter(self) -> None:
        result = self.module.parse_frontmatter(UNTERMINATED_FRONTMATTER)
        self.assertTrue(result.found)
        self.assertFalse(result.terminated)


class ValidateProgressFieldsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_valid_fixture_has_no_errors(self) -> None:
        result = self.module.parse_frontmatter(VALID_FRONTMATTER)
        errors = self.module.validate_progress_fields(result.data)
        self.assertEqual(errors, [])

    def test_forbidden_next_skill_is_flagged(self) -> None:
        result = self.module.parse_frontmatter(INVALID_FRONTMATTER_FORBIDDEN_FIELD)
        errors = self.module.validate_progress_fields(result.data)
        self.assertTrue(any("next_skill" in error for error in errors))

    def test_missing_required_fields_are_flagged(self) -> None:
        result = self.module.parse_frontmatter(INVALID_FRONTMATTER_FORBIDDEN_FIELD)
        errors = self.module.validate_progress_fields(result.data)
        self.assertTrue(any("missing field: discovery_revision" in error for error in errors))

    def test_wrong_workflow_contract_is_flagged(self) -> None:
        data = {"workflow_contract": "planning-delegation/v2"}
        errors = self.module.validate_progress_fields(data)
        self.assertTrue(any("workflow_contract" in error for error in errors))

    def test_invalid_handoff_status_is_flagged(self) -> None:
        data = {"handoff_status": "MAYBE"}
        errors = self.module.validate_progress_fields(data)
        self.assertTrue(any("handoff_status" in error for error in errors))

    def test_negative_revision_is_flagged(self) -> None:
        data = {"plan_revision": "-1"}
        errors = self.module.validate_progress_fields(data)
        self.assertTrue(any("plan_revision" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
