#!/usr/bin/env python3
"""Regression: routing validator must read #### Dependencies sections.

Before the fix, validate_routing.parse_tasks only used find_field() for an
inline `Dependencies:` line. The canonical PHASE template uses a #### section,
so dependencies were silently treated as empty/NONE.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROUTING_SCRIPT = REPO / "skills" / "route-ai-work-by-capability" / "scripts" / "validate_routing.py"


def load_routing_module():
    spec = importlib.util.spec_from_file_location("validate_routing", ROUTING_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TASK_WITH_SECTION = """# F01 — Phase

### [ ] F01-001 — First task

Executor: MODEL-A
Reviewer: NONE
State: PENDING

#### Dependencies

- NONE

### [ ] F01-002 — Second task

Executor: MODEL-A
Reviewer: NONE
State: PENDING

#### Dependencies

- F01-001
"""


class RoutingDependenciesSectionTest(unittest.TestCase):
    def test_parse_tasks_reads_dependencies_section(self):
        module = load_routing_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            phase = root / "phases"
            phase.mkdir()
            (phase / "F01.md").write_text(TASK_WITH_SECTION, encoding="utf-8")
            tasks = {task.task_id: task for task in module.parse_tasks(root)}
            self.assertIn("F01-001", tasks)
            self.assertIn("F01-002", tasks)
            self.assertEqual(tasks["F01-001"].dependencies, [])
            self.assertEqual(tasks["F01-002"].dependencies, ["F01-001"])


if __name__ == "__main__":
    unittest.main()
