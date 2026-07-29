"""Static schema contract tests; runtime enforcement is added by F01-002."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ContractSchemasTest(unittest.TestCase):
    def test_progress_requires_every_active_and_writer_field(self):
        schema = json.loads((ROOT / "contracts/progress-schema.json").read_text())
        self.assertTrue({"active_task", "active_batch", "active_executor_model", "active_reviewer_model", "writer_task"}.issubset(schema["required"]))
        self.assertFalse(schema["additionalProperties"])

    def test_handoff_inventory_includes_waived_review_path(self):
        schema = json.loads((ROOT / "contracts/handoff-schema.json").read_text())
        self.assertIn("implementation-to-release", schema["properties"]["handoff_type"]["enum"])
        self.assertFalse(schema["additionalProperties"])

    def test_task_and_routing_schemas_require_operational_metadata(self):
        task = json.loads((ROOT / "contracts/task-schema.json").read_text())
        routing = json.loads((ROOT / "contracts/routing-schema.json").read_text())
        self.assertIn("acceptance", task["required"])
        self.assertIn("parallel_eligible", routing["required"])
