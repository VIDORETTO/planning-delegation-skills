"""Black-box tests for deterministic, atomic workflow initialization."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "init_workflow.py"
FIXTURE = REPO / "tests" / "fixtures" / "workflow-init" / "expected-brainstorm.json"
TIMESTAMP = "2026-07-29T00:00:00Z"


class InitWorkflowTest(unittest.TestCase):
    def run_init(self, root: Path, discovery: str = "brainstorm", *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--project-id", "widget-001", "--project-slug", "widget", "--profile", "standard", "--discovery", discovery, "--timestamp", TIMESTAMP, *extra],
            capture_output=True, text=True, check=False,
        )

    def test_brainstorm_creates_strict_canonical_initial_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_init(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), json.loads(FIXTURE.read_text(encoding="utf-8")))
            workflow = root / "docs" / "ai" / "widget"
            self.assertTrue((workflow / "discovery" / "brainstorm" / "BRAINSTORM.md").is_file())
            self.assertFalse((workflow / "handoffs").exists())
            self.assertIn("status: BRAINSTORM_IN_PROGRESS", (workflow / "PROGRESS.md").read_text(encoding="utf-8"))

    def test_codebase_and_ux_create_only_their_canonical_discovery_files(self) -> None:
        for mode, expected in (("codebase", ("INVESTIGATION.md", "EVIDENCE.md")), ("ux", ("SITEMAP.md", "COVERAGE.md", "UX-AUDIT.md"))):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                result = self.run_init(Path(directory), mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                discovery = Path(directory) / "docs" / "ai" / "widget" / "discovery" / mode
                self.assertEqual(sorted(path.name for path in discovery.iterdir()), sorted(expected))

    def test_dry_run_has_json_contract_and_no_residue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_init(root, "brainstorm", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["dry_run"])
            self.assertFalse((root / "docs").exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_collision_refuses_without_modification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = self.run_init(root)
            progress = root / "docs" / "ai" / "widget" / "PROGRESS.md"
            original = progress.read_bytes()
            second = self.run_init(root)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 1)
            self.assertIn("STV3-E025-SCOPE", second.stderr)
            self.assertEqual(progress.read_bytes(), original)

    def test_path_traversal_and_symlink_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            traversal = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--project-id", "widget-001", "--project-slug", "../outside", "--profile", "standard", "--discovery", "brainstorm"], capture_output=True, text=True, check=False)
            self.assertEqual(traversal.returncode, 1)
            self.assertIn("STV3-E025-SCOPE", traversal.stderr)
            (root / "docs").mkdir()
            target = root / "target"
            target.mkdir()
            try:
                (root / "docs" / "ai").symlink_to(target, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")
            unsafe = self.run_init(root)
            self.assertEqual(unsafe.returncode, 1)
            self.assertIn("STV3-E025-SCOPE", unsafe.stderr)

    def test_windows_style_root_path_is_accepted_when_representable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root_argument = str(root).replace("/", "\\") if sys.platform == "win32" else str(root)
            result = subprocess.run([sys.executable, str(SCRIPT), "--root", root_argument, "--project-id", "widget-001", "--project-slug", "widget", "--profile", "compact", "--discovery", "brainstorm", "--timestamp", TIMESTAMP], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_timestamp_and_cli_usage_leave_no_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = self.run_init(root, "brainstorm", "--timestamp", "not-a-timestamp")
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("STV3-E005-ENUM", invalid.stderr)
            self.assertEqual(list(root.iterdir()), [])
            usage = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
            self.assertEqual(usage.returncode, 2)
            self.assertIn("STV3-E030-INTERNAL", usage.stderr)


if __name__ == "__main__":
    unittest.main()
