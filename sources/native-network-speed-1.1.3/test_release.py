#!/usr/bin/env python3
"""Offline package/filter/architecture checks, optionally source-code reproduction."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import plistlib
import struct
import tarfile

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent

def deb_members(data):
    assert data[:8]==b'!<arch>\n'
    result={};pos=8
    while pos<len(data):
        h=data[pos:pos+60];assert h[58:60]==b'`\n'
        size=int(h[48:58]);name=h[:16].decode().strip().rstrip('/')
        result[name]=data[pos+60:pos+60+size];pos+=60+size+size%2
    return result

def slices(data):
    assert struct.unpack_from('>I',data)[0]==0xcafebabe
    n=struct.unpack_from('>I',data,4)[0];assert n==2
    result={}
    for i in range(n):
        cpu,sub,off,size,align=struct.unpack_from('>5I',data,8+i*20)
        assert cpu==0x100000c and sub&0xffffff in (0,2)
        result[sub&0xffffff]=data[off:off+size]
    assert set(result)=={0,2}
    return result

def sections(data):
    assert struct.unpack_from('<I',data)[0]==0xfeedfacf
    pos=32;result={}
    for i in range(struct.unpack_from('<I',data,16)[0]):
        cmd,size=struct.unpack_from('<II',data,pos)
        if cmd==0x19:
            for j in range(struct.unpack_from('<I',data,pos+64)[0]):
                sec=pos+72+j*80
                name=data[sec:sec+16].rstrip(b'\0').decode()
                length=struct.unpack_from('<Q',data,sec+40)[0]
                off=struct.unpack_from('<I',data,sec+48)[0]
                if name in ('__text','__const','__cstring','__objc_methname','__objc_classname','__objc_methtype'):
                    result[name]=data[off:off+length]
        pos+=size
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=ROOT)
    p.add_argument('--compare-built',type=Path);a=p.parse_args()
    receipt=json.loads((a.source_dir/'verification.json').read_text())
    pkg=REPO/receipt['package_path'];data=pkg.read_bytes()
    assert hashlib.sha256(data).hexdigest()==receipt['package_sha256']
    members=deb_members(data)
    with tarfile.open(fileobj=io.BytesIO(members['control.tar.gz'])) as t:
        assert [x.name for x in t.getmembers()]==['./control']
    with tarfile.open(fileobj=io.BytesIO(members['data.tar.gz'])) as t:
        entries={x.name.lstrip('./'):t.extractfile(x).read() for x in t.getmembers()}
    assert set(entries)=={'var/jb/usr/lib/TweakInject/TonyNetStatus.dylib',
        'var/jb/usr/lib/TweakInject/TonyNetStatus.plist',
        'var/jb/Library/PreferenceLoader/Preferences/TonyNetStatus.plist'}
    payload=entries['var/jb/usr/lib/TweakInject/TonyNetStatus.dylib']
    assert hashlib.sha256(payload).hexdigest()==receipt['payload_sha256']
    assert plistlib.loads(entries['var/jb/usr/lib/TweakInject/TonyNetStatus.plist'])['Filter']['Bundles']==['com.apple.springboard']
    thin=slices(payload)
    if a.compare_built:
        rebuilt=slices(a.compare_built.read_bytes())
        for arch in thin: assert sections(thin[arch])==sections(rebuilt[arch]), 'Source code/data differ'
    print('PASS: exact release, arm64+arm64e, SpringBoard-only filter, no restart scripts')

if __name__=='__main__': main()
