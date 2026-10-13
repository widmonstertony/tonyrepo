#!/usr/bin/env python3
"""Offline release hashes, mutation scope and archive checks; not device tests."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import tarfile

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
spec=importlib.util.spec_from_file_location('legacy',ROOT.parent/'clash-stability-1.0.57/build.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
receipt=json.loads((ROOT/'verification.json').read_text())
path=REPO/'debs/com.codex.clashstability17_1.1.0_iphoneos-arm64.deb'
assert hashlib.sha256(path.read_bytes()).hexdigest()==receipt['package_sha256']
members=legacy.deb_members(path)
with tarfile.open(fileobj=io.BytesIO(members['control.tar.gz'])) as t:
    assert [x.name for x in t.getmembers()]==['./control'], 'Unexpected maintainer script'
with tarfile.open(fileobj=io.BytesIO(members['data.tar.gz'])) as t:
    names=[x.name.lstrip('./') for x in t.getmembers()]
    assert set(names)=={'var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib',
                       'var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.plist'}
    payload=t.extractfile(t.getmembers()[0]).read()
assert hashlib.sha256(payload).hexdigest()==receipt['payload_sha256']
baseline=(ROOT.parent/'clash-stability-1.0.57/ClashTraceDiagnostic-baseline-1.0.41.dylib').read_bytes()
assert payload[0x7db8:0x16be0]==baseline[0x7db8:0x16be0], 'iOS16 code changed'
assert payload[0x27200:0x2c000]==baseline[0x27200:0x2c000], 'Original profile changed'
for call in (0x18974,0x1d378,0x245bc):
    assert struct.unpack_from('<I',payload,call)[0]==0x94000000|(((0x4100-call)//4)&0x3ffffff)
for off,val in ((0x20108,0x52800e4d),(0x2049c,0x7100111f),(0x204b8,0x7101c91f)):
    assert struct.unpack_from('<I',payload,off)[0]==val
suffix=b'/usr/lib/TweakInject/ClashTraceDiagnostic.dylib\0'
assert payload[0x4014:0x4014+len(suffix)]==suffix
print('PASS: exact release, isolated iOS17 code changes, no restart/diagnostic artifacts')
