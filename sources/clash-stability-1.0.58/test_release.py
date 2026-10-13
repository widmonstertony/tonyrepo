#!/usr/bin/env python3
"""Read-only source/payload tests; never inject test code into the game."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import struct
import sys
import tarfile
import unittest

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(REPO / 'sources/clash-stability-1.0.57'))
spec = importlib.util.spec_from_file_location('oldbuild', REPO / 'sources/clash-stability-1.0.57/build.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
RECEIPT = json.loads((ROOT / 'release.json').read_text())
DEB = REPO / 'debs/com.codex.clashstability_1.0.58_iphoneos-arm64.deb'


def payload():
    with tarfile.open(fileobj=io.BytesIO(old.deb_members(DEB)['data.tar.gz'])) as archive:
        members = {m.name.lstrip('./'): archive.extractfile(m).read() for m in archive.getmembers()}
    return members['var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib']


class FingerprintReleaseTests(unittest.TestCase):
    def test_exact_release(self):
        self.assertEqual(hashlib.sha256(DEB.read_bytes()).hexdigest(), RECEIPT['package_sha256'])
        self.assertEqual(hashlib.sha256(payload()).hexdigest(), RECEIPT['payload_sha256'])
        members = old.deb_members(DEB)
        with tarfile.open(fileobj=io.BytesIO(members['control.tar.gz'])) as archive:
            self.assertEqual([m.name.lstrip('./') for m in archive.getmembers()], ['control'])
        with tarfile.open(fileobj=io.BytesIO(members['data.tar.gz'])) as archive:
            self.assertEqual({m.name.lstrip('./') for m in archive.getmembers()}, {
                'var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib',
                'var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.plist'})

    def test_only_version_calls_changed_in_original_text(self):
        original = old.release_payload(REPO / 'debs/com.codex.clashstability_1.0.57_iphoneos-arm64.deb')
        actual = payload()
        expected = bytearray(original)
        for address in RECEIPT['version_call_sites']:
            before = 0x94000000 | (((0x26c30 - address) // 4) & 0x3ffffff)
            after = 0x94000000 | (((RECEIPT['gate_offset'] - address) // 4) & 0x3ffffff)
            self.assertEqual(struct.unpack_from('<I', original, address)[0], before)
            struct.pack_into('<I', expected, address, after)
        start, end = old.text_range(original)
        self.assertEqual(actual[start:end], expected[start:end])
        self.assertEqual(actual[0x4000:0x4050], original[0x4000:0x4050])
        self.assertEqual(actual[0x27200:0x2c000], original[0x27200:0x2c000])
        self.assertEqual(actual[0x2c060:0x2c0c0], original[0x2c060:0x2c0c0])

    def test_c_fingerprints_match_recipe(self):
        source = (ROOT / 'gate.c').read_text()
        for symbol, key in [('magicx_sha', 'magicx_sha256'),
                            ('systemhook_sha', 'systemhook_file_sha256'),
                            ('dyld_sha', 'dyld_file_sha256')]:
            initializer = re.search(r'unsigned char ' + symbol + r'\[32\] = \{(.*?)\};', source, re.S).group(1)
            values = bytes(int(x, 16) for x in re.findall(r'0x([0-9a-f]{2})', initializer))
            self.assertEqual(values.hex(), RECEIPT[key])
        self.assertIn('O_NOFOLLOW', source)
        self.assertIn('first.st_ino != second.st_ino', source)
        self.assertIn('(void)expected', source)
        self.assertNotIn('CFEqual(', source)

    def test_repacker_rejects_unknown_payload(self):
        spec = importlib.util.spec_from_file_location('pack58', ROOT / 'package_release.py')
        pack = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pack)
        with self.assertRaises(ValueError):
            pack.make_deb(b'unknown')
        self.assertEqual(pack.make_deb(payload()), DEB.read_bytes())


if __name__ == '__main__':
    unittest.main()
