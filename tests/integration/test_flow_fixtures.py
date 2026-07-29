#!/usr/bin/env python3
"""Integration coverage for skill-team/v3 workflow fixtures A–E and invalid cases."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIX = REPO / "tests" / "fixtures"
sys.path.insert(0, str(REPO / "scripts"))
from progress_contract import parse_frontmatter
from workflow_contract import validate_progress


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FlowFixturesTest(unittest.TestCase):
    def test_flow_a_greenfield_ends_at_release_readiness(self):
        text = (FIX / "greenfield-product" / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("required_skill: NONE", text)
        self.assertIn("status: RELEASE_READY", text)
        self.assertEqual(validate_progress(parse_frontmatter(text).data), [])
        chain = (FIX / "greenfield-product" / "CHAIN.md").read_text(encoding="utf-8")
        self.assertIn("brainstorm → plan → route → execute → review → release", chain)

    def test_flow_b_bugfix_omits_brainstorm(self):
        text = (FIX / "existing-code-bug" / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertEqual(validate_progress(parse_frontmatter(text).data), [])

    def test_flow_c_ux_unapproved_not_tasks(self):
        handoff = (FIX / "ux-audit-to-plan" / "handoffs" / "UX-AUDIT-TO-PLAN.md").read_text(encoding="utf-8")
        self.assertIn("APPROVED", handoff)
        self.assertIn("Not approved by product owner", handoff)
        self.assertIn("UX-002", handoff)

    def test_flow_d_scope_change_enters_replan(self):
        text = (FIX / "scope-change" / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("status: REPLAN_REQUIRED", text)
        self.assertIn("required_skill: create-spec-driven-plan", text)

    def test_flow_e_economy_stops_on_architecture(self):
        text = (FIX / "invalid-workflows" / "economy-architecture-stop" / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("status: TASK_BLOCKED", text)
        self.assertIn("Architecture decision required", text)
        blocker = (
            FIX / "invalid-workflows" / "economy-architecture-stop" / "execution" / "blockers" / "F02-003.md"
        ).read_text(encoding="utf-8")
        self.assertIn("stopped", blocker.lower())


class ContractInvalidFixturesTest(unittest.TestCase):
    def test_two_writers_recorded_as_conflict(self):
        text = (FIX / "invalid-workflows" / "two-writers" / "PROGRESS.md").read_text(encoding="utf-8")
        errors = validate_progress(parse_frontmatter(text).data)
        self.assertTrue(any(error.startswith("STV3-E009-WRITER-LOCK") for error in errors), errors)

    def test_stale_revision_blocked(self):
        text = (FIX / "invalid-workflows" / "stale-revision" / "PROGRESS.md").read_text(encoding="utf-8")
        errors = validate_progress(parse_frontmatter(text).data)
        self.assertTrue(any(error.startswith("STV3-E010-REVISION") for error in errors), errors)

    def test_release_failed_gate_not_ready(self):
        progress = (FIX / "invalid-workflows" / "release-with-failed-gate" / "PROGRESS.md").read_text(encoding="utf-8")
        report = (
            FIX / "invalid-workflows" / "release-with-failed-gate" / "release" / "RELEASE-READINESS.md"
        ).read_text(encoding="utf-8")
        self.assertIn("RELEASE_BLOCKED", progress)
        self.assertIn("security | FAIL", report)


class CompactPlanProfileTest(unittest.TestCase):
    def test_compact_fixture_passes_profile_aware_validator(self):
        module = load(
            REPO / "skills" / "create-spec-driven-plan" / "scripts" / "validate_plan.py",
            "validate_plan_fixture",
        )
        # validate_plan expects docs/ai/<slug> layout with parent project root optionally.
        # Our fixture is already the workflow root; copy into a temp docs/ai path.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slug = root / "docs" / "ai" / "compact-plan"
            src = FIX / "compact-plan"
            for path in src.rglob("*"):
                if path.is_file():
                    dest = slug / path.relative_to(src)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "docs/ai/compact-plan/PROGRESS.md\nPROGRESS.md is the operational pointer.\n",
                encoding="utf-8",
            )
            progress = (slug / "PROGRESS.md").read_text(encoding="utf-8")
            progress = progress.replace("stage: RELEASE", "stage: PLANNING").replace("status: RELEASE_READY", "status: PLAN_VALIDATED")
            progress = progress.replace("stage_owner: validate-release-readiness", "stage_owner: create-spec-driven-plan").replace("required_skill: NONE", "required_skill: route-ai-work-by-capability", 1)
            progress = progress.replace("successor_skill: NONE", "successor_skill: execute-routed-task").replace("routing_revision: 1", "routing_revision: 0").replace("implementation_revision: 1", "implementation_revision: 0").replace("review_revision: 1", "review_revision: 0").replace("release_revision: 1", "release_revision: 0")
            progress = progress.replace("active_artifact: docs/ai/compact-plan/release/RELEASE-READINESS.md", "active_artifact: docs/ai/compact-plan/handoffs/PLAN-TO-ROUTING.md")
            progress = progress.replace("handoff_status: CONSUMED", "handoff_status: READY")
            (slug / "PROGRESS.md").write_text(progress, encoding="utf-8")
            old_argv = sys.argv[:]
            try:
                sys.argv = ["validate_plan.py", str(slug)]
                result, code = module.validate()
            finally:
                sys.argv = old_argv
            self.assertEqual(code, 0, msg="\n".join(result["errors"]))
            self.assertEqual(result["errors"], [])

    def test_compact_fixture_proves_the_canonical_routing_to_release_chain(self):
        validators = {
            "routing": load(REPO / "skills" / "route-ai-work-by-capability" / "scripts" / "validate_routing.py", "compact_routing"),
            "execution": load(REPO / "skills" / "execute-routed-task" / "scripts" / "validate_execution.py", "compact_execution"),
            "review": load(REPO / "skills" / "review-implementation-evidence" / "scripts" / "validate_review.py", "compact_review"),
            "release": load(REPO / "skills" / "validate-release-readiness" / "scripts" / "validate_release.py", "compact_release"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / "compact-plan"
            shutil.copytree(FIX / "compact-plan", workflow)
            self.assertTrue((workflow / "handoffs" / "ROUTING-TO-IMPLEMENTATION.md").is_file())
            self.assertTrue((workflow / "handoffs" / "IMPLEMENTATION-TO-REVIEW.md").is_file())
            self.assertTrue((workflow / "handoffs" / "REVIEW-TO-RELEASE.md").is_file())
            self.assertTrue((workflow / "release" / "RELEASE-READINESS.md").is_file())

            def set_progress(**fields: str) -> None:
                path = workflow / "PROGRESS.md"
                lines = path.read_text(encoding="utf-8").splitlines()
                path.write_text("\n".join(
                    f"{key}: {fields[key]}" if key in fields else line
                    for line in lines
                    for key in [line.split(":", 1)[0]]
                ) + "\n", encoding="utf-8")

            set_progress(stage="ROUTING", status="IMPLEMENTATION_READY", stage_owner="route-ai-work-by-capability", required_skill="execute-routed-task", successor_skill="execute-routed-task", handoff_status="READY", active_artifact="handoffs/ROUTING-TO-IMPLEMENTATION.md")
            self.assertEqual(validators["routing"].validate_workflow(workflow), 0)
            set_progress(stage="IMPLEMENTATION", status="IMPLEMENTATION_COMPLETE", stage_owner="execute-routed-task", required_skill="review-implementation-evidence", successor_skill="review-implementation-evidence", handoff_status="READY", active_artifact="handoffs/IMPLEMENTATION-TO-REVIEW.md")
            self.assertEqual(validators["execution"].main([str(workflow)]), 0)
            (workflow / "handoffs" / "REVIEW-TO-RELEASE.md").rename(workflow / "handoffs" / "REVIEW-TO-RELEASE.pending")
            set_progress(stage="REVIEW", status="REVIEW_REQUIRED", stage_owner="review-implementation-evidence", required_skill="review-implementation-evidence", successor_skill="validate-release-readiness", handoff_status="READY", active_artifact="handoffs/IMPLEMENTATION-TO-REVIEW.md")
            self.assertEqual(validators["review"].main([str(workflow)]), 0)
            (workflow / "handoffs" / "REVIEW-TO-RELEASE.pending").rename(workflow / "handoffs" / "REVIEW-TO-RELEASE.md")
            set_progress(stage="RELEASE", status="RELEASE_REVIEW_REQUIRED", stage_owner="validate-release-readiness", required_skill="validate-release-readiness", successor_skill="NONE", handoff_status="READY", active_artifact="handoffs/REVIEW-TO-RELEASE.md")
            self.assertEqual(validators["release"].main([str(workflow)]), 0)


class RoutingDependenciesRegressionTest(unittest.TestCase):
    def test_section_dependencies_still_parsed(self):
        module = load(
            REPO / "skills" / "route-ai-work-by-capability" / "scripts" / "validate_routing.py",
            "validate_routing_fixture",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            phase = root / "phases"
            phase.mkdir()
            (phase / "F01.md").write_text(
                """# F01

### [ ] F01-001 — A

Executor: MODEL-A
Reviewer: NONE

#### Dependencies

- NONE

### [ ] F01-002 — B

Executor: MODEL-A
Reviewer: NONE

#### Dependencies

- F01-001
""",
                encoding="utf-8",
            )
            tasks = {t.task_id: t for t in module.parse_tasks(root)}
            self.assertEqual(tasks["F01-002"].dependencies, ["F01-001"])


if __name__ == "__main__":
    unittest.main()
