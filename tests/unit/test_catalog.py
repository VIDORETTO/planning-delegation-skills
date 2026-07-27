#!/usr/bin/env python3
"""Smoke tests for catalog/skills.json and scripts/validate_catalog.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VALIDATE_CATALOG_SCRIPT = REPO / "scripts" / "validate_catalog.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class CatalogFilesTest(unittest.TestCase):
    def test_skills_json_is_well_formed(self) -> None:
        data = json.loads((REPO / "catalog" / "skills.json").read_text(encoding="utf-8"))
        self.assertEqual(data.get("schema_version"), 1)
        self.assertIsInstance(data.get("skills"), list)
        self.assertGreaterEqual(len(data["skills"]), 9)

    def test_skills_json_names_are_unique(self) -> None:
        data = json.loads((REPO / "catalog" / "skills.json").read_text(encoding="utf-8"))
        names = [entry["name"] for entry in data["skills"]]
        self.assertEqual(len(names), len(set(names)))

    def test_advisor_planner_excluded_from_active_catalog(self) -> None:
        data = json.loads((REPO / "catalog" / "skills.json").read_text(encoding="utf-8"))
        names = {entry["name"] for entry in data["skills"]}
        self.assertNotIn("advisor-planner", names)

    def test_advisor_planner_noted_as_absorbed_in_compatibility(self) -> None:
        data = json.loads((REPO / "catalog" / "compatibility.json").read_text(encoding="utf-8"))
        legacy_names = {entry["name"] for entry in data.get("legacy_skills", [])}
        self.assertIn("advisor-planner", legacy_names)

    def test_categories_json_covers_every_skill_category(self) -> None:
        skills = json.loads((REPO / "catalog" / "skills.json").read_text(encoding="utf-8"))
        categories = json.loads((REPO / "catalog" / "categories.json").read_text(encoding="utf-8"))
        cats = categories.get("categories", [])
        if isinstance(cats, dict):
            known_categories = set(cats.keys())
        else:
            known_categories = {item["id"] if isinstance(item, dict) else item for item in cats}
        used_categories = {entry["category"] for entry in skills["skills"]}
        self.assertTrue(used_categories.issubset(known_categories), used_categories - known_categories)

    def test_every_entry_has_required_fields(self) -> None:
        data = json.loads((REPO / "catalog" / "skills.json").read_text(encoding="utf-8"))
        required = {"name", "category", "status", "workflow_contracts", "accepts", "produces", "standalone", "platform_neutral"}
        for entry in data["skills"]:
            with self.subTest(skill=entry.get("name")):
                self.assertTrue(required.issubset(entry.keys()))
                self.assertIn("skill-team/v3", entry["workflow_contracts"])


class ValidateCatalogScriptTest(unittest.TestCase):
    """Exercises validate_catalog.validate() against a small, isolated fixture
    repo, so this smoke test stays deterministic regardless of the live
    skills/ tree's ongoing content (which other work may still be editing).
    """

    def _build_fixture_repo(self, tmp_path: Path) -> None:
        (tmp_path / "catalog").mkdir()
        (tmp_path / "catalog" / "skills.json").write_text(json.dumps({
            "schema_version": 1,
            "skills": [
                {
                    "name": "sample-skill",
                    "category": "discovery",
                    "status": "stable",
                    "workflow_contracts": ["skill-team/v3"],
                    "accepts": ["x"],
                    "produces": ["y"],
                    "standalone": True,
                    "platform_neutral": True,
                },
            ],
        }), encoding="utf-8")
        (tmp_path / "catalog" / "categories.json").write_text(json.dumps({
            "schema_version": 1,
            "categories": {"discovery": "Understand before planning."},
        }), encoding="utf-8")
        skill_dir = tmp_path / "skills" / "sample-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: sample-skill\ndescription: A sample.\n---\n\n# Sample\n",
            encoding="utf-8",
        )

    def test_valid_fixture_reports_no_errors(self) -> None:
        module = load_module(VALIDATE_CATALOG_SCRIPT, "validate_catalog")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._build_fixture_repo(tmp_path)
            errors, meta = module.validate(tmp_path)
            self.assertEqual(errors, [], msg="\n".join(errors))
            self.assertEqual(meta.get("skill_count"), 1)

    def test_unregistered_skill_folder_is_flagged(self) -> None:
        module = load_module(VALIDATE_CATALOG_SCRIPT, "validate_catalog")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._build_fixture_repo(tmp_path)
            stray = tmp_path / "skills" / "stray-skill"
            stray.mkdir(parents=True)
            (stray / "SKILL.md").write_text(
                "---\nname: stray-skill\ndescription: Not registered.\n---\n\n# Stray\n",
                encoding="utf-8",
            )
            errors, _meta = module.validate(tmp_path)
            self.assertTrue(any("stray-skill" in error for error in errors))

    def test_live_catalog_is_internally_consistent(self) -> None:
        """A lighter-weight live-repo check: the catalog itself must always
        validate cleanly against its own declared entries and folders, even
        while unrelated skill content elsewhere in the repo is in flux.
        """

        module = load_module(VALIDATE_CATALOG_SCRIPT, "validate_catalog")
        errors, meta = module.validate(REPO)
        unexpected = [e for e in errors if "catalog/skills.json" in e or "catalog/categories.json" in e]
        self.assertEqual(unexpected, [], msg="\n".join(unexpected))
        self.assertGreaterEqual(meta.get("skill_count", 0), 9)


if __name__ == "__main__":
    unittest.main()
