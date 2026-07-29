#!/usr/bin/env python3
"""Golden tests for the deterministic F02-005 plan consistency analysis."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "plan-analysis"


def load_analyzer():
    path = REPO / "skills" / "create-spec-driven-plan" / "scripts" / "analyze_plan.py"
    spec = importlib.util.spec_from_file_location("analyze_plan_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PlanAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = load_analyzer()

    def assert_golden(self, fixture: str):
        actual = self.analyzer.analyze(FIXTURES / fixture)
        expected = json.loads((FIXTURES / fixture / "expected.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)
        self.assertEqual(self.analyzer.render_report(actual), self.analyzer.render_report(expected))

    def test_advisory_findings_and_metrics_match_golden(self):
        self.assert_golden("advisory")

    def test_mechanical_findings_and_metrics_match_golden(self):
        self.assert_golden("mechanical")

    def test_report_is_deterministic(self):
        first = self.analyzer.analyze(FIXTURES / "mechanical")
        second = self.analyzer.analyze(FIXTURES / "mechanical")
        self.assertEqual(first, second)
        self.assertEqual(self.analyzer.render_report(first), self.analyzer.render_report(second))


if __name__ == "__main__":
    unittest.main()
