"""Ensure the prose contract declares the complete v3 release path."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class StateTransitionContractTest(unittest.TestCase):
    def test_release_review_states_and_waived_handoff_are_declared(self):
        contract = (ROOT / "contracts/skill-team-v3.md").read_text(encoding="utf-8")
        for value in ("RELEASE_REVIEW_IN_PROGRESS", "POST_RELEASE_REVIEW_IN_PROGRESS", "implementation-to-release"):
            self.assertIn(value, contract)

    def test_contract_declares_return_and_revision_behavior(self):
        contract = (ROOT / "contracts/skill-team-v3.md").read_text(encoding="utf-8")
        self.assertIn("return never resets a downstream revision", contract)
        self.assertIn("Combined discovery is sequential", contract)
