"""Offline tests: the gateway never requires live email or mailbox credentials."""
import contextlib
import io
import json
import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import shaw_mail_protocol as protocol
import shaw_mail_gateway as gateway


class ProtocolTests(unittest.TestCase):
    def test_encrypted_request_response(self):
        private, ready = protocol.server_session()
        command, client_private, request_id = protocol.client_command(
            ready, {"name": "search", "folder": "Sent Items", "query": "personal"}
        )
        serialized = json.dumps(command)
        self.assertNotIn("personal", serialized)
        self.assertNotIn("Sent Items", serialized)
        request = protocol.server_command(private, command, ready["session"])
        self.assertEqual(request["operation"]["query"], "personal")
        answer = protocol.server_response(private, ready, command, request_id, {
            "ok": True, "data": [{"subject": "private research"}]
        })
        self.assertNotIn("private research", json.dumps(answer))
        self.assertEqual(
            protocol.client_response(client_private, ready, answer, request_id)["data"][0]["subject"],
            "private research"
        )

    def test_wrong_private_key_fails(self):
        private, ready = protocol.server_session()
        command, unused_key, rid = protocol.client_command(ready, {"name": "ping"})
        another, _ = protocol.server_session()
        with self.assertRaises(Exception):
            protocol.server_command(another, command, ready["session"])

    def test_expired_request_fails(self):
        private, ready = protocol.server_session()
        client = protocol.X25519PrivateKey.generate()
        command = {
            "version": 2, "kind": "command", "session": ready["session"],
            "client_public": protocol.b64(protocol.public_bytes(client)),
            "ciphertext": protocol.seal(client, ready["server_public"], "request", {
                "id": "0" * 32, "timestamp": int(time.time()) - 2000,
                "operation": {"name": "ping"}
            })
        }
        with self.assertRaisesRegex(ValueError, "Stale"):
            protocol.server_command(private, command, ready["session"])


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            "action": "created", "issue": {"number": 6},
            "repository": {"full_name": "gamesbyian/chat-scheduler"},
            "comment": {"id": 101, "created_at": "2026-10-16T00:00:00Z",
                        "user": {"login": "gamesbyian"},
                        "body": 'SHAWMAIL2 {"version":2,"kind":"start"}'}
        }

    def test_owner_restriction(self):
        self.assertTrue(gateway.eligible(self.event))
        self.event["comment"]["user"]["login"] = "attacker"
        self.assertFalse(gateway.eligible(self.event))

    def test_separate_mail_lanes(self):
        self.assertEqual(gateway.validate_lane("start", {"name": "inbox", "folder": "INBOX"}), "inbox")
        self.assertEqual(gateway.validate_lane("start_smtp", {"name": "diagnose"}), "diagnose")
        valid_draft = {
            "name": "send", "confirm": True,
            "draft": {"to": ["test@example.org"], "subject": "Safe", "body": "Sample"}
        }
        self.assertEqual(gateway.validate_lane("start_smtp", valid_draft), "send")
        with self.assertRaises(ValueError):
            gateway.validate_lane("start", valid_draft)
        with self.assertRaises(ValueError):
            gateway.validate_lane("start_smtp", {"name": "read", "uid": "1"})
        with self.assertRaises(ValueError):
            gateway.validate_lane("start", {"name": "diagnose"})

    def test_smtp_start_restricts_actor_and_exact_body(self):
        self.event["comment"]["body"] = 'SHAWMAIL2 {"version":2,"kind":"start_smtp"}'
        self.assertTrue(gateway.eligible(self.event))
        self.event["comment"]["body"] += ' extra'
        self.assertFalse(gateway.eligible(self.event))
        self.event["comment"]["user"]["login"] = "attacker"
        self.assertFalse(gateway.eligible(self.event))

    def test_full_issue_roundtrip_ping(self):
        handshake, command_info, result = {}, {}, []
        def poster(_token, value):
            if value.get("kind") == "ready":
                handshake.update(value)
                command, client_private, request_id = protocol.client_command(
                    value, {"name": "ping"}
                )
                command_info.update({
                    "body": gateway.PREFIX + json.dumps(command),
                    "user": {"login": "gamesbyian"}, "id": 102,
                    "client_private": client_private, "request_id": request_id
                })
            elif value.get("kind") == "result":
                result.append(value)
            return {"id": 103}
        def getter(_token, _since):
            return [dict(command_info)] if command_info else []

        with patch.object(gateway, "post_comment", side_effect=poster), \
                patch.object(gateway, "comments_since", side_effect=getter):
            self.assertTrue(gateway.run(self.event, "dummy-token"))

        answer = protocol.client_response(
            command_info["client_private"], handshake, result[0],
            command_info["request_id"]
        )
        self.assertEqual(answer["reply"], "pong")
        self.assertNotIn("pong", json.dumps(result[0]))

    def test_send_without_confirmation_denied(self):
        with self.assertRaises(ValueError):
            gateway.validate_operation({"name": "send", "draft": {
                "to": ["a@example.com"], "subject": "Hi", "body": "Hello"
            }})
        with self.assertRaises(ValueError):
            gateway.validate_operation({"name": "send", "confirm": True,
                                        "draft": {"to": [], "subject": "Hi", "body": "x" * 18000}})

    def test_missing_mail_secret_stays_encrypted_in_real_protocol(self):
        with patch.dict(os.environ, {"SHAW_PASSWORD": ""}):
            self.assertEqual(
                gateway.operate({"name": "folders"}, "x",
                                {"session": "stub"}, "f" * 32)["error"],
                "mail_secret_not_configured"
            )

    def test_no_plaintext_mail_from_mock(self):
        with patch.dict(os.environ, {"SHAW_PASSWORD": "test-password"}), \
             patch.object(gateway.mail, "fetch") as fetch:
            def fake_fetch(args):
                print(json.dumps([{"subject": "confidential", "body": "test"}]))
            fetch.side_effect = fake_fetch
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                result = gateway.operate({"name": "inbox", "folder": "INBOX", "limit": 2},
                                         "token", {"session": "stub"}, "f" * 32)
            self.assertEqual(out.getvalue(), "")
            self.assertEqual(result["data"][0]["subject"], "confidential")


if __name__ == "__main__":
    unittest.main()
