"""Tripwire against accidental Shaw secret exposure in other workflows.

This is a regression check, not a substitute for protected GitHub permissions.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATEWAY = ROOT / ".github/workflows/shaw-mail-gateway.yml"


class SecretBoundaryTests(unittest.TestCase):
    def test_only_gateway_workflow_reads_mail_secret(self):
        workflows = list((ROOT / ".github/workflows").glob("*.yml"))
        for workflow in workflows:
            text = workflow.read_text(encoding="utf-8")
            if "secrets.SHAW_PASSWORD" in text:
                self.assertEqual(workflow, GATEWAY, f"Secret referenced by {workflow}")
        self.assertIn("secrets.SHAW_PASSWORD", GATEWAY.read_text(encoding="utf-8"))

    def test_smtp_lane_selects_macos_runner(self):
        text = GATEWAY.read_text(encoding="utf-8")
        self.assertIn("start_smtp", text)
        self.assertIn("macos-latest", text)
        self.assertIn("ubuntu-latest", text)
        self.assertIn("github.event.comment.user.login == 'gamesbyian'", text)

    def test_pinned_gateway_runtime_source(self):
        text = GATEWAY.read_text(encoding="utf-8")
        self.assertIn("ref: ea4f43a0c4c4d74fdcd075c7dbac03b67af573b8", text)
        self.assertNotIn("pull_request_target:", text)


if __name__ == "__main__":
    unittest.main()
