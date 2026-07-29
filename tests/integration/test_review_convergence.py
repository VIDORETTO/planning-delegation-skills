"""Integration coverage for F02-007 review gap convergence."""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "review-convergence"


def load_validator():
    path = ROOT / "skills" / "review-implementation-evidence" / "scripts" / "validate_review.py"
    spec = importlib.util.spec_from_file_location("validate_review_convergence", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReviewConvergenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def test_each_gap_type_and_return_owner_validates(self):
        cases = {
            "missing-to-plan": ("missing", "create-spec-driven-plan"),
            "partial-to-implementation": ("partial", "execute-routed-task"),
            "contradicts-to-investigation": ("contradicts", "investigate-existing-codebase"),
            "unrequested-to-routing": ("unrequested", "route-ai-work-by-capability"),
            "intent-to-brainstorm": ("missing", "brainstorm-idea-with-user"),
        }
        for name, expected in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / name
                shutil.copytree(FIXTURES / name, target)
                self.materialize(target)
                finding = (target / "findings" / "FND-001.md").read_text(encoding="utf-8")
                self.assertIn(f"gap_type: {expected[0]}", finding)
                self.assertIn(f"return_owner: {expected[1]}", finding)
                self.assertEqual(self.validator.main([str(target)]), 0)

    def test_clean_approval_has_no_empty_finding(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "clean-approval"
            shutil.copytree(FIXTURES / "clean-approval", target)
            self.materialize(target)
            self.assertFalse((target / "findings").exists())
            self.assertEqual(self.validator.main([str(target)]), 0)

    def materialize(self, root: Path) -> None:
        case = dict(line.split(": ", 1) for line in (root / "case.txt").read_text(encoding="utf-8").splitlines() if ": " in line)
        owner = case.get("return_owner")
        routes = {
            "execute-routed-task": ("REVIEW", "CHANGES_REQUIRED", "review-implementation-evidence", "execute-routed-task", "null", "READY", "CHANGES_REQUIRED"),
            "route-ai-work-by-capability": ("ROUTING", "REROUTE_REQUIRED", "route-ai-work-by-capability", "route-ai-work-by-capability", "null", "NOT_READY", "REROUTE_REQUIRED"),
            "create-spec-driven-plan": ("PLANNING", "REPLAN_REQUIRED", "create-spec-driven-plan", "create-spec-driven-plan", "null", "NOT_READY", "REPLAN_REQUIRED"),
            "investigate-existing-codebase": ("DISCOVERY", "CODEBASE_INVESTIGATION_IN_PROGRESS", "investigate-existing-codebase", "investigate-existing-codebase", "investigate-existing-codebase", "NOT_READY", "CODEBASE_INVESTIGATION_IN_PROGRESS"),
            "brainstorm-idea-with-user": ("DISCOVERY", "BRAINSTORM_IN_PROGRESS", "brainstorm-idea-with-user", "brainstorm-idea-with-user", "brainstorm-idea-with-user", "NOT_READY", "BRAINSTORM_IN_PROGRESS"),
            None: ("REVIEW", "REVIEW_APPROVED", "review-implementation-evidence", "validate-release-readiness", "null", "READY", "REVIEW_APPROVED"),
        }
        stage, status, stage_owner, required, writer, handoff_status, outcome = routes[owner]
        root.joinpath("PROGRESS.md").write_text(f"""---
workflow_contract: skill-team/v3
project_id: review-convergence
project_slug: review-convergence
workflow_profile: standard
stage: {stage}
status: {status}
stage_owner: {stage_owner}
required_skill: {required}
successor_skill: NONE
handoff_status: {handoff_status}
discovery_revision: 1
plan_revision: 1
routing_revision: 1
implementation_revision: 1
review_revision: 1
release_revision: 0
active_artifact: review/REVIEW-REPORT.md
active_task: null
active_batch: null
active_executor_model: null
active_reviewer_model: null
writer_skill: {writer}
writer_task: null
next_action: Return review outcome.
blockers: NONE
last_validation_command: python validate_review.py
last_validation_result: PASS
updated_at: 2026-07-29T00:00:00Z
---
""", encoding="utf-8")
        (root / "review").mkdir(exist_ok=True)
        finding_id = "FND-001" if owner else "No findings"
        (root / "review" / "REVIEW-REPORT.md").write_text(f"""---
workflow_contract: skill-team/v3
project_id: review-convergence
project_slug: review-convergence
review_revision: 1
implementation_revision_reviewed: 1
outcome: {outcome}
updated_at: 2026-07-29T00:00:00Z
---
## Identification
Reviewed implementation revision 1.
## Verification performed
Read actual evidence.
## Scope adherence
Within declared scope.
## Contracts, security, and regression risk
Checked against requirements.
## Findings summary
{finding_id}
## Outcome
{outcome}
## Next required skill
{required}
""", encoding="utf-8")
        if owner:
            (root / "findings").mkdir()
            (root / "evidence").mkdir()
            (root / "evidence" / "actual.md").write_text("Actual reviewed evidence.\n", encoding="utf-8")
            gap_type = case["gap_type"]
            (root / "findings" / "FND-001.md").write_text(f"""---
workflow_contract: skill-team/v3
document_type: review-finding
finding_id: FND-001
classification: HIGH
gap_type: {gap_type}
requirement_ids: REQ-031
task_id: F02-007
evidence_path: evidence/actual.md
return_owner: {owner}
status: OPEN
---
## Location
`evidence/actual.md:1`
## Traceability and evidence
Actual evidence differs from REQ-031.
## What is wrong
The reviewed implementation has a gap.
## Why it matters
The requirement is not satisfied.
## Suggested resolution
Return to the owning stage without edits.
## Routed to
{owner}
""", encoding="utf-8")
            if owner == "execute-routed-task":
                self.write_handoff(root / "handoffs" / "REVIEW-TO-IMPLEMENTATION.md", "review-to-implementation", owner)
        else:
            self.write_handoff(root / "handoffs" / "REVIEW-TO-RELEASE.md", "review-to-release", "validate-release-readiness")

    @staticmethod
    def write_handoff(path: Path, handoff_type: str, consumer: str) -> None:
        path.parent.mkdir(exist_ok=True)
        sections = "\n".join(f"## {heading}\nNone." for heading in ("Identification", "Summary", "Artifact inventory", "Preserved decisions", "Allowed open questions", "Blockers", "Consumer write scope", "Forbidden files", "Commands and results", "Stop instruction"))
        path.write_text(f"""---
workflow_contract: skill-team/v3
handoff_type: {handoff_type}
project_id: review-convergence
producer_skill: review-implementation-evidence
consumer_skill: {consumer}
input_revision: 1
output_revision: 1
handoff_status: READY
validation_command: python validate_review.py
validation_result: PASS
generated_at: 2026-07-29T00:00:00Z
---
{sections}
""", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
