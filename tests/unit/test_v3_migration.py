from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "migrate_v2_to_v3.py"
FIXTURES = ROOT / "tests" / "fixtures" / "migration"


def run_migrator(target: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class V3MigrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "workflow"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def fixture(self, name: str) -> Path:
        shutil.copy(FIXTURES / name / "PROGRESS.md", self.root / "PROGRESS.md")
        return self.root / "PROGRESS.md"

    def test_dry_run_emits_hash_and_revision_manifest_without_changes(self) -> None:
        progress = self.fixture("valid")
        original = progress.read_text(encoding="utf-8")
        result = run_migrator(self.root, "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        entry = report["manifest"]["files"][0]
        self.assertTrue(entry["source_sha256"])
        self.assertEqual(entry["source_revisions"]["brainstorm_revision"], "2")
        self.assertEqual(progress.read_text(encoding="utf-8"), original)
        self.assertFalse((self.root / ".migration-backup").exists())

    def test_migration_is_strict_and_second_run_is_a_noop(self) -> None:
        progress = self.fixture("valid")
        first = run_migrator(self.root, "--json")
        self.assertEqual(first.returncode, 0, first.stderr)
        text = progress.read_text(encoding="utf-8")
        self.assertIn("workflow_contract: skill-team/v3", text)
        self.assertNotIn("next_skill:", text)
        second = run_migrator(self.root)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("NO-OP", second.stdout)
        self.assertEqual(progress.read_text(encoding="utf-8"), text)

    def test_unknown_state_and_active_writer_refuse_without_writes(self) -> None:
        for fixture in ("unknown-state", "writer-lock"):
            with self.subTest(fixture=fixture):
                progress = self.fixture(fixture)
                original = progress.read_text(encoding="utf-8")
                result = run_migrator(self.root)
                self.assertEqual(result.returncode, 1)
                self.assertIn("MIGRATION REFUSED", result.stderr)
                self.assertEqual(progress.read_text(encoding="utf-8"), original)

    def test_alias_collision_refuses_without_writes(self) -> None:
        progress = self.fixture("valid")
        text = progress.read_text(encoding="utf-8").replace(
            "active_skill: brainstorm-idea-with-user", "active_skill: brainstorm-idea-with-user\nstage_owner: advisor-planner"
        )
        progress.write_text(text, encoding="utf-8")
        result = run_migrator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("conflicting aliases", result.stderr)

    def test_hash_safe_rollback_preserves_user_changes(self) -> None:
        progress = self.fixture("valid")
        self.assertEqual(run_migrator(self.root).returncode, 0)
        backup = next((self.root / ".migration-backup").iterdir())
        progress.write_text(progress.read_text(encoding="utf-8") + "\nUser change.\n", encoding="utf-8")
        rollback = subprocess.run(
            [sys.executable, str(SCRIPT), "--rollback", str(backup)], cwd=ROOT, text=True, capture_output=True, check=False
        )
        self.assertEqual(rollback.returncode, 0, rollback.stderr)
        self.assertIn("preserved PROGRESS.md", rollback.stdout)
        self.assertIn("User change.", progress.read_text(encoding="utf-8"))

    def test_non_pointer_user_artifacts_are_preserved(self) -> None:
        self.fixture("valid")
        artifact = self.root / "handoffs" / "legacy-notes.md"
        artifact.parent.mkdir()
        artifact.write_text("User-authored legacy material.\n", encoding="utf-8")
        self.assertEqual(run_migrator(self.root).returncode, 0)
        self.assertEqual(artifact.read_text(encoding="utf-8"), "User-authored legacy material.\n")

    def test_interrupted_write_keeps_recovery_manifest(self) -> None:
        self.fixture("valid")
        spec = importlib.util.spec_from_file_location("migration_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        with patch.object(sys, "argv", [str(SCRIPT), str(self.root)]), patch.object(Path, "replace", side_effect=OSError("interrupted")):
            self.assertEqual(module.main(), 2)
        backup = next((self.root / ".migration-backup").iterdir())
        self.assertTrue((backup / "MANIFEST.json").is_file())
        self.assertTrue((backup / "originals" / "PROGRESS.md").is_file())


if __name__ == "__main__":
    unittest.main()
