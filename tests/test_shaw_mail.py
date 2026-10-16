"""Offline tests for Shaw mail parsing and outbound safeguards."""
import importlib.util
import os
import unittest
from unittest.mock import patch
from pathlib import Path

spec = importlib.util.spec_from_file_location("shaw_mail", Path(__file__).resolve().parents[1] / "tools" / "shaw_mail.py")
mail = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mail)


class MailTests(unittest.TestCase):
    @patch.dict(os.environ, {"SHAW_EMAIL": "person@shaw.ca", "SHAW_PASSWORD": "dummy"})
    def test_username(self):
        self.assertEqual(mail.credentials()[1], "person")

    def test_message_summary(self):
        raw = b"From: sender@example.org\r\nSubject: Hello\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nHi"
        item = mail.message_summary(b"123", raw, True)
        self.assertEqual(item["uid"], "123")
        self.assertEqual(item["body_parts"][0]["text"], "Hi")

    @patch.dict(os.environ, {"SHAW_EMAIL": "person@shaw.ca", "SHAW_PASSWORD": "dummy", "SHAW_ALLOWED_RECIPIENTS": "safe@example.org"})
    def test_allowlist(self):
        with self.assertRaises(ValueError):
            mail.compose({"to": ["other@example.org"], "subject": "Hi", "body": "Hello"})
        msg = mail.compose({"to": ["safe@example.org"], "subject": "Hi", "body": "Hello"})
        self.assertEqual(msg["Subject"], "Hi")

    def test_missing_credentials(self):
        with patch.dict(os.environ, {"SHAW_EMAIL": "", "SHAW_PASSWORD": ""}):
            with self.assertRaises(ValueError):
                mail.credentials()


if __name__ == "__main__":
    unittest.main()
