"""Strict v3 fixtures for post-plan routing, execution, review, and release transitions."""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "post-plan-transitions"
SCRIPTS = {
    "routing": ROOT / "skills/route-ai-work-by-capability/scripts/validate_routing.py",
    "execution": ROOT / "skills/execute-routed-task/scripts/validate_execution.py",
    "review": ROOT / "skills/review-implementation-evidence/scripts/validate_review.py",
    "release": ROOT / "skills/validate-release-readiness/scripts/validate_release.py",
}


def load(name: str):
    spec = importlib.util.spec_from_file_location(f"post_plan_{name}", SCRIPTS[name])
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PostPlanTransitionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = {name: load(name) for name in SCRIPTS}

    def run_fixture(self, name: str, validator: str, expected: int) -> None:
        source = FIXTURES / name
        self.assertTrue(source.is_dir(), f"missing fixture {source}")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / name
            shutil.copytree(source, target)
            self.build_workflow(target, name, validator)
            self.assertEqual(self.modules[validator].main([str(target)]), expected, name)

    def build_workflow(self, root: Path, scenario: str, validator: str) -> None:
        """Instantiate the checked-in scenario marker into a complete strict v3 workflow."""
        (root / "plan").mkdir(); (root / "routing").mkdir(); (root / "handoffs").mkdir()
        (root / "plan" / "TASKS.md").write_text("### [x] F01-001 - Strict transition\n", encoding="utf-8")
        review_mode = "NONE" if scenario == "waived-review" else "REQUIRED_BEFORE_RELEASE"
        (root / "routing" / "ROUTING.md").write_text(
            "| Task | Executor | Reviewer | Review mode |\n| --- | --- | --- | --- |\n"
            f"| F01-001 | MODEL-EXEC | MODEL-REVIEW | {review_mode} |\n", encoding="utf-8")
        (root / "routing" / "MODEL-CAPABILITIES.md").write_text(
            "| Model ID | Tier |\n| --- | --- |\n| MODEL-EXEC | STRONG |\n| MODEL-REVIEW | STRONG |\n", encoding="utf-8")
        self.write_handoff(root / "handoffs" / "ROUTING-TO-IMPLEMENTATION.md", "routing-to-implementation", "route-ai-work-by-capability", "execute-routed-task", 1, 1)
        if scenario in {"reroute", "replan", "investigation", "intent-return", "wrong-model", "two-writer"}:
            required = {"reroute": "route-ai-work-by-capability", "replan": "create-spec-driven-plan", "investigation": "investigate-existing-codebase", "intent-return": "brainstorm-idea-with-user"}.get(scenario, "execute-routed-task")
            status = "TASK_IN_PROGRESS" if scenario in {"wrong-model", "two-writer"} else "TASK_BLOCKED"
            writer = "execute-routed-task" if status == "TASK_IN_PROGRESS" else "null"
            task = "F01-001" if status == "TASK_IN_PROGRESS" else "null"
            model = "MODEL-WRONG" if scenario == "wrong-model" else "MODEL-EXEC"
            if scenario == "two-writer": writer = "review-implementation-evidence"
            if status == "TASK_BLOCKED":
                (root / "blockers").mkdir()
                (root / "blockers" / "F01-001.md").write_text("---\nstatus: OPEN\n---\n", encoding="utf-8")
            self.write_progress(root, "IMPLEMENTATION", status, "execute-routed-task", required, writer, task, model)
            (root / "execution").mkdir(); (root / "execution" / "EVIDENCE.md").write_text("# Evidence\n", encoding="utf-8"); (root / "execution" / "HISTORY.md").write_text("# History\n", encoding="utf-8")
            return
        if validator == "execution":
            self.write_progress(root, "IMPLEMENTATION", "IMPLEMENTATION_COMPLETE", "execute-routed-task", "validate-release-readiness", "null", "null", "null")
            (root / "execution").mkdir(); (root / "execution" / "EVIDENCE.md").write_text("# Evidence\n", encoding="utf-8"); (root / "execution" / "HISTORY.md").write_text("# History\n", encoding="utf-8")
            self.write_handoff(root / "handoffs" / "IMPLEMENTATION-TO-RELEASE.md", "implementation-to-release", "execute-routed-task", "validate-release-readiness", 1, 1)
            return
        if validator == "review":
            status = "CHANGES_REQUIRED" if scenario == "bounded-correction" else "REVIEW_REQUIRED"
            required = "execute-routed-task" if status == "CHANGES_REQUIRED" else "review-implementation-evidence"
            self.write_progress(root, "REVIEW", status, "review-implementation-evidence", required, "null", "null", "null")
            (root / "review").mkdir(); (root / "findings").mkdir()
            report_revision = "0" if scenario == "stale-revision" else "1"
            (root / "review" / "REVIEW-REPORT.md").write_text(self.review_report(report_revision), encoding="utf-8")
            self.write_handoff(root / "handoffs" / "IMPLEMENTATION-TO-REVIEW.md", "implementation-to-review", "execute-routed-task", "review-implementation-evidence", 1, 1)
            if status == "CHANGES_REQUIRED":
                (root / "findings" / "FND-001.md").write_text("---\nfinding_id: FND-001\nclassification: HIGH\nstatus: OPEN\n---\n", encoding="utf-8")
                self.write_handoff(root / "handoffs" / "REVIEW-TO-IMPLEMENTATION.md", "review-to-implementation", "review-implementation-evidence", "execute-routed-task", 1, 1)
            return
        self.write_progress(root, "RELEASE", "RELEASE_REVIEW_REQUIRED", "validate-release-readiness", "validate-release-readiness", "null", "null", "null")
        if scenario == "waived-review":
            self.write_handoff(root / "handoffs" / "IMPLEMENTATION-TO-RELEASE.md", "implementation-to-release", "execute-routed-task", "validate-release-readiness", 1, 1)
        else:
            self.write_handoff(root / "handoffs" / "REVIEW-TO-RELEASE.md", "review-to-release", "review-implementation-evidence", "validate-release-readiness", 1, 1)
        (root / "release").mkdir()
        evidence = "missing/evidence.md" if scenario == "missing-release-evidence" else "command: python -m unittest PASS"
        risk = "| RISK-001 | Tests | bounded |  | 2026-12-01 | NO |\n" if scenario == "accepted-risk-no-owner" else ""
        result = "ACCEPTED_RISK" if scenario == "accepted-risk-no-owner" else "PASS"
        (root / "release" / "RELEASE-READINESS.md").write_text(self.release_decision(result, evidence, risk), encoding="utf-8")

    @staticmethod
    def write_progress(root: Path, stage: str, status: str, owner: str, required: str, writer: str, task: str, model: str) -> None:
        root.joinpath("PROGRESS.md").write_text(f"""---
workflow_contract: skill-team/v3
project_id: P
project_slug: p
workflow_profile: standard
stage: {stage}
status: {status}
stage_owner: {owner}
required_skill: {required}
successor_skill: {required if status == 'IMPLEMENTATION_COMPLETE' else 'NONE'}
handoff_status: {'CONSUMED' if status.endswith('IN_PROGRESS') else 'READY' if status in {'IMPLEMENTATION_COMPLETE', 'REVIEW_REQUIRED', 'CHANGES_REQUIRED', 'RELEASE_REVIEW_REQUIRED'} else 'NOT_READY'}
discovery_revision: 1
plan_revision: 1
routing_revision: 1
implementation_revision: 1
review_revision: 1
release_revision: 1
active_artifact: handoffs/ROUTING-TO-IMPLEMENTATION.md
active_task: {task}
active_batch: null
active_executor_model: {model}
active_reviewer_model: null
writer_skill: {writer}
writer_task: {task if writer != 'null' else 'null'}
next_action: Continue
blockers: {'Open blocker' if status == 'TASK_BLOCKED' else 'NONE'}
last_validation_command: python validate
last_validation_result: PASS
updated_at: 2026-07-29T00:00:00Z
---
""", encoding="utf-8")

    @staticmethod
    def write_handoff(path: Path, kind: str, producer: str, consumer: str, input_revision: int, output_revision: int) -> None:
        body = "\n".join(f"## {section}\nNone." for section in ("Identification", "Summary", "Artifact inventory", "Preserved decisions", "Allowed open questions", "Blockers", "Consumer write scope", "Forbidden files", "Commands and results", "Stop instruction"))
        path.write_text(f"""---
workflow_contract: skill-team/v3
handoff_type: {kind}
project_id: P
producer_skill: {producer}
consumer_skill: {consumer}
input_revision: {input_revision}
output_revision: {output_revision}
handoff_status: READY
validation_command: python validate
validation_result: PASS
generated_at: 2026-07-29T00:00:00Z
---
{body}
""", encoding="utf-8")

    @staticmethod
    def review_report(revision: str) -> str:
        sections = "\n".join(f"## {section}\nNone." for section in ("Identification", "Verification performed", "Scope adherence", "Contracts, security, and regression risk", "Findings summary", "Outcome", "Next required skill"))
        return f"---\nworkflow_contract: skill-team/v3\nproject_id: P\nproject_slug: p\nreview_revision: 1\nimplementation_revision_reviewed: {revision}\noutcome: APPROVED\nupdated_at: 2026-07-29T00:00:00Z\n---\n{sections}\n"

    @staticmethod
    def release_decision(result: str, evidence: str, risk: str) -> str:
        return f"""---
workflow_contract: skill-team/v3
project_id: P
project_slug: p
release_revision: 1
workflow_profile: standard
decision: RELEASE_READY
updated_at: 2026-07-29T00:00:00Z
---
## Identification
None.
## Gate evaluation
| Gate | Result | Evidence |
| --- | --- | --- |
| Tests | {result} | {evidence} |
## Accepted risk register
| ID | Gate | Rationale | Owner | Review | Non-waivable |
| --- | --- | --- | --- | --- | --- |
{risk}## Blockers
None.
## Decision
Ready.
## Next required skill
NONE.
"""

    def test_required_review_path(self):
        self.run_fixture("required-review", "review", 0)
        self.run_fixture("required-review", "release", 0)

    def test_explicitly_waived_review_path(self):
        self.run_fixture("waived-review", "execution", 0)
        self.run_fixture("waived-review", "release", 0)

    def test_bounded_correction_loop(self):
        self.run_fixture("bounded-correction", "review", 0)

    def test_return_paths_name_the_correct_owner(self):
        for name in ("reroute", "replan", "investigation", "intent-return"):
            self.run_fixture(name, "execution", 0)

    def test_stale_revision_is_rejected(self):
        self.run_fixture("stale-revision", "review", 1)

    def test_wrong_active_model_is_rejected(self):
        self.run_fixture("wrong-model", "execution", 1)

    def test_two_writer_conflict_is_rejected(self):
        self.run_fixture("two-writer", "execution", 1)

    def test_release_without_resolving_evidence_is_rejected(self):
        self.run_fixture("missing-release-evidence", "release", 1)

    def test_accepted_risk_without_owner_is_rejected(self):
        self.run_fixture("accepted-risk-no-owner", "release", 1)
