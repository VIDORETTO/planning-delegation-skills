#!/usr/bin/env python3
"""Integration coverage for F02-004 requirements-quality checklists."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "requirements-checklists"


def load_validator():
    path = REPO / "skills" / "create-spec-driven-plan" / "scripts" / "validate_plan.py"
    spec = importlib.util.spec_from_file_location("validate_plan_requirements_checklists", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RequirementsChecklistTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def validate(self, fixture: str, profile: str, revision: int, requirements=None):
        return self.validator.validate_requirements_checklists(
            FIXTURES / fixture, profile, revision, requirements
        )

    def test_standard_profile_requires_traceable_core_domains(self):
        errors, warnings = self.validate("valid", "standard", 3, {"REQ-001"})
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_unchecked_critical_item_blocks_validation(self):
        errors, warnings = self.validate("critical-unchecked", "compact", 1)
        self.assertIn("unchecked critical checklist item blocks plan validation: CHK-001", errors)
        self.assertEqual(warnings, [])

    def test_unchecked_advisory_item_is_explicit_and_non_blocking(self):
        errors, warnings = self.validate("advisory-open", "compact", 1)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, ["unchecked advisory checklist item: CHK-001"])

    def test_material_spec_change_requires_current_re_evaluation(self):
        errors, _ = self.validate("stale-and-implementation", "compact", 2, {"REQ-001"})
        self.assertIn(
            "checklist plan/checklists/requirements-completeness.md is stale for plan_revision", errors
        )
        self.assertIn(
            "checklist plan/checklists/requirements-completeness.md requires re-evaluation", errors
        )

    def test_checklists_reject_implementation_tests(self):
        errors, _ = self.validate("stale-and-implementation", "compact", 1, {"REQ-001"})
        self.assertIn(
            "checklist plan/checklists/requirements-completeness.md: CHK-001 tests implementation behavior instead of written requirements",
            errors,
        )

    def test_every_checklist_item_requires_a_requirement_or_gap_marker(self):
        errors, _ = self.validate("missing-traceability", "compact", 1)
        self.assertIn(
            "checklist plan/checklists/requirements-completeness.md has malformed checklist item: CHK-001",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
