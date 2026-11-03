"""Offline protocol and safety tests; no real seedbox required."""
import pathlib
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import rtorrent_bridge as b

class DummyRPC:
    def __init__(self):
        self.commands = []
        self.active = False
        self.present = True
    def call(self, method, *args):
        self.commands.append((method, args))
        if method == 'd.multicall2':
            return [["A" * 40, "Show S01E01", 100, 75, 125, 10, 20, 1250, 0, 0, 0]]
        if method == 'd.hash':
            if not self.present: raise b.BridgeError('Missing')
            return "A" * 40
        if method == 'd.name': return "Show S01E01"
        if method == 'd.is_active': return int(self.active)
        if method == 'd.complete': return 0
        if method == 'download_list': return ["A" * 40] if self.present else []
        if method == 'd.start': self.active = True; return 0
        if method == 'd.stop': self.active = False; return 0
        if method == 'd.erase': self.present = False; return 0
        if method == 'load.verbose': self.present = True; return 0
        raise AssertionError(method)

class TestBridge(unittest.TestCase):
    def test_https_only_and_endpoint_exact(self):
        with self.assertRaises(b.BridgeError):
            b.validate_url('http://seedhost.example/rutorrent/plugins/httprpc/action.php')
        with self.assertRaises(b.BridgeError):
            b.validate_url('https://user:pass@seedhost.example/rutorrent/plugins/httprpc/action.php')
        with self.assertRaises(b.BridgeError):
            b.validate_url('https://seedhost.example/rutorrent2/')
        self.assertTrue(b.validate_url(b.DEFAULTS[1][1]).startswith('https://'))

    def test_rejects_bad_and_duplicate_hash(self):
        with self.assertRaises(b.BridgeError): b.clean_hash('A' * 39)
        with self.assertRaises(b.BridgeError): b.clean_hash('../../etc')
        rpc = DummyRPC()
        self.assertEqual(b.snapshot(rpc)[0]['ratio'], 1.25)
        rpc.call = lambda name, *args: [["A" * 40] + [0] * 10] * 2
        with self.assertRaises(b.BridgeError): b.snapshot(rpc)

    def test_remove_checks_exact_name_before_rpc(self):
        rpc = DummyRPC()
        with patch.object(b, '_call', return_value=rpc):
            with self.assertRaises(b.BridgeError):
                b.perform('primary', 'A' * 40, 'd.erase', 'remove', 'wrong name')
        self.assertNotIn('d.erase', [m for m, _ in rpc.commands])

    def test_remove_preserves_data_and_verifies(self):
        rpc = DummyRPC()
        with patch.object(b, '_call', return_value=rpc), patch.object(b, 'audit'):
            result = b.perform('primary', 'A' * 40, 'd.erase', 'remove', 'Show S01E01')
        self.assertTrue(result['verified_removed'])
        self.assertFalse(result['files_deleted'])

    def test_start_readback(self):
        rpc = DummyRPC()
        with patch.object(b, '_call', return_value=rpc), patch.object(b, 'audit'):
            result = b.perform('primary', 'A' * 40, 'd.start', 'start')
        self.assertTrue(result['verified_active'])

    def test_magnet_b32_or_hex(self):
        h = '0123456789ABCDEF0123456789ABCDEF01234567'
        self.assertEqual(b.magnet_hash('magnet:?xt=urn:btih:' + h), h)
        import base64
        encoded = base64.b32encode(bytes.fromhex(h)).decode()
        self.assertEqual(b.magnet_hash('magnet:?xt=urn:btih:' + encoded), h)
        with self.assertRaises(b.BridgeError): b.magnet_hash('https://example.com')
        with self.assertRaises(b.BridgeError): b.magnet_hash('magnet:?xt=urn:btmh:somehash')

    def test_no_redirect(self):
        with self.assertRaises(b.BridgeError):
            b.NoRedirect().redirect_request(None, None, 302, 'redirect', {}, 'https://evil.example/')

if __name__ == '__main__': unittest.main()
