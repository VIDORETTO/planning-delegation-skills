"""Regression tests for the repository-wide strict workflow gate."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from progress_contract import parse_frontmatter
from workflow_contract import validate_progress


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class RepositoryContractGateTest(unittest.TestCase):
    def test_canonical_templates_are_instantiated_and_validated(self):
        validator = load_module(REPO / "scripts" / "validate_repository.py", "repository_gate_templates")
        result = validator.step_canonical_template_instances(REPO)
        self.assertTrue(result.ok, "\n".join(result.details))
        self.assertEqual(len(result.details), 9)

    def test_catalog_path_drift_is_rejected(self):
        validator = load_module(REPO / "scripts" / "validate_catalog.py", "catalog_gate")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(REPO / "catalog", root / "catalog")
            shutil.copytree(REPO / "skills", root / "skills")
            catalog_path = root / "catalog" / "skills.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["skills"][1]["produces"][0] = "docs/ai/<slug>/discovery/investigation/CODEBASE-INVESTIGATION.md"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            errors, _meta = validator.validate(root)
        self.assertTrue(any("produces must match canonical paths" in error for error in errors), errors)

    def test_valid_and_invalid_workflow_fixtures_have_strict_outcomes(self):
        fixtures = REPO / "tests" / "fixtures"
        for name in ("greenfield-product", "existing-code-bug", "ux-audit-to-plan", "compact-plan"):
            with self.subTest(valid=name):
                data = parse_frontmatter((fixtures / name / "PROGRESS.md").read_text(encoding="utf-8")).data
                self.assertEqual(validate_progress(data), [])
        expected = {
            "two-writers": "STV3-E009-WRITER-LOCK",
            "stale-revision": "STV3-E010-REVISION",
            "legacy-alias": "STV3-E001-CONTRACT",
        }
        for name, error_code in expected.items():
            with self.subTest(invalid=name):
                data = parse_frontmatter(
                    (fixtures / "invalid-workflows" / name / "PROGRESS.md").read_text(encoding="utf-8")
                ).data
                self.assertTrue(any(error.startswith(error_code) for error in validate_progress(data)))
        validator = load_module(REPO / "scripts" / "validate_repository.py", "repository_gate_fixtures")
        result = validator.step_workflow_fixtures(REPO)
        self.assertTrue(result.ok, "\n".join(result.details))
        self.assertIn(
            "rejected invalid fixture placeholder-handoff: STV3-E012-HANDOFF-CONTRACT",
            result.details,
        )


if __name__ == "__main__":
    unittest.main()
