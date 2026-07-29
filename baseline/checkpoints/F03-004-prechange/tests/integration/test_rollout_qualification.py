"""Controlled W1-W5 rollout qualification for the strict v3 program."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "tests" / "fixtures" / "rollout-sample"
ROLLOUT = ROOT / "baseline" / "rollout"
MIGRATOR = ROOT / "scripts" / "migrate_v2_to_v3.py"
INITIALIZER = ROOT / "scripts" / "init_workflow.py"


def run(*command: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, env=env)


class RolloutQualificationTest(unittest.TestCase):
    """Every wave uses disposable content; committed artifacts are audit snapshots."""

    def assert_promotion(self, wave: str) -> None:
        promotion = (ROLLOUT / wave / "PROMOTION.md").read_text(encoding="utf-8")
        self.assertIn(f"- Wave: `{wave}`", promotion)
        self.assertIn("- Executor: `openai/gpt-5.6-terra`", promotion)
        self.assertIn("- Independent reviewer: `release-reviewer-01`", promotion)
        self.assertIn("- Decision: `PROMOTE`", promotion)

    def test_w1_shadow(self) -> None:
        original = (SAMPLE / "PROGRESS.md").read_bytes()
        original_hash = hashlib.sha256(original).hexdigest()
        result = run(sys.executable, str(MIGRATOR), str(SAMPLE), "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["dry_run"])
        self.assertEqual(report["migrated_count"], 1)
        self.assertEqual(hashlib.sha256((SAMPLE / "PROGRESS.md").read_bytes()).hexdigest(), original_hash)
        self.assertIn("planning-delegation/v2", (SAMPLE / "PROGRESS.md").read_text(encoding="utf-8"))
        self.assert_promotion("W1")

    def test_w2_migration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            shutil.copytree(SAMPLE, workspace)
            dry_run = run(sys.executable, str(MIGRATOR), str(workspace), "--dry-run", "--json")
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            first = run(sys.executable, str(MIGRATOR), str(workspace), "--json")
            self.assertEqual(first.returncode, 0, first.stderr)
            migrated = (workspace / "PROGRESS.md").read_text(encoding="utf-8")
            self.assertIn("workflow_contract: skill-team/v3", migrated)
            second = run(sys.executable, str(MIGRATOR), str(workspace))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("NO-OP", second.stdout)
            self.assertEqual((workspace / "PROGRESS.md").read_text(encoding="utf-8"), migrated)
        self.assert_promotion("W2")

    def test_w3_specification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            initialized = run(
                sys.executable, str(INITIALIZER), "--root", str(root), "--project-id", "rollout-w3-001",
                "--project-slug", "rollout-w3", "--profile", "compact", "--discovery", "brainstorm",
                "--timestamp", "2026-07-29T00:00:00Z",
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            workflow = root / "docs" / "ai" / "rollout-w3"
            self.assertTrue((workflow / "PROGRESS.md").is_file())
            # Exercise the artifacts on this initializer-created workflow, not standalone capability fixtures.
            shutil.copytree(ROLLOUT / "W3" / "workspace" / "docs" / "ai" / "rollout-w3" / "plan", workflow / "plan")
            shutil.copy2(ROLLOUT / "W3" / "workspace" / "docs" / "ai" / "rollout-w3" / "GOVERNANCE.md", workflow / "GOVERNANCE.md")
            progress = (workflow / "PROGRESS.md").read_text(encoding="utf-8")
            progress = progress.replace("stage: DISCOVERY", "stage: PLANNING").replace("status: BRAINSTORM_IN_PROGRESS", "status: PLAN_IN_PROGRESS")
            progress = progress.replace("stage_owner: brainstorm-idea-with-user", "stage_owner: create-spec-driven-plan").replace("required_skill: brainstorm-idea-with-user", "required_skill: create-spec-driven-plan")
            progress = progress.replace("plan_revision: 0", "plan_revision: 1").replace("writer_skill: brainstorm-idea-with-user", "writer_skill: create-spec-driven-plan")
            (workflow / "PROGRESS.md").write_text(progress, encoding="utf-8")
            planner = ROOT / "skills" / "create-spec-driven-plan" / "scripts" / "validate_plan.py"
            analysis = ROOT / "skills" / "create-spec-driven-plan" / "scripts" / "analyze_plan.py"
            checks = (
                (planner, "--artifact-only", str(workflow)),
                (analysis, str(workflow), "--write"),
                (planner, "--artifact-only", str(workflow)),
            )
            for script, *arguments in checks:
                result = run(sys.executable, str(script), *arguments)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            spec = (workflow / "plan" / "SPEC.md").read_text(encoding="utf-8")
            self.assertIn("## Clarification records", spec)
            self.assertTrue(list((workflow / "plan" / "checklists").glob("*.md")))
            self.assertTrue((workflow / "plan" / "GOVERNANCE-CHECK.md").is_file())
            self.assertTrue((workflow / "plan" / "CONSISTENCY-REPORT.md").is_file())
        self.assert_promotion("W3")

    def test_w4_review(self) -> None:
        result = run(
            sys.executable, "-m", "unittest",
            "tests.integration.test_post_plan_transitions.PostPlanTransitionsTest.test_required_review_path",
            "tests.integration.test_post_plan_transitions.PostPlanTransitionsTest.test_explicitly_waived_review_path",
            "tests.integration.test_post_plan_transitions.PostPlanTransitionsTest.test_return_paths_name_the_correct_owner",
            "tests.integration.test_review_convergence.ReviewConvergenceTest.test_each_gap_type_and_return_owner_validates",
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        cases = (ROLLOUT / "W4" / "workspace" / "CASES.md").read_text(encoding="utf-8")
        for owner in ("create-spec-driven-plan", "execute-routed-task", "investigate-existing-codebase", "route-ai-work-by-capability", "brainstorm-idea-with-user"):
            self.assertIn(owner, cases)
        self.assert_promotion("W4")

    def test_w5_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            shutil.copytree(SAMPLE, workspace)
            self.assertEqual(run(sys.executable, str(MIGRATOR), str(workspace)).returncode, 0)
            backup = next((workspace / ".migration-backup").iterdir())
            qualified_hash = hashlib.sha256((workspace / "PROGRESS.md").read_bytes()).hexdigest()
            self.assertEqual(
                (workspace / "PROGRESS.md").read_bytes(),
                (ROLLOUT / "W5" / "workspace" / "qualified" / "PROGRESS.md").read_bytes(),
            )
            rollback = run(sys.executable, str(MIGRATOR), "--rollback", str(backup))
            self.assertEqual(rollback.returncode, 0, rollback.stderr)
            self.assertIn("restored PROGRESS.md", rollback.stdout)
            self.assertEqual((workspace / "PROGRESS.md").read_bytes(), (SAMPLE / "PROGRESS.md").read_bytes())
            self.assertEqual((SAMPLE / "PROGRESS.md").read_bytes(), (ROLLOUT / "W5" / "workspace" / "checkpoint" / "PROGRESS.md").read_bytes())
            self.assertNotEqual(hashlib.sha256((workspace / "PROGRESS.md").read_bytes()).hexdigest(), qualified_hash)
        # The repository gate runs this test too. Its child invocation is the
        # final validation, so it must not recursively launch another gate.
        if not os.environ.get("SKILL_TEAM_ROLLOUT_GATE"):
            environment = os.environ.copy()
            environment["SKILL_TEAM_ROLLOUT_GATE"] = "1"
            validation = run(sys.executable, "scripts/validate_repository.py", env=environment)
            self.assertEqual(validation.returncode, 0, validation.stderr + validation.stdout)
        self.assert_promotion("W5")


if __name__ == "__main__":
    unittest.main()
