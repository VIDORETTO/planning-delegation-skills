from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import workflow_contract

BASE = {"workflow_contract":"skill-team/v3","project_id":"p","project_slug":"p","workflow_profile":"standard","stage":"DISCOVERY","status":"BRAINSTORM_IN_PROGRESS","stage_owner":"brainstorm-idea-with-user","required_skill":"brainstorm-idea-with-user","successor_skill":"create-spec-driven-plan","handoff_status":"NOT_READY","discovery_revision":"1","plan_revision":"0","routing_revision":"0","implementation_revision":"0","review_revision":"0","release_revision":"0","active_artifact":"discovery/brainstorm/BRAINSTORM.md","active_task":"null","active_batch":"null","active_executor_model":"null","active_reviewer_model":"null","writer_skill":"brainstorm-idea-with-user","writer_task":"null","next_action":"write","blockers":"NONE","last_validation_command":"NONE","last_validation_result":"NOT_RUN","updated_at":"2026-01-01T00:00:00Z"}

class WorkflowContractTest(unittest.TestCase):
    def test_canonical_discovery_state_passes(self): self.assertEqual([], workflow_contract.validate_progress(BASE))
    def test_every_canonical_state_accepts_its_declared_relation(self):
        for (stage, status), (owner, required, writer, handoff) in workflow_contract.STATES.items():
            with self.subTest(stage=stage, status=status):
                required_skill = required or "validate-release-readiness"
                if (stage, status) == ("IMPLEMENTATION", "TASK_BLOCKED"):
                    required_skill = "create-spec-driven-plan"
                data = dict(BASE, stage=stage, status=status, stage_owner=owner or "brainstorm-idea-with-user", required_skill=required_skill, writer_skill=writer or "null", handoff_status=handoff, writer_task="TASK-001" if (stage, status) == ("IMPLEMENTATION", "TASK_IN_PROGRESS") else "null")
                self.assertEqual([], workflow_contract.validate_progress(data))
    def test_legacy_contract_and_unknown_field_fail(self):
        data = dict(BASE, workflow_contract="planning-delegation/v2", next_skill="x")
        errors = workflow_contract.validate_progress(data)
        self.assertTrue(any(e.startswith("STV3-E001-CONTRACT") for e in errors))
        self.assertTrue(any(e.startswith("STV3-E003-FIELD-UNKNOWN") for e in errors))
    def test_wrong_writer_fails(self):
        errors = workflow_contract.validate_progress(dict(BASE, writer_skill="null"))
        self.assertTrue(any(e.startswith("STV3-E009-WRITER-LOCK") for e in errors))
    def test_each_state_rejects_wrong_required_skill(self):
        for (stage, status), (owner, required, writer, handoff) in workflow_contract.STATES.items():
            if not required:
                continue
            with self.subTest(stage=stage, status=status):
                data = dict(BASE, stage=stage, status=status, stage_owner=owner or "execute-routed-task", required_skill="wrong-skill", writer_skill=writer or "null", handoff_status=handoff, writer_task="TASK-001" if (stage, status) == ("IMPLEMENTATION", "TASK_IN_PROGRESS") else "null")
                self.assertTrue(any(e.startswith("STV3-E008-REQUIRED-SKILL") for e in workflow_contract.validate_progress(data)))
    def test_blocked_task_requires_a_classified_owner(self):
        data = dict(BASE, stage="IMPLEMENTATION", status="TASK_BLOCKED", stage_owner="execute-routed-task", required_skill="validate-release-readiness", writer_skill="null", handoff_status="NOT_READY")
        self.assertTrue(any(e.startswith("STV3-E008-REQUIRED-SKILL") for e in workflow_contract.validate_progress(data)))
        for owner in workflow_contract.TASK_BLOCKED_REQUIRED_SKILLS:
            with self.subTest(owner=owner):
                self.assertEqual([], workflow_contract.validate_progress(dict(data, required_skill=owner)))
    def test_implementation_complete_requires_reviewer_or_release_validator(self):
        data = dict(BASE, stage="IMPLEMENTATION", status="IMPLEMENTATION_COMPLETE", stage_owner="execute-routed-task", required_skill="create-spec-driven-plan", writer_skill="null", handoff_status="READY")
        self.assertTrue(any(e.startswith("STV3-E008-REQUIRED-SKILL") for e in workflow_contract.validate_progress(data)))
        for skill in workflow_contract.IMPLEMENTATION_COMPLETE_REQUIRED_SKILLS:
            with self.subTest(skill=skill):
                self.assertEqual([], workflow_contract.validate_progress(dict(data, required_skill=skill)))
    def test_handoff_rejects_unknown_fields_invalid_enum_timestamp_and_empty_body(self):
        handoff = {"workflow_contract":"skill-team/v3","handoff_type":"brainstorm-to-plan","project_id":"p","producer_skill":"brainstorm-idea-with-user","consumer_skill":"create-spec-driven-plan","input_revision":"1","output_revision":"1","handoff_status":"MAYBE","validation_command":"python validate","validation_result":"MAYBE","generated_at":"tomorrow","extra":"no"}
        errors = workflow_contract.validate_handoff(handoff, "")
        for code in ("STV3-E003-FIELD-UNKNOWN", "STV3-E005-ENUM", "STV3-E011-TIMESTAMP", "STV3-E013-HANDOFF-BODY"):
            self.assertTrue(any(error.startswith(code) for error in errors), errors)
    def test_handoff_requires_each_nonempty_body_section(self):
        handoff = {"workflow_contract":"skill-team/v3","handoff_type":"brainstorm-to-plan","project_id":"p","producer_skill":"brainstorm-idea-with-user","consumer_skill":"create-spec-driven-plan","input_revision":"1","output_revision":"1","handoff_status":"READY","validation_command":"python validate","validation_result":"PASS","generated_at":"2026-01-01T00:00:00Z"}
        body = "\n".join(f"## {section}\nNone." for section in workflow_contract.HANDOFF_SECTIONS if section != "Blockers")
        errors = workflow_contract.validate_handoff(handoff, body)
        self.assertTrue(any("Blockers: required section is absent" in error for error in errors), errors)
        body = "\n".join(f"## {section}" if section == "Blockers" else f"## {section}\nNone." for section in workflow_contract.HANDOFF_SECTIONS)
        errors = workflow_contract.validate_handoff(handoff, body)
        self.assertTrue(any("Blockers: section must not be empty" in error for error in errors), errors)
    def test_transition_requires_canonical_edge_and_revision_increment(self):
        current = dict(BASE, stage="PLANNING", status="PLAN_IN_PROGRESS", stage_owner="create-spec-driven-plan", required_skill="create-spec-driven-plan", writer_skill="create-spec-driven-plan", plan_revision="1")
        self.assertEqual([], workflow_contract.validate_transition(dict(BASE, status="DISCOVERY_READY", stage_owner="brainstorm-idea-with-user", required_skill="create-spec-driven-plan", writer_skill="null", handoff_status="READY"), current))
        missing_increment = dict(current, plan_revision="0")
        errors = workflow_contract.validate_transition(dict(BASE, status="DISCOVERY_READY", stage_owner="brainstorm-idea-with-user", required_skill="create-spec-driven-plan", writer_skill="null", handoff_status="READY"), missing_increment)
        self.assertTrue(any(error.startswith("STV3-E010-REVISION") for error in errors))
        invalid = dict(BASE, stage="PLANNING", status="PLAN_VALIDATED", stage_owner="create-spec-driven-plan", required_skill="route-ai-work-by-capability", writer_skill="null", handoff_status="READY")
        errors = workflow_contract.validate_transition(BASE, invalid)
        self.assertTrue(any(error.startswith("STV3-E014-TRANSITION") for error in errors))
        previous = dict(BASE, stage="PLANNING", status="PLAN_IN_PROGRESS", stage_owner="create-spec-driven-plan", required_skill="create-spec-driven-plan", writer_skill="create-spec-driven-plan")
        errors = workflow_contract.validate_progress(invalid, previous)
        self.assertTrue(any(error.startswith("STV3-E010-REVISION") for error in errors))
