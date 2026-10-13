#!/usr/bin/env python3
"""Read-only checks for the final package, build input and repository indexes."""
import bz2
import gzip
import hashlib
import io
from pathlib import Path
import plistlib
import tarfile
import unittest
from build import ROOT, RECIPE, deb_members, release_payload, pinned
from repack import package

REPO = ROOT.parent.parent
DEB = REPO / 'debs/com.codex.clashstability_1.0.57_iphoneos-arm64.deb'


def tar_content(data):
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        return {m.name.lstrip('./'): archive.extractfile(m).read()
                for m in archive.getmembers()}


class ReleaseTests(unittest.TestCase):
    def test_exact_verified_payload_and_archive_members(self):
        payload = release_payload(DEB)
        members = deb_members(DEB)
        self.assertEqual(set(members), {'debian-binary', 'control.tar.gz', 'data.tar.gz'})
        control = tar_content(members['control.tar.gz'])
        self.assertEqual(set(control), {'control'})  # no reboot/respring scripts
        self.assertEqual(control['control'], (ROOT / 'control').read_bytes())
        data = tar_content(members['data.tar.gz'])
        base = 'var/jb/usr/lib/TweakInject/ClashTraceDiagnostic'
        self.assertEqual(set(data), {base + '.dylib', base + '.plist'})
        self.assertEqual(plistlib.loads(data[base + '.plist']),
                         {'Filter': {'Bundles': ['com.supercell.magic']}})
        self.assertEqual(tar_content(deb_members_bytes(package(payload))['data.tar.gz'])[base + '.dylib'], payload)

    def test_pinned_baseline(self):
        pinned(ROOT / 'ClashTraceDiagnostic-baseline-1.0.41.dylib', 'baseline_sha256')
        with self.assertRaises(ValueError):
            pinned(ROOT / 'recipe.json', 'baseline_sha256')

    def test_package_indexes(self):
        packages = (REPO / 'Packages').read_bytes()
        self.assertEqual(gzip.decompress((REPO / 'Packages.gz').read_bytes()), packages)
        self.assertEqual(bz2.decompress((REPO / 'Packages.bz2').read_bytes()), packages)
        found = False
        for stanza in packages.decode().strip().split('\n\n'):
            fields = dict(line.split(': ', 1) for line in stanza.splitlines() if not line.startswith(' '))
            data = (REPO / fields['Filename']).read_bytes()
            self.assertEqual(len(data), int(fields['Size']))
            for field, algorithm in [('MD5sum', 'md5'), ('SHA1', 'sha1'), ('SHA256', 'sha256')]:
                self.assertEqual(hashlib.new(algorithm, data).hexdigest(), fields[field])
            if fields['Package'] == 'com.codex.clashstability' and fields['Version'] == '1.0.57':
                found = True
                self.assertEqual(fields['SHA256'], RECIPE['release_package_sha256'])
                self.assertIn('firmware (<< 17.0)', fields['Depends'])
        self.assertTrue(found)

    def test_release_checksums(self):
        algorithm = None
        for line in (REPO / 'Release').read_text().splitlines():
            if line in ['MD5Sum:', 'SHA1:', 'SHA256:']:
                algorithm = {'MD5Sum:': 'md5', 'SHA1:': 'sha1', 'SHA256:': 'sha256'}[line]
            elif line.startswith(' ') and algorithm:
                digest, size, name = line.split()
                data = (REPO / name).read_bytes()
                self.assertEqual(len(data), int(size))
                self.assertEqual(hashlib.new(algorithm, data).hexdigest(), digest)


def deb_members_bytes(data):
    # Test the in-memory repacker without writing any new DEB files.
    result = {}
    pos = 8
    while pos < len(data):
        header = data[pos:pos + 60]
        size = int(header[48:58])
        result[header[:16].decode().strip().rstrip('/')] = data[pos + 60:pos + 60 + size]
        pos += 60 + size + size % 2
    return result


if __name__ == '__main__':
    unittest.main()
