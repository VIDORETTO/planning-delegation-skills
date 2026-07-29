#!/usr/bin/env python3
"""Integration coverage for the F02-001 deterministic governance planning gate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "governance"


def load_validator():
    path = REPO / "skills" / "create-spec-driven-plan" / "scripts" / "validate_plan.py"
    spec = importlib.util.spec_from_file_location("validate_plan_governance", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GovernanceGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def test_confirmed_must_conflict_blocks(self):
        errors, _ = self.validator.validate_governance(FIXTURES / "must-conflict", "standard")
        self.assertIn("confirmed MUST conflict blocks plan validation: GOV-001", errors)

    def test_valid_governance_record_passes(self):
        errors, warnings = self.validator.validate_governance(FIXTURES / "valid", "standard")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_authorized_exception_is_traceable(self):
        errors, warnings = self.validator.validate_governance(FIXTURES / "authorized-exception", "standard")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_compact_profile_explicitly_permits_absent_governance(self):
        errors, warnings = self.validator.validate_governance(FIXTURES / "empty", "compact")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_standard_profile_requires_governance(self):
        errors, _ = self.validator.validate_governance(FIXTURES / "empty", "standard")
        self.assertIn("missing governance records for profile=standard", errors)


if __name__ == "__main__":
    unittest.main()
