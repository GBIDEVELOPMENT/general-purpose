"""Secret-free contract coverage for operator-side encrypted Shaw mailbox access."""
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import shaw_gateway_client as client
import shaw_mail_protocol as protocol


class GatewayClientTests(unittest.TestCase):
    def test_private_one_use_roundtrip(self):
        server, ready = protocol.server_session()
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "private-state.json")
            command = client.prepare(ready, {"name": "inbox", "folder": "Sent", "limit": 4}, path)
            self.assertFalse("Sent" in str(command))
            self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)
            operation = protocol.server_command(server, command, ready["session"])
            self.assertEqual(operation["operation"]["folder"], "Sent")
            response = protocol.server_response(
                server, ready, command, operation["id"],
                {"ok": True, "data": [{"subject": "private mail"}]}
            )
            self.assertNotIn("private mail", str(response))
            clear = client.complete(path, response)
            self.assertEqual(clear["data"][0]["subject"], "private mail")
            self.assertFalse(Path(path).exists())

    def test_refuse_overwrite_existing_state(self):
        server, ready = protocol.server_session()
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            state.write_text("do not replace", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                client.prepare(ready, {"name": "folders"}, str(state))
            self.assertEqual(state.read_text(encoding="utf-8"), "do not replace")

    def test_send_requires_matching_single_recipient(self):
        _, ready = protocol.server_session()
        op = {
            "name": "send", "confirm": True,
            "draft": {"to": ["ianmakesjokes@gmail.com"], "subject": "Test", "body": "Test"}
        }
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                client.prepare(ready, op, str(Path(tmp) / "a.json"))
            with self.assertRaises(ValueError):
                client.prepare(ready, op, str(Path(tmp) / "a.json"),
                               send_recipient="different@example.com")
            correct = str(Path(tmp) / "approved.json")
            client.prepare(ready, op, correct, send_recipient="ianmakesjokes@gmail.com")
            self.assertTrue(Path(correct).exists())

    def test_invalid_decryption_does_not_discard_state(self):
        _, ready = protocol.server_session()
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "key.json")
            client.prepare(ready, {"name": "ping"}, path)
            with self.assertRaises(ValueError):
                client.complete(path, {"version": 2, "kind": "result", "id": "wrong"})
            self.assertTrue(Path(path).exists())


if __name__ == "__main__":
    unittest.main()
