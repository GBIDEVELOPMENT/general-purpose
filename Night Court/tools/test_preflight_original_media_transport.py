"""Fast offline tests for checked original-film protocol readiness."""
import io
import socket
import unittest

from preflight_original_media_transport import probe_banner, run


class FakeSocket:
    def __init__(self, data):
        self.data = data
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def settimeout(self, t):
        assert t > 0

    def recv(self, n):
        return self.data


class SourcePreflightTests(unittest.TestCase):
    def test_ftp_success_on_retry_never_exposes_greeting(self):
        replies = [b"", b"220 seedhost private text\r\n"]
        sockets = []

        def connect(addr, timeout):
            self.assertEqual(addr, ("example.invalid", 21))
            value = FakeSocket(replies.pop(0))
            sockets.append(value)
            return value

        q = probe_banner("example.invalid", 21, expected=b"220", tries=2,
                         timeout=3, delay=0, socket_connection=connect,
                         sleep=lambda n: None)
        self.assertTrue(q["reachable"])
        self.assertEqual(q["failure_classes"], ["closed_before_greeting"])
        self.assertEqual(q["attempts"], 2)
        self.assertTrue(all(x.closed for x in sockets))
        self.assertNotIn("seedhost", str(q))

    def test_sftp_is_only_an_untrusted_banner_diagnostic(self):
        def connect(addr, timeout):
            return FakeSocket(b"SSH-2.0-something\r\n")
        q = probe_banner("test.invalid", 22, expected=b"SSH-", tries=1,
                         socket_connection=connect)
        self.assertTrue(q["reachable"])
        self.assertFalse(q["authenticated"])
        self.assertIsNone(q["file_available"])

    def test_ftp_closed_before_welcome_prevents_heavy_work(self):
        def connect(addr, timeout):
            return FakeSocket(b"")
        q = probe_banner("test.invalid", 21, expected=b"220", tries=3,
                         delay=0, socket_connection=connect, sleep=lambda _: None)
        self.assertEqual(q["failure_classes"], ["closed_before_greeting"] * 3)
        self.assertFalse(q["reachable"])

    def test_network_refusals_not_logged_as_secret_values(self):
        def connect(addr, timeout):
            raise ConnectionRefusedError("some host address in error")
        q = probe_banner("test.invalid", 21, expected=b"220", tries=1,
                         socket_connection=connect)
        self.assertEqual(q["failure_classes"], ["connection_refused"])
        self.assertNotIn("some host", str(q))

    def test_mismatched_banner_not_regarded_as_ftp(self):
        def connect(addr, timeout):
            return FakeSocket(b"SSH-2.0-other")
        q = probe_banner("test.invalid", 21, expected=b"220", tries=1,
                         socket_connection=connect)
        self.assertFalse(q["reachable"])
        self.assertEqual(q["failure_classes"], ["unexpected_protocol_greeting"])

    def test_invalid_bounds(self):
        with self.assertRaisesRegex(ValueError, "bounds"):
            probe_banner("x", 8080, expected=b"220")
        with self.assertRaisesRegex(ValueError, "bounds"):
            probe_banner("x", 21, expected=b"220", tries=99)

    def test_sftp_reachable_is_not_permission_to_run_inference(self):
        def simulated(host, port, **kw):
            return {"port": port, "reachable": port == 22,
                    "authenticated": False, "file_available": None}
        q = run("test.invalid", ftp_probe=simulated)
        self.assertFalse(q["ftp_control_ready_for_authenticated_stage"])
        self.assertFalse(q["ssh_host_key_pinned"])
        self.assertFalse(q["original_media_downloaded"])
        self.assertEqual(q["independent_speaker_or_turns_verified"], 0)


if __name__ == "__main__":
    unittest.main()
