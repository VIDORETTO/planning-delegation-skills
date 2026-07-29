"""Controlled W1-W5 rollout qualification for the strict v3 program."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
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
    """Execute each wave in its persisted rollout workspace."""

    @staticmethod
    def reset_workspace(wave: str, source: Path = SAMPLE) -> Path:
        workspace = ROLLOUT / wave / "workspace"
        if workspace.exists():
            shutil.rmtree(workspace)
        shutil.copytree(source, workspace)
        return workspace

    @staticmethod
    def load_module(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    def assert_promotion(self, wave: str) -> None:
        promotion = (ROLLOUT / wave / "PROMOTION.md").read_text(encoding="utf-8")
        self.assertIn(f"- Wave: `{wave}`", promotion)
        self.assertIn("- Executor: `openai/gpt-5.6-terra`", promotion)
        self.assertIn("- Independent reviewer: `release-reviewer-01`", promotion)
        self.assertIn("- Decision: `PROMOTE`", promotion)

    def test_w1_shadow(self) -> None:
        workspace = self.reset_workspace("W1")
        original = (workspace / "PROGRESS.md").read_bytes()
        original_hash = hashlib.sha256(original).hexdigest()
        result = run(sys.executable, str(MIGRATOR), str(workspace), "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["dry_run"])
        self.assertEqual(report["migrated_count"], 1)
        self.assertEqual(hashlib.sha256((workspace / "PROGRESS.md").read_bytes()).hexdigest(), original_hash)
        self.assertIn("planning-delegation/v2", (workspace / "PROGRESS.md").read_text(encoding="utf-8"))
        self.assert_promotion("W1")

    def test_w2_migration(self) -> None:
        workspace = self.reset_workspace("W2")
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
        root = ROLLOUT / "W3" / "workspace"
        source = root / "docs" / "ai" / "rollout-w3"
        seed = root / ".artifact-seed"
        if seed.exists():
            shutil.rmtree(seed)
        shutil.copytree(source, seed)
        shutil.rmtree(root / "docs")
        initialized = run(
            sys.executable, str(INITIALIZER), "--root", str(root), "--project-id", "rollout-w3-001",
            "--project-slug", "rollout-w3", "--profile", "compact", "--discovery", "brainstorm",
            "--timestamp", "2026-07-29T00:00:00Z",
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        workflow = root / "docs" / "ai" / "rollout-w3"
        self.assertTrue((workflow / "PROGRESS.md").is_file())
        # Install the W3 qualification artifacts on the workflow created above.
        shutil.copytree(seed / "plan", workflow / "plan")
        shutil.copytree(seed / "discovery", workflow / "discovery", dirs_exist_ok=True)
        shutil.copy2(seed / "GOVERNANCE.md", workflow / "GOVERNANCE.md")
        progress = (workflow / "PROGRESS.md").read_text(encoding="utf-8")
        progress = progress.replace("stage: DISCOVERY", "stage: PLANNING").replace("status: BRAINSTORM_IN_PROGRESS", "status: PLAN_IN_PROGRESS")
        progress = progress.replace("stage_owner: brainstorm-idea-with-user", "stage_owner: create-spec-driven-plan").replace("required_skill: brainstorm-idea-with-user", "required_skill: create-spec-driven-plan")
        progress = progress.replace("plan_revision: 0", "plan_revision: 1").replace("writer_skill: brainstorm-idea-with-user", "writer_skill: create-spec-driven-plan")
        (workflow / "PROGRESS.md").write_text(progress, encoding="utf-8")
        planner = ROOT / "skills" / "create-spec-driven-plan" / "scripts" / "validate_plan.py"
        analysis = ROOT / "skills" / "create-spec-driven-plan" / "scripts" / "analyze_plan.py"
        for script, *arguments in ((planner, "--artifact-only", str(workflow)), (analysis, str(workflow), "--write"), (planner, "--artifact-only", str(workflow))):
            result = run(sys.executable, str(script), *arguments)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        spec = (workflow / "plan" / "SPEC.md").read_text(encoding="utf-8")
        self.assertIn("## Clarification records", spec)
        self.assertTrue(list((workflow / "plan" / "checklists").glob("*.md")))
        self.assertTrue((workflow / "plan" / "GOVERNANCE-CHECK.md").is_file())
        self.assertTrue((workflow / "plan" / "CONSISTENCY-REPORT.md").is_file())
        self.assert_promotion("W3")

    def test_w4_review(self) -> None:
        workspace = ROLLOUT / "W4" / "workspace"
        cases = workspace / "CASES.md"
        post_plan = self.load_module("rollout_post_plan", ROOT / "tests" / "integration" / "test_post_plan_transitions.py")
        transition = post_plan.PostPlanTransitionsTest()
        transition.modules = {name: post_plan.load(name) for name in post_plan.SCRIPTS}
        review_cases = (("required-review", "review"), ("required-review", "release"), ("waived-review", "execution"), ("waived-review", "release"))
        for index, (scenario, validator) in enumerate(review_cases):
            target = workspace / "policies" / f"{index}-{scenario}-{validator}"
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(post_plan.FIXTURES / scenario, target)
            transition.build_workflow(target, scenario, validator)
            self.assertEqual(transition.modules[validator].main([str(target)]), 0, str(target))
        for scenario in ("reroute", "replan", "investigation", "intent-return"):
            target = workspace / "returns" / scenario
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(post_plan.FIXTURES / scenario, target)
            transition.build_workflow(target, scenario, "execution")
            self.assertEqual(transition.modules["execution"].main([str(target)]), 0, str(target))
        convergence = self.load_module("rollout_review_convergence", ROOT / "tests" / "integration" / "test_review_convergence.py")
        review = convergence.ReviewConvergenceTest()
        review.validator = convergence.load_validator()
        for name in ("missing-to-plan", "partial-to-implementation", "contradicts-to-investigation", "unrequested-to-routing", "intent-to-brainstorm"):
            target = workspace / "convergence" / name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(convergence.FIXTURES / name, target)
            review.materialize(target)
            self.assertEqual(review.validator.main([str(target)]), 0, str(target))
        cases = cases.read_text(encoding="utf-8")
        for owner in ("create-spec-driven-plan", "execute-routed-task", "investigate-existing-codebase", "route-ai-work-by-capability", "brainstorm-idea-with-user"):
            self.assertIn(owner, cases)
        self.assert_promotion("W4")

    def test_w5_release(self) -> None:
        root = ROLLOUT / "W5" / "workspace"
        for name in ("run", "qualified", "checkpoint"):
            target = root / name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(SAMPLE, target)
        workspace = root / "run"
        self.assertEqual(run(sys.executable, str(MIGRATOR), str(workspace)).returncode, 0)
        backup = next((workspace / ".migration-backup").iterdir())
        qualified_hash = hashlib.sha256((workspace / "PROGRESS.md").read_bytes()).hexdigest()
        shutil.copy2(workspace / "PROGRESS.md", root / "qualified" / "PROGRESS.md")
        self.assertEqual((workspace / "PROGRESS.md").read_bytes(), (root / "qualified" / "PROGRESS.md").read_bytes())
        rollback = run(sys.executable, str(MIGRATOR), "--rollback", str(backup))
        self.assertEqual(rollback.returncode, 0, rollback.stderr)
        self.assertIn("restored PROGRESS.md", rollback.stdout)
        self.assertEqual((workspace / "PROGRESS.md").read_bytes(), (root / "checkpoint" / "PROGRESS.md").read_bytes())
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
