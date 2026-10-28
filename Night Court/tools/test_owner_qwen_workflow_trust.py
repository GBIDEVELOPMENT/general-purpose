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
            "github.event.pull_request.head.repo.full_name == 'GBIDEVELOPMENT/general-purpose'",
            "github.event.pull_request.head.ref == 'research/night-court-qwen-real-original-trigger'",
            "github.event.pull_request.base.ref == 'main'",
            "FTP_PASSWORD: ${{ secrets.FTP_PASSWORD }}",
        ):
            self.assertIn(required, self.workflow)

    def test_new_physical_business_trigger_is_exact_owner_and_untrusted_head_never_executed(self):
        self.assertIn("Night Court/research/trigger-owner-qwen-physical-comedy.txt", self.workflow)
        self.assertIn("github.event.pull_request.head.ref == 'research/night-court-qwen-physical-comedy-trigger'", self.workflow)
        self.assertIn("&& 'physical_comedy' || 'observational'", self.workflow)
        self.assertIn("--focus '${{ (github.event.pull_request.head.ref", self.workflow)
        self.assertIn("ref: ${{ github.sha }}", self.workflow)
        self.assertNotIn("ref: ${{ github.event.pull_request.head.sha }}", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)

    def test_compact_prompt_trial_is_strictly_owner_only(self):
        self.assertIn("Night Court/research/trigger-owner-qwen-compact-action.txt", self.workflow)
        self.assertIn("research/night-court-qwen-compact-action-trigger", self.workflow)
        self.assertIn("&& 'action_compact' || 'standard'", self.workflow)
        self.assertIn("--prompt-profile '${{ (github.event.pull_request.head.ref", self.workflow)
        self.assertIn("github.event.pull_request.user.login == 'gamesbyian'", self.workflow)
        self.assertIn("github.event.pull_request.head.repo.full_name == 'GBIDEVELOPMENT/general-purpose'", self.workflow)
        self.assertIn("github.event.pull_request.base.ref == 'main'", self.workflow)
        self.assertIn("ref: ${{ github.sha }}", self.workflow)
        self.assertNotIn("ref: ${{ github.event.pull_request.head.sha }}", self.workflow)

    def test_only_owner_temporal_sampling_branch_can_raise_fps(self):
        self.assertIn("Night Court/research/trigger-owner-qwen-compact-twofps.txt", self.workflow)
        self.assertIn("research/night-court-qwen-compact-twofps-trigger", self.workflow)
        self.assertIn("--video-fps '${{ github.event.pull_request.head.ref", self.workflow)
        self.assertIn("&& '2' || '1'", self.workflow)
        self.assertIn("ref: ${{ github.sha }}", self.workflow)
        self.assertNotIn("ref: ${{ github.event.pull_request.head.sha }}", self.workflow)

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

    def test_original_film_reports_publish_with_no_media_and_no_pr_head(self):
        trusted = self.workflow.split("  persist-trusted-owner-original-video-model-review:", 1)[1]
        self.assertIn("needs: trusted-owner-source-visual-inference", trusted)
        self.assertIn("github.event_name == 'pull_request_target'", trusted)
        self.assertIn("github.event.repository.private == true", trusted)
        self.assertIn("github.event.pull_request.user.login == 'gamesbyian'", trusted)
        self.assertIn("github.event.pull_request.head.repo.full_name == 'GBIDEVELOPMENT/general-purpose'", trusted)
        self.assertIn("ref: ${{ github.sha }}", trusted)
        self.assertNotIn("github.event.pull_request.head.sha", trusted)
        self.assertNotIn("FTP_PASSWORD: ${{", trusted)
        self.assertIn("permissions:\n      actions: read\n      contents: write", trusted)
        self.assertIn("test_preserve_original_qwen_model_reports", trusted)
        self.assertIn("preserve_original_qwen_model_reports.py", trusted)

    def test_source_only_publisher_replays_on_unrelated_changes_without_force(self):
        trusted = self.workflow.split("  persist-trusted-owner-original-video-model-review:", 1)[1]
        self.assertIn('source_base="$(git rev-parse HEAD)"', trusted)
        self.assertIn('git diff --name-only "${source_base}" origin/main -- "${protected_paths[@]}"', trusted)
        self.assertIn("rebase.autoStash=false rebase origin/main", trusted)
        self.assertIn("git rebase --abort", trusted)
        self.assertIn("git push origin HEAD:main", trusted)
        self.assertNotIn("git push --force", trusted)
        self.assertNotIn("git push -f ", trusted)
        self.assertIn("for attempt in 1 2; do", trusted)
        self.assertIn("Original-film visual evidence changed concurrently", trusted)

    def test_comment_writer_is_separate_job(self):
        self.assertIn("announce-trusted-owner-run-locator:", self.workflow)
        self.assertIn("pull-requests: write", self.workflow)
        self.assertIn("trusted-owner-source-visual-inference:", self.workflow)
        self.assertIn("permissions:\n  contents: read", self.workflow)

if __name__ == "__main__":
    unittest.main()
