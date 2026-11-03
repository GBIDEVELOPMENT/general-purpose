"""Regression tests: adding secondary rTorrent profiles must preserve primary credentials."""
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import rtorrent_bridge as b

@unittest.skipUnless(os.name == "nt", "Local DPAPI profile setup is Windows-only")
class TestExtension(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = pathlib.Path(self.tmp.name) / "profiles.json"
        self.initial = {"version":1, "allow_writes":True, "extra_setting":"do-not-lose",
                        "profiles":[{"id":"primary", "url":b.DEFAULTS[0][1],
                                     "username":"original-user",
                                     "password_dpapi":"ORIGINAL_DPAPI_BLOB"}]}
        self.path.write_text(json.dumps(self.initial),encoding="utf-8")
        self.patcher1=patch.object(b,"CONFIG_FILE",self.path)
        self.patcher2=patch.object(b,"CONFIG_DIR",self.path.parent)
        self.patcher1.start()
        self.patcher2.start()
        self.addCleanup(self.patcher1.stop)
        self.addCleanup(self.patcher2.stop)

    def test_extend_preserves_primary_blob_and_write_policy(self):
        with patch("builtins.input",return_value=""), \
             patch.object(b.getpass,"getpass",side_effect=["new-pass", ""]), \
             patch.object(b,"_win_dpapi",return_value=b"mock-protected"):
            b.setup(extend=True)
        current=json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(current["profiles"][0],self.initial["profiles"][0])
        self.assertEqual(current["extra_setting"],"do-not-lose")
        self.assertTrue(current["allow_writes"])
        self.assertEqual([p["id"] for p in current["profiles"]],["primary","second"])
        backup=json.loads(self.path.with_suffix(".bak").read_text(encoding="utf-8"))
        self.assertEqual(backup,self.initial)

    def test_extend_with_no_new_password_does_not_write(self):
        before=self.path.read_bytes()
        with patch("builtins.input",return_value=""), \
             patch.object(b.getpass,"getpass",side_effect=["",""]):
            b.setup(extend=True)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertFalse(self.path.with_suffix(".bak").exists())

    def test_reset_and_extend_conflict(self):
        with self.assertRaises(b.BridgeError):
            b.setup(force=True,extend=True)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")),self.initial)

if __name__ == "__main__":
    unittest.main()
