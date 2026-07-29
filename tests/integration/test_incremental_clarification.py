#!/usr/bin/env python3
"""Integration coverage for F02-003 incremental clarification records."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "clarification"


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class IncrementalClarificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brainstorm = load("validate_brainstorm_clarification", "skills/brainstorm-idea-with-user/scripts/validate_brainstorm.py")
        cls.plan = load("validate_plan_clarification", "skills/create-spec-driven-plan/scripts/validate_plan.py")

    def fixture(self, name: str) -> str:
        return (FIXTURES / name / "records.md").read_text(encoding="utf-8")

    def test_answer_is_persisted_once_with_authority_and_revision(self):
        record = self.fixture("valid")
        errors = self.brainstorm.validate_clarification_records(record, FIXTURES / "valid" / "records.md")
        self.assertEqual(errors, [])
        self.assertIn("Autoridade: usuário", record)
        self.assertIn("Revisão: 1", record)

    def test_duplicate_question_is_rejected_before_it_can_be_asked_again(self):
        errors = self.brainstorm.validate_clarification_records(self.fixture("duplicate"), FIXTURES / "duplicate" / "records.md")
        self.assertIn("duplicate clarification question: Q-002 duplicates Q-001", errors)

    def test_conflicting_active_answers_are_rejected(self):
        errors = self.plan.validate_clarification_records(self.fixture("contradiction"))
        self.assertIn("SPEC.md contradictory active clarification decisions: Q-002 conflicts with Q-001", errors)

    def test_product_intent_return_is_owned_by_discovery(self):
        record = self.fixture("return-to-discovery")
        errors = self.plan.validate_clarification_records(record)
        self.assertEqual(errors, [])
        self.assertEqual(
            self.plan.clarification_blocks_plan_validation(record),
            "PLAN_VALIDATED requires return to brainstorm-idea-with-user for product intent",
        )


if __name__ == "__main__":
    unittest.main()
