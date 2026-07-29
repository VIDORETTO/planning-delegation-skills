#!/usr/bin/env python3
"""Reproduce known false-green contract gaps that pass repository validation but
represent real v3 violations. These tests demonstrate defects visible at baseline
that repository validation does not currently catch.

Gap 1: v2 contract alias still accepted by stage validators.
Gap 2: Obsolete stage/status vocabulary (BRAINSTORM, BRAINSTORM_READY) accepted.
Gap 3: Template-style PROGRESS with legacy fields passes one validator path
       (or the planning validator) but fails the shared contract validator.
"""

from __future__ import annotations

import importlib.util
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIX = REPO / "tests" / "fixtures" / "known-contract-gaps"


def _load_module(script_path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Gap 1 — v2 contract alias acceptance
# ---------------------------------------------------------------------------

class Gap1V2ContractAliasTest(unittest.TestCase):
    """DEF-002 / DEF-003: Stage validators accept planning-delegation/v2."""

    @classmethod
    def setUpClass(cls):
        cls._progress_contract = _load_module(
            REPO / "scripts" / "progress_contract.py", "gap1_progress"
        )
        cls._validate_plan = _load_module(
            REPO / "skills" / "create-spec-driven-plan" / "scripts" / "validate_plan.py",
            "gap1_plan",
        )
        cls._validate_brainstorm = _load_module(
            REPO / "skills" / "brainstorm-idea-with-user" / "scripts" / "validate_brainstorm.py",
            "gap1_brainstorm",
        )

    def test_shared_contract_rejects_v2(self):
        """progress_contract.py correctly rejects v2 — baseline good behavior."""
        fixture = FIX / "v2-alias-acceptance" / "PROGRESS.md"
        result = self._progress_contract.load_frontmatter(fixture)
        errors = self._progress_contract.validate_progress_fields(result.data)
        self.assertTrue(
            any("workflow_contract" in e for e in errors),
            f"Shared contract must flag v2: {errors}",
        )

    def test_plan_validator_rejects_v2(self):
        """Regression: validate_plan.py rejects planning-delegation/v2.

        The planning validator checks workflow_contract against
        {"skill-team/v3", "planning-delegation/v2"} at line 215, which
        constitutes a false-green pass for v2 artifacts.
        """

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slug = root / "docs" / "ai" / "v2-gap-plan"
            src = FIX / "v2-alias-acceptance"
            for path in src.rglob("*"):
                if path.is_file():
                    dest = slug / path.relative_to(src)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "docs/ai/v2-gap-plan/PROGRESS.md\n", encoding="utf-8"
            )

            old_argv = sys.argv[:]
            try:
                sys.argv = ["validate_plan.py", str(slug)]
                result, code = self._validate_plan.validate()
            finally:
                sys.argv = old_argv

            contract_errors = [
                e for e in result["errors"] if "unsupported workflow_contract" in e
            ]
            self.assertTrue(contract_errors)

    def test_brainstorm_validator_rejects_v2(self):
        """BUG: validate_brainstorm.py allows planning-delegation/v2.

        The brainstorm validator checks workflow_contract against
        {CONTRACT, LEGACY_CONTRACT} where LEGACY_CONTRACT = "planning-delegation/v2"
        at line 198, which is a false-green pass.
        """

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slug = root / "docs" / "ai" / "v2-gap-bs"
            src = FIX / "v2-alias-acceptance"
            for path in src.rglob("*"):
                if path.is_file():
                    dest = slug / path.relative_to(src)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "docs/ai/v2-gap-bs/PROGRESS.md\n", encoding="utf-8"
            )

            old_stderr = sys.stderr
            captured = io.StringIO()
            try:
                sys.stderr = captured
                old_argv = sys.argv[:]
                sys.argv = [
                    "validate_brainstorm.py",
                    str(slug),
                    "--allow-in-progress",
                    "--artifact-only",
                ]
                code = self._validate_brainstorm.main()
            finally:
                sys.argv = old_argv
                sys.stderr = old_stderr

            self.assertNotEqual(
                code,
                0,
                "Brainstorm validator must reject a v2 artifact.",
            )


# ---------------------------------------------------------------------------
# Gap 2 — Obsolete stage/status acceptance
# ---------------------------------------------------------------------------

class Gap2ObsoleteStatusTest(unittest.TestCase):
    """DEF-001/DEF-015: Validators accept obsolete stage and status vocabulary."""

    @classmethod
    def setUpClass(cls):
        cls._progress_contract = _load_module(
            REPO / "scripts" / "progress_contract.py", "gap2_progress"
        )

    def test_shared_contract_rejects_obsolete_stage(self):
        """The shared contract correctly rejects BRAINSTORM as a stage."""
        fixture = FIX / "obsolete-status-acceptance" / "PROGRESS.md"
        result = self._progress_contract.load_frontmatter(fixture)
        errors = self._progress_contract.validate_progress_fields(result.data)
        self.assertTrue(
            any("stage" in e and "BRAINSTORM" in e for e in errors),
            f"BRAINSTORM stage must be rejected: {errors}",
        )

    def test_brainstorm_validator_rejects_obsolete_statuses(self):
        """BUG: validate_brainstorm.py accepts BRAINSTORM_READY and REBRAINSTORM_REQUIRED.

        The ALLOWED_STATUSES set (line 17-19) includes BRAINSTORM_READY
        which should be DISCOVERY_READY per the canonical v3 contract.
        It also includes REBRAINSTORM_REQUIRED which is not in the contract.
        """
        validate_brainstorm = _load_module(
            REPO / "skills" / "brainstorm-idea-with-user" / "scripts" / "validate_brainstorm.py",
            "gap2_brainstorm",
        )
        self.assertNotIn("BRAINSTORM_READY", validate_brainstorm.ALLOWED_STATUSES)
        self.assertNotIn("REBRAINSTORM_REQUIRED", validate_brainstorm.ALLOWED_STATUSES)


# ---------------------------------------------------------------------------
# Gap 3 — Template-validator field mismatch
# ---------------------------------------------------------------------------

class Gap3TemplateFieldMismatchTest(unittest.TestCase):
    """DEF-001: Planning PROGRESS template uses obsolete fields that pass
    planning validation but fail the shared contract validator.

    The planning PROGRESS template (create-spec-driven-plan/assets/PROGRESS.template.md)
    uses: stage=PLAN, brainstorm_revision, current_task, blockers=[], last_validation (nested).
    """

    @classmethod
    def setUpClass(cls):
        cls._progress_contract = _load_module(
            REPO / "scripts" / "progress_contract.py", "gap3_progress"
        )

    def test_shared_contract_rejects_template_fields(self):
        """The shared contract should reject fields from the template-style PROGRESS."""
        fixture = FIX / "template-field-mismatch" / "PROGRESS.md"
        result = self._progress_contract.load_frontmatter(fixture)
        errors = self._progress_contract.validate_progress_fields(result.data)

        stage_rejected = any("stage" in e and "PLAN" in e for e in errors)
        brainstorm_missing_or_rejected = (
            any("brainstorm_revision" in e for e in errors)
            or any("missing field: discovery_revision" in e for e in errors)
        )
        current_task_missing_or_rejected = (
            any("current_task" in e for e in errors)
            or any("missing field: active_task" in e for e in errors)
        )
        last_val_missing_or_rejected = (
            any("last_validation" in e for e in errors)
            or any("missing field: last_validation_command" in e for e in errors)
        )

        self.assertTrue(stage_rejected,
                        "PLAN stage should be rejected (canonical is PLANNING).")
        self.assertTrue(brainstorm_missing_or_rejected,
                        "brainstorm_revision should cause rejection or missing discovery_revision.")
        self.assertTrue(current_task_missing_or_rejected,
                        "current_task/active_task mismatch should be caught.")
        self.assertTrue(last_val_missing_or_rejected,
                        "nested last_validation should be rejected or missing flat fields flagged.")

        # blockers: [] parses as "[]" raw string in progress_contract.py
        # (simple regex match), so it passes the field-existence check.
        # This is itself a gap: the validator does not validate field values
        # for blockers type. Document this as part of DEF-010/DEF-011.
        raw_blockers = result.data.get("blockers", "")
        self.assertIn(
            raw_blockers, ("[]", "{}"),
            f"Template uses blockers: [] which the shared validator does not "
            f"reject as invalid type. Got: {raw_blockers!r}. "
            f"This is documented as part of DEF-010 (progress schema does not "
            f"constrain field types beyond presence).",
        )

    def test_template_uses_canonical_progress_fields(self):
        """Regression: the planning template must not reintroduce v2 fields."""
        template_path = (
            REPO / "skills" / "create-spec-driven-plan" / "assets" / "PROGRESS.template.md"
        )
        content = template_path.read_text(encoding="utf-8")
        self.assertIn("stage: PLANNING", content)
        self.assertIn("discovery_revision:", content)
        self.assertIn("active_task:", content)
        self.assertIn("blockers: NONE", content)
        for obsolete in ("stage: PLAN\n", "brainstorm_revision:", "current_task:", "blockers: []", "last_validation:"):
            self.assertNotIn(obsolete, content)


# ---------------------------------------------------------------------------
# Gap 4 — Planning validator accepts BRAINSTORM stage
# ---------------------------------------------------------------------------

class Gap4PlanningStageAcceptanceTest(unittest.TestCase):
    """DEF-002: validate_plan.py accepts BRAINSTORM and PLAN stages (line 227)."""

    @classmethod
    def setUpClass(cls):
        cls._validate_plan = _load_module(
            REPO / "skills" / "create-spec-driven-plan" / "scripts" / "validate_plan.py",
            "gap4_plan",
        )

    def test_plan_validator_rejects_legacy_stages(self):
        """Regression: planning validation rejects legacy BRAINSTORM and PLAN stages.

        The canonical contract defines only DISCOVERY and PLANNING as stages.
        The planning validator's stage check at line 227 allows:
            {"BRAINSTORM", "PLAN", "DISCOVERY", "PLANNING"}
        This is a false-green: artifacts with legacy stage names pass
        validation when they should be rejected per REQ-003.
        """

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slug = root / "docs" / "ai" / "gap4"
            src = FIX / "obsolete-status-acceptance"
            for path in src.rglob("*"):
                if path.is_file():
                    dest = slug / path.relative_to(src)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "docs/ai/gap4/PROGRESS.md\n", encoding="utf-8"
            )

            old_argv = sys.argv[:]
            try:
                sys.argv = ["validate_plan.py", str(slug)]
                result, code = self._validate_plan.validate()
            finally:
                sys.argv = old_argv

            stage_errors = [
                e for e in result["errors"] if "incompatible stage" in e
            ]
            self.assertTrue(stage_errors)


if __name__ == "__main__":
    unittest.main()
