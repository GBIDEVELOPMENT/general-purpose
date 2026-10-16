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

    def test_pinned_gateway_runtime_source(self):
        text = GATEWAY.read_text(encoding="utf-8")
        self.assertIn("ref: bf7ba25edab17765ee7b8805704bc8a43cd894c5", text)
        self.assertNotIn("pull_request_target:", text)


if __name__ == "__main__":
    unittest.main()
