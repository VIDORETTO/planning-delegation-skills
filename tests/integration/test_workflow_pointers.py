#!/usr/bin/env python3
"""Integration skeleton: workflow pointer transitions for skill-team/v3."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def write_progress(path: Path, **fields: str) -> None:
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {value}")
    lines.extend(["---", "", "# Progress", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


class WorkflowPointerIntegrationTest(unittest.TestCase):
    def test_greenfield_required_skill_chain(self):
        chain = [
            ("DISCOVERY", "BRAINSTORM_IN_PROGRESS", "brainstorm-idea-with-user", "create-spec-driven-plan"),
            ("DISCOVERY", "DISCOVERY_READY", "create-spec-driven-plan", "route-ai-work-by-capability"),
            ("PLANNING", "PLAN_VALIDATED", "route-ai-work-by-capability", "execute-routed-task"),
            ("ROUTING", "IMPLEMENTATION_READY", "execute-routed-task", "review-implementation-evidence"),
            ("REVIEW", "REVIEW_APPROVED", "validate-release-readiness", "validate-release-readiness"),
            ("RELEASE", "RELEASE_READY", "validate-release-readiness", "null"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            progress = Path(tmp) / "PROGRESS.md"
            for stage, status, required, successor in chain:
                write_progress(
                    progress,
                    workflow_contract="skill-team/v3",
                    project_id="PRJ-001",
                    project_slug="greenfield",
                    workflow_profile="standard",
                    stage=stage,
                    status=status,
                    stage_owner=required,
                    required_skill=required,
                    successor_skill=successor,
                    handoff_status="READY",
                    discovery_revision="1",
                    plan_revision="1",
                    routing_revision="1",
                    implementation_revision="1",
                    review_revision="1",
                    release_revision="1",
                    active_artifact="docs/ai/greenfield/PROGRESS.md",
                    writer_skill="null",
                    next_action="continue",
                    blockers="NONE",
                    last_validation_command="NONE",
                    last_validation_result="PASS",
                    updated_at="2026-07-27T12:00:00-03:00",
                )
                text = progress.read_text(encoding="utf-8")
                self.assertIn("required_skill:", text)
                self.assertNotIn("next_skill:", text)

    def test_bugfix_skips_brainstorm(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress = Path(tmp) / "PROGRESS.md"
            write_progress(
                progress,
                workflow_contract="skill-team/v3",
                project_id="PRJ-002",
                project_slug="bugfix",
                workflow_profile="compact",
                stage="DISCOVERY",
                status="CODEBASE_INVESTIGATION_IN_PROGRESS",
                stage_owner="investigate-existing-codebase",
                required_skill="investigate-existing-codebase",
                successor_skill="create-spec-driven-plan",
                handoff_status="NOT_READY",
                discovery_revision="1",
                plan_revision="0",
                routing_revision="0",
                implementation_revision="0",
                review_revision="0",
                release_revision="0",
                active_artifact="docs/ai/bugfix/discovery/codebase/INVESTIGATION.md",
                writer_skill="investigate-existing-codebase",
                next_action="Collect root-cause evidence",
                blockers="NONE",
                last_validation_command="NONE",
                last_validation_result="NOT_RUN",
                updated_at="2026-07-27T12:00:00-03:00",
            )
            text = progress.read_text(encoding="utf-8")
            self.assertIn("investigate-existing-codebase", text)
            self.assertNotIn("brainstorm-idea-with-user", text.split("required_skill:", 1)[1].splitlines()[0])


if __name__ == "__main__":
    unittest.main()
