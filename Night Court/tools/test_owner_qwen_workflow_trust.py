#!/usr/bin/env python3
"""Static read-only regression checks for trusted original-video workflow checkout."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/night-court-owner-qwen-picture-pilot.yml"

class OwnerSourceWorkflowTrust(unittest.TestCase):
    def setUp(self):
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_event_base_checkout_is_current_and_never_pr_head(self):
        self.assertIn("ref: ${{ github.sha }}", self.workflow)
        self.assertNotIn("ref: ${{ github.event.pull_request.base.sha }}", self.workflow)
        self.assertNotIn("ref: ${{ github.event.pull_request.head.sha }}", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)

    def test_exact_owner_main_trigger(self):
        for required in (
            "github.event_name == 'pull_request_target'",
            "github.event.pull_request.user.login == 'gamesbyian'",
            "github.event.pull_request.head.repo.full_name == 'gamesbyian/general-purpose'",
            "github.event.pull_request.head.ref == 'research/night-court-qwen-real-original-trigger'",
            "github.event.pull_request.base.ref == 'main'",
            "FTP_PASSWORD: ${{ secrets.FTP_PASSWORD }}",
        ):
            self.assertIn(required, self.workflow)

    def test_one_original_model_pass_produces_deferred_review_and_safe_metrics(self):
        self.assertIn("prepare_video_stage_review.py", self.workflow)
        self.assertIn("summarize_original_qwen_pilot_metrics.py", self.workflow)
        self.assertIn("--reviewer-id original-film-pending", self.workflow)
        self.assertIn("nc-qwen-pending-", self.workflow)
        self.assertIn("nc-qwen-review-", self.workflow)
        self.assertIn("nc-qwen-safe-metrics-", self.workflow)
        self.assertIn("retention-days: 7", self.workflow)
        self.assertIn("if: success()", self.workflow)
        # All report files are generated *after* source data is acquired, and
        # credential-scoped FTP_PASSWORD must not be declared at job scope.
        self.assertNotIn("\n      FTP_PASSWORD: ${{ secrets.FTP_PASSWORD }}", self.workflow)

    def test_cheap_ci_lane_does_not_block_source_jobs(self):
        self.assertIn("github.event_name == 'pull_request_target' && 'trusted-source' || github.ref", self.workflow)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", self.workflow)

    def test_comment_writer_is_separate_job(self):
        self.assertIn("announce-trusted-owner-run-locator:", self.workflow)
        self.assertIn("pull-requests: write", self.workflow)
        self.assertIn("trusted-owner-source-visual-inference:", self.workflow)
        self.assertIn("permissions:\n  contents: read", self.workflow)

if __name__ == "__main__":
    unittest.main()
