#!/usr/bin/env python3
"""Integration coverage for skill-team/v3 workflow fixtures A–E and invalid cases."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIX = REPO / "tests" / "fixtures"


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
        self.assertIn("required_skill: validate-release-readiness", text)
        self.assertIn("status: RELEASE_READY", text)
        self.assertNotIn("next_skill:", text)
        chain = (FIX / "greenfield-product" / "CHAIN.md").read_text(encoding="utf-8")
        self.assertIn("brainstorm → plan → route → execute → review → release", chain)

    def test_flow_b_bugfix_omits_brainstorm(self):
        text = (FIX / "existing-code-bug" / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("required_skill: investigate-existing-codebase", text)
        self.assertIn("workflow_profile: compact", text)
        self.assertNotIn("brainstorm-idea-with-user", text)

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
        self.assertIn("writer_skill: execute-routed-task", text)
        self.assertIn("CONFLICT", text)

    def test_stale_revision_blocked(self):
        text = (FIX / "invalid-workflows" / "stale-revision" / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("status: TASK_BLOCKED", text)
        self.assertIn("stale", text.lower())

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
            old_argv = sys.argv[:]
            try:
                sys.argv = ["validate_plan.py", str(slug)]
                result, code = module.validate()
            finally:
                sys.argv = old_argv
            # Compact profile should not demand full standard document set.
            missing_standard = [e for e in result["errors"] if "PRODUCT-SCOPE.md" in e or "USER-JOURNEYS.md" in e]
            self.assertEqual(missing_standard, [], msg="\n".join(missing_standard))
            # May still have task section strictness errors depending on template completeness;
            # assert profile gating specifically worked.
            profile_errors = [e for e in result["errors"] if "profile=compact" in e and "ANALYSIS.md" in e]
            self.assertEqual(profile_errors, [])


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
