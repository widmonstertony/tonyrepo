#!/usr/bin/env python3
"""Repack only the exact verified 1.0.58 payload, without restart scripts."""
import argparse
from pathlib import Path
import sys
import hashlib
import json

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(REPO / 'sources/clash-stability-1.0.57'))
from repack import archive


CONTROL = '''Package: com.codex.clashstability
Name: Clash Stability
Version: 1.0.58
Architecture: iphoneos-arm64
Maintainer: widmonstertony
Author: widmonstertony
Section: Tweaks
Priority: optional
Depends: firmware (>= 16.0), firmware (<< 17.0), mobilesubstrate
Replaces: com.codex.clashstability17, com.codex.clashid16refresh
Conflicts: com.codex.clashstability17, com.codex.clashid16refresh
Description: Fingerprint-based CoC compatibility on the verified iPadOS16.1/Dopamine3.0.11 profile. Allows version-number changes only when complete protection and jailbreak file fingerprints match. Preserves existing identity, caller, snapshot and readiness checks. No restart scripts.
Rootless: true
'''


def make_deb(payload):
    receipt = json.loads((ROOT / 'release.json').read_text())
    if hashlib.sha256(payload).hexdigest() != receipt['payload_sha256']:
        raise ValueError('Not the verified release payload; refuse packaging as 1.0.58')
    filter_plist = (REPO / 'sources/clash-stability-1.0.57/ClashTraceDiagnostic.plist').read_bytes()
    members = [('debian-binary', b'2.0\n'),
               ('control.tar.gz', archive([('control', CONTROL.encode())])),
               ('data.tar.gz', archive([
                   ('var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib', payload),
                   ('var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.plist', filter_plist)]))]
    output = bytearray(b'!<arch>\n')
    for name, data in members:
        header = (name.ljust(16) + '0'.ljust(12) + '0'.ljust(6) +
                  '0'.ljust(6) + '100644'.ljust(8) + str(len(data)).ljust(10) + '`\n')
        output += header.encode() + data
        if len(data) % 2:
            output += b'\n'
    return bytes(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--payload', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Output already exists; refusing overwrite')
    args.output.write_bytes(make_deb(args.payload.read_bytes()))
    print(args.output, hashlib.sha256(args.output.read_bytes()).hexdigest())
