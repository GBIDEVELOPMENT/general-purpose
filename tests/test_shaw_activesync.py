"""Offline tests for safe ActiveSync capability negotiation. Never contacts Shaw."""
import base64
import os
import sys
import unittest
from email.message import Message
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import shaw_activesync as eas


class ActiveSyncTests(unittest.TestCase):
    @patch.dict(os.environ, {"SHAW_EMAIL": "test@shaw.ca", "SHAW_PASSWORD": "not-a-real-secret"})
    def test_verified_options_does_not_send_or_follow_redirects(self):
        resp = MagicMock()
        resp.status = 200
        resp.headers = {
            "MS-ASProtocolVersions": "2.5,12.1,14.1",
            "MS-ASProtocolCommands": "Sync,SendMail,Ping",
        }
        with patch.object(eas, "build_opener") as opener:
            opener.return_value.open.return_value.__enter__.return_value = resp
            result = eas.discover()
            self.assertTrue(result["auth_accepted"])
            self.assertTrue(result["supports_sendmail"])
            self.assertIn("12.1", result["protocol_versions"])
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(request.get_method(), "OPTIONS")
            self.assertEqual(request.full_url, eas.EAS_URL)
            header = request.get_header("Authorization")
            self.assertEqual(
                base64.b64decode(header.split(" ", 1)[1]),
                b"test:not-a-real-secret",
            )
            self.assertTrue(opener.call_args.args[1]._context.check_hostname)
            self.assertIsNone(opener.call_args.args[0].redirect_request(
                request, None, 302, "redirect", {}, "https://attacker.example/"
            ))

    @patch.dict(os.environ, {"SHAW_EMAIL": "test@shaw.ca", "SHAW_PASSWORD": "not-a-real-secret"})
    def test_http_challenge_returns_status_only(self):
        req = Request(eas.EAS_URL)
        exc = HTTPError(eas.EAS_URL, 401, "Invalid secret", {}, None)
        exc.headers = {
            "WWW-Authenticate": 'Basic realm="secrets"',
            "MS-ASProtocolCommands": "",
        }
        with patch.object(eas, "build_opener") as opener:
            opener.return_value.open.side_effect = exc
            out = eas.discover()
            self.assertEqual(out["http_status"], 401)
            self.assertFalse(out["auth_accepted"])
            self.assertNotIn("secret", str(out).lower())

    def test_metadata_is_sanitized(self):
        self.assertEqual(eas.safe_header("SendMail\npassword", frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")), "SendMailpassword")


if __name__ == "__main__":
    unittest.main()
