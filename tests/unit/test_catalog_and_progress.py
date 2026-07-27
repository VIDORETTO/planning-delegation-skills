#!/usr/bin/env python3
"""Smoke tests for catalog and progress contract helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class CatalogTest(unittest.TestCase):
    def test_catalog_lists_nine_active_skills(self):
        catalog = json.loads((REPO / "catalog" / "skills.json").read_text(encoding="utf-8"))
        names = [item["name"] for item in catalog["skills"]]
        self.assertEqual(len(names), 9)
        self.assertNotIn("advisor-planner", names)
        self.assertIn("execute-routed-task", names)
        self.assertIn("investigate-existing-codebase", names)


class ProgressContractTest(unittest.TestCase):
    def test_v3_progress_fields_roundtrip(self):
        from scripts.frontmatter_util import parse_frontmatter

        text = """---
workflow_contract: skill-team/v3
project_id: PRJ-001
project_slug: example
workflow_profile: compact
stage: DISCOVERY
status: DISCOVERY_READY
stage_owner: brainstorm-idea-with-user
required_skill: create-spec-driven-plan
successor_skill: route-ai-work-by-capability
handoff_status: READY
discovery_revision: 1
plan_revision: 0
routing_revision: 0
implementation_revision: 0
review_revision: 0
release_revision: 0
active_artifact: docs/ai/example/discovery/brainstorm/BRAINSTORM.md
active_task: null
active_batch: null
active_executor_model: null
active_reviewer_model: null
writer_skill: null
writer_task: null
next_action: Start planning
blockers: NONE
last_validation_command: NONE
last_validation_result: PASS
updated_at: 2026-07-27T12:00:00-03:00
---

# Progress
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PROGRESS.md"
            path.write_text(text, encoding="utf-8")
            data = parse_frontmatter(path)
            self.assertEqual(data["workflow_contract"], "skill-team/v3")
            self.assertEqual(data["required_skill"], "create-spec-driven-plan")
            self.assertNotIn("next_skill", data)


class MigratorSmokeTest(unittest.TestCase):
    def test_dry_run_maps_implementation(self):
        import subprocess, sys
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            progress = root / "PROGRESS.md"
            progress.write_text(
                """---
workflow_contract: planning-delegation/v2
project_id: PRJ-001
project_slug: demo
stage: ROUTING
status: IMPLEMENTATION_READY
active_skill: route-ai-work-by-capability
next_skill: implementation
handoff_status: READY
brainstorm_revision: 1
plan_revision: 2
routing_revision: 1
active_artifact: docs/ai/demo/handoffs/ROUTING-TO-IMPLEMENTATION.md
current_task: null
next_action: implement
blockers: []
last_validation: null
updated_at: 2026-07-27T12:00:00-03:00
---

# Progress
""",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "migrate_v2_to_v3.py"), str(root), "--dry-run"],
                capture_output=True,
                text=True,
            )
            joined = completed.stdout + completed.stderr
            self.assertIn("execute-routed-task", joined)


if __name__ == "__main__":
    unittest.main()
