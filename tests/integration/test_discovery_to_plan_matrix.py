"""Discovery handoff selection is canonical and does not require brainstorm input."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/create-spec-driven-plan/scripts/validate_plan.py"

def load_module():
    spec = importlib.util.spec_from_file_location("discovery_matrix_plan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DiscoveryToPlanMatrixTest(unittest.TestCase):
    def _handoff(self, handoff_type, producer, revision=1, status="READY", result="PASS"):
        return f"""---
workflow_contract: skill-team/v3
handoff_type: {handoff_type}
project_id: PROJECT-001
producer_skill: {producer}
consumer_skill: create-spec-driven-plan
input_revision: {revision}
output_revision: {revision}
handoff_status: {status}
validation_command: python validate.py
validation_result: {result}
generated_at: 2026-07-29T00:00:00Z
---

# Canonical handoff

## Identification

Discovery handoff revision {revision}.

## Summary

Discovery is ready for planning.

## Artifact inventory

- Discovery artifact.

## Preserved decisions

- Preserve the recorded discovery outcome.

## Allowed open questions

None.

## Blockers

None.

## Consumer write scope

Planning artifacts only.

## Forbidden files

- Discovery artifacts.

## Commands and results

`python validate.py`: PASS.

## Stop instruction

Stop after producing the planning handoff.
"""

    def test_each_advertised_handoff_is_selected_without_a_brainstorm_alias(self):
        module = load_module()
        for name in module.DISCOVERY_HANDOFFS:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                handoffs = project / "handoffs"
                handoffs.mkdir()
                handoff_type = module.DISCOVERY_HANDOFFS[name]
                (handoffs / name).write_text(self._handoff(handoff_type, module.DISCOVERY_PRODUCERS[handoff_type]), encoding="utf-8")
                self.assertEqual(module.discover_input_handoffs(project), [handoffs / name])
                self.assertEqual(module.validate_discovery_handoff(handoffs / name, 1), [])

    def test_combined_discovery_returns_only_existing_canonical_inputs(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            handoffs = project / "handoffs"
            handoffs.mkdir()
            for name in ("CODEBASE-TO-PLAN.md", "UX-AUDIT-TO-PLAN.md", "LEGACY-TO-PLAN.md"):
                (handoffs / name).write_text("x", encoding="utf-8")
            self.assertEqual({path.name for path in module.discover_input_handoffs(project)}, {"CODEBASE-TO-PLAN.md", "UX-AUDIT-TO-PLAN.md"})

    def test_stale_or_unready_discovery_input_fails_deterministically(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CODEBASE-TO-PLAN.md"
            path.write_text(self._handoff("codebase-to-plan", "investigate-existing-codebase", revision=2, status="NOT_READY", result="NOT_RUN"), encoding="utf-8")
            errors = module.validate_discovery_handoff(path, 1)
            self.assertTrue(any("input_revision does not match" in error for error in errors))
            self.assertTrue(any("READY with validation_result PASS" in error for error in errors))

    def test_compact_brief_requires_closed_structural_questions(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "COMPACT-BRIEF.md"
            path.write_text("""# Brief

## Problem
Fix the bounded defect.

## Outcome
The defect is absent.

## Actors
Maintainer.

## Requirements
- REQ-001: Preserve existing behavior.

## Structural questions
NONE
""", encoding="utf-8")
            self.assertEqual(module.validate_compact_brief(path), [])
            path.write_text(path.read_text(encoding="utf-8").replace("NONE", "- Which storage system?"), encoding="utf-8")
            self.assertIn("compact brief contains unresolved structural questions", module.validate_compact_brief(path))
