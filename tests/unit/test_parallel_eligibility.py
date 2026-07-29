#!/usr/bin/env python3
"""F02-006 fixtures for deterministic parallel-eligibility checks."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "skills" / "route-ai-work-by-capability" / "scripts" / "validate_routing.py"
FIXTURES = REPO / "tests" / "fixtures" / "parallel-eligibility"


def load_module():
    spec = importlib.util.spec_from_file_location("parallel_eligibility_validator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ParallelEligibilityTest(unittest.TestCase):
    def validate_fixture(self, name: str) -> list[str]:
        module = load_module()
        root = FIXTURES / name
        tasks = {task.task_id: task for task in module.parse_tasks(root / "plan")}
        routes, parse_errors = module.parse_routes(root / "routing" / "ROUTING.md")
        errors = parse_errors + module.validate_parallel_eligibility(tasks, {route.task_id: route for route in routes}, [])
        return errors

    def test_disjoint_dependency_ready_tasks_are_eligible(self):
        self.assertEqual([], self.validate_fixture("disjoint-ready"))

    def test_overlapping_file_scope_is_rejected(self):
        errors = self.validate_fixture("overlapping-scope")
        self.assertTrue(any("parallel task lock conflict" in error for error in errors), errors)

    def test_unresolved_dependency_is_rejected(self):
        errors = self.validate_fixture("unresolved-dependency")
        self.assertTrue(any("unresolved dependencies" in error for error in errors), errors)

    def test_global_state_and_migration_are_rejected(self):
        errors = self.validate_fixture("global-state-migration")
        self.assertTrue(any("global state" in error for error in errors), errors)
        self.assertTrue(any("migration" in error for error in errors), errors)

    def test_missing_isolation_and_merge_strategy_is_rejected(self):
        errors = self.validate_fixture("missing-strategy")
        self.assertTrue(any("missing isolation/merge strategy" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
