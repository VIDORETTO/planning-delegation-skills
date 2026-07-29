"""Canonical templates must expose the strict v3 fields and handoff sections."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFFS = (
    "skills/brainstorm-idea-with-user/assets/BRAINSTORM-TO-PLAN.template.md",
    "skills/investigate-existing-codebase/assets/CODEBASE-TO-PLAN.template.md",
    "skills/product-ux-audit/assets/UX-AUDIT-TO-PLAN.template.md",
    "skills/create-spec-driven-plan/assets/PLAN-TO-ROUTING.template.md",
    "skills/route-ai-work-by-capability/assets/ROUTING-TO-IMPLEMENTATION.template.md",
    "skills/execute-routed-task/assets/IMPLEMENTATION-TO-REVIEW.template.md",
    "skills/execute-routed-task/assets/IMPLEMENTATION-TO-RELEASE.template.md",
)
SECTIONS = ("Identification", "Summary", "Artifact inventory", "Preserved decisions", "Allowed open questions", "Blockers", "Consumer write scope", "Forbidden files", "Commands and results", "Stop instruction")

class CanonicalTemplatesTest(unittest.TestCase):
    def test_planning_progress_uses_only_canonical_fields(self):
        text = (ROOT / "skills/create-spec-driven-plan/assets/PROGRESS.template.md").read_text()
        self.assertIn("stage: PLANNING", text)
        self.assertIn("discovery_revision:", text)
        self.assertIn("active_task:", text)
        self.assertNotIn("brainstorm_revision:", text)
        self.assertNotIn("current_task:", text)

    def test_handoffs_have_strict_frontmatter_and_required_body(self):
        for relative in HANDOFFS:
            with self.subTest(template=relative):
                text = (ROOT / relative).read_text()
                self.assertIn("workflow_contract: skill-team/v3", text)
                self.assertIn("handoff_type:", text)
                self.assertIn("validation_result:", text)
                for section in SECTIONS:
                    self.assertIn(f"## {section}", text)
