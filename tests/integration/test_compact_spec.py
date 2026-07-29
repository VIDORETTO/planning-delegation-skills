#!/usr/bin/env python3
"""Integration coverage for F02-002 compact product specifications."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "compact-spec"


def load_validator():
    path = REPO / "skills" / "create-spec-driven-plan" / "scripts" / "validate_plan.py"
    spec = importlib.util.spec_from_file_location("validate_plan_compact_spec", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CompactSpecTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def validate(self, fixture: str):
        return self.validator.validate_spec(FIXTURES / fixture / "plan" / "SPEC.md")

    def test_valid_spec_has_stable_requirements_and_origins(self):
        records, errors = self.validate("valid")
        self.assertEqual(errors, [])
        self.assertEqual(set(records), {"REQ-001", "REQ-002"})
        self.assertEqual(records["REQ-001"]["Origin"], "CR-001 / SRC-001")
        self.assertEqual(records["REQ-001"]["State"], "ACTIVE")

    def test_p1_story_requires_independent_value(self):
        _, errors = self.validate("missing-independent-value")
        self.assertIn("SPEC.md story missing Independent value: US-001", errors)

    def test_unapproved_technical_detail_is_blocking(self):
        _, errors = self.validate("unapproved-technical-detail")
        self.assertIn("SPEC.md contains unapproved technical implementation detail: REQ-001", errors)


if __name__ == "__main__":
    unittest.main()
