"""Offline contract checks. No Shaw credentials or network access needed."""
import contextlib
import io
import json
import os
import sys
import ssl
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import shaw_mail as mail
import shaw_imap_codec as codec

FAKE_ENV = {"SHAW_EMAIL": "unit-test@shaw.ca", "SHAW_PASSWORD": "dummy-test-only"}


class CodecTests(unittest.TestCase):
    def test_folder_roundtrip(self):
        for folder in ("INBOX", "Sent Items", "Archive/2026", "Bücher & Korrespondenz", "✉ Private"):
            self.assertEqual(codec.decode_mailbox(codec.encode_mailbox(folder)), folder)

    def test_folder_list(self):
        row = b'(\\HasNoChildren) "/" "Sent Items"'
        self.assertEqual(codec.parse_folder_row(row)["name"], "Sent Items")

    def test_quoted_arguments(self):
        self.assertEqual(codec.quoted('A "B" \\ C'), b'"A \\"B\\" \\\\ C"')
        with self.assertRaises(ValueError):
            codec.quoted("x\nLOGOUT")
        with self.assertRaises(ValueError):
            codec.encode_mailbox("x\r\n")

    def test_search_is_literal(self):
        self.assertEqual(codec.search_arguments('a b'), ["TEXT", b'"a b"'])
        self.assertEqual(codec.search_arguments('" OR ALL'), ["TEXT", b'"\\" OR ALL"'])
        self.assertEqual(codec.search_arguments("café")[:3], ["CHARSET", "UTF-8", "TEXT"])


class MailTests(unittest.TestCase):
    def test_shaw_imap_tls_requires_validated_ecdhe(self):
        ctx = mail.imap_tls_context()
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(ctx.check_hostname)
        self.assertGreaterEqual(ctx.minimum_version, ssl.TLSVersion.TLSv1_2)
        names = [item["name"] for item in ctx.get_ciphers()]
        self.assertTrue(any(name.startswith("ECDHE-") for name in names))
        self.assertFalse(any(name.startswith("DHE-") for name in names))

    @patch.dict(os.environ, FAKE_ENV)
    def test_login_name(self):
        self.assertEqual(mail.credentials()[1], "unit-test")

    def test_parse_message(self):
        raw = b"From: person@example.org\r\nSubject: Hello\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nHi"
        msg = mail.message_summary(b"123", raw, True)
        self.assertEqual(msg["uid"], "123")
        self.assertEqual(msg["body_parts"][0]["text"], "Hi")

    @patch.dict(os.environ, {**FAKE_ENV, "SHAW_ALLOWED_RECIPIENTS": "safe@example.org"})
    def test_recipient_allowlist(self):
        draft = {"to": ["other@example.org"], "subject": "Hi", "body": "Hello"}
        with self.assertRaises(ValueError):
            mail.compose(draft)
        draft["to"] = ["safe@example.org"]
        self.assertEqual(mail.compose(draft)["Subject"], "Hi")

    @patch.dict(os.environ, FAKE_ENV)
    def test_header_injection_is_rejected(self):
        draft = {"to": ["safe@example.org, attacker@example.org"], "subject": "Hi", "body": "Hello"}
        with self.assertRaises(ValueError):
            mail.compose(draft)
        draft["to"] = ["safe@example.org"]
        draft["subject"] = "Hi\nBcc: attacker@example.org"
        with self.assertRaises(ValueError):
            mail.compose(draft)

    @patch.dict(os.environ, FAKE_ENV)
    def test_attachment_metadata_only(self):
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["From"] = "friend@example.org"
        msg["Subject"] = "Report"
        msg.set_content("Text")
        msg.add_attachment(b"binary", maintype="application", subtype="octet-stream", filename="report.bin")
        result = mail.message_summary(b"42", msg.as_bytes(), True)
        self.assertEqual(result["attachments"][0]["filename"], "report.bin")
        self.assertEqual(result["attachments"][0]["size_bytes"], 6)

    @patch.dict(os.environ, FAKE_ENV)
    def test_folder_discovery_is_read_only(self):
        conn = MagicMock()
        conn.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "Sent Items"'])
        args = SimpleNamespace(command="folders")
        with patch.object(mail.imaplib, "IMAP4_SSL") as ctor, contextlib.redirect_stdout(io.StringIO()) as out:
            ctor.return_value.__enter__.return_value = conn
            mail.fetch(args)
        self.assertEqual(json.loads(out.getvalue())[0]["name"], "Sent Items")
        conn.select.assert_not_called()

    @patch.dict(os.environ, FAKE_ENV)
    def test_listing_fetches_headers_only(self):
        conn = MagicMock()
        conn.select.return_value = ("OK", [b"3"])
        conn.uid.side_effect = [
            ("OK", [b"12"]),
            ("OK", [(b"1", b"From: other@example.org\r\nSubject: Item\r\n\r\n")]),
        ]
        args = SimpleNamespace(command="inbox", folder="Sent Items", limit=10)
        with patch.object(mail.imaplib, "IMAP4_SSL") as ctor, contextlib.redirect_stdout(io.StringIO()) as out:
            ctor.return_value.__enter__.return_value = conn
            mail.fetch(args)
        self.assertEqual(json.loads(out.getvalue())[0]["uid"], "12")
        self.assertEqual(conn.select.call_args.kwargs["readonly"], True)
        self.assertIn(b'"Sent Items"', conn.select.call_args.args)
        self.assertIn("HEADER.FIELDS", str(conn.uid.call_args))

    @patch.dict(os.environ, FAKE_ENV, clear=True)
    def test_send_requires_allow_send(self):
        draft = {"to": ["friend@example.com"], "subject": "Test", "body": "Hello"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "draft.json"
            path.write_text(json.dumps(draft), encoding="utf-8")
            with patch.object(mail.smtplib, "SMTP") as smtp, contextlib.redirect_stdout(io.StringIO()) as out:
                mail.send(SimpleNamespace(draft=str(path), confirm=False))
                self.assertEqual(json.loads(out.getvalue())["mode"], "preview_only")
                with self.assertRaises(ValueError):
                    mail.send(SimpleNamespace(draft=str(path), confirm=True))
                smtp.assert_not_called()


if __name__ == "__main__":
    unittest.main()
