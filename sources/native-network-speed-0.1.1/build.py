#!/usr/bin/env python3
"""Build the verified iPadOS16 arm64/arm64e tweak; never install/respring."""
import argparse
from pathlib import Path
import subprocess
import gzip
import io
import tarfile
import hashlib

ROOT = Path(__file__).resolve().parent
def archive(files):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as output:
        for name, data in files:
            entry = tarfile.TarInfo('./' + name)
            entry.size = len(data)
            entry.mode = 0o644
            entry.uid = entry.gid = entry.mtime = 0
            output.addfile(entry, io.BytesIO(data))
    return gzip.compress(stream.getvalue(), mtime=0)

CONTROL = '''Package: com.tony.netstatus
Name: Tony Native Network Speed
Version: 0.1.1
Architecture: iphoneos-arm64
Maintainer: widmonstertony
Author: widmonstertony
Section: Tweaks
Depends: firmware (>= 16.1), firmware (<< 16.2), mobilesubstrate, preferenceloader
Description: Verified native right-side status-bar download/upload speed on iPad14,6 iPadOS16.1. arm64/arm64e; SpringBoard only; no floating window, game injection or restart scripts.
Rootless: true
'''

def package(payload):
    members = [('debian-binary', b'2.0\n'),
        ('control.tar.gz', archive([('control', CONTROL.encode())])),
        ('data.tar.gz', archive([
            ('var/jb/usr/lib/TweakInject/TonyNetStatus.dylib', payload),
            ('var/jb/usr/lib/TweakInject/TonyNetStatus.plist', (ROOT/'TonyNetStatus.plist').read_bytes()),
            ('var/jb/Library/PreferenceLoader/Preferences/TonyNetStatus.plist', (ROOT/'Preferences.plist').read_bytes())]))]
    result = bytearray(b'!<arch>\n')
    for name, data in members:
        result += (name.ljust(16)+'0'.ljust(12)+'0'.ljust(6)+'0'.ljust(6)+
                   '100644'.ljust(8)+str(len(data)).ljust(10)+'`\n').encode()+data
        if len(data)%2: result += b'\n'
    return bytes(result)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', type=Path)
    p.add_argument('--signed-payload', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a=p.parse_args()
    if a.output.exists(): raise ValueError('Refusing overwrite')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    image=a.signed_payload
    if image and hashlib.sha256(image.read_bytes()).hexdigest()!='b7444c5f68a7dde89324d9e86ce9f9c90c936273f0beabea18db5040a279834b':
        raise ValueError('Not the verified device-signed release payload')
    if image is None:
        if a.sdk is None: p.error('--sdk required when compiling')
        for arch in ('arm64','arm64e'):
            subprocess.run(['xcrun','clang','-target',arch+'-apple-ios16.0',
                '-isysroot',str(a.sdk),'-Os','-Wall','-Wextra','-Werror','-fobjc-arc',
                '-dynamiclib','-framework','UIKit','-framework','Foundation',
                '-framework','CoreFoundation','-framework','CoreGraphics',
                '-Wl,-install_name,/var/jb/usr/lib/TweakInject/TonyNetStatus.dylib',
                '-o',str(a.output.parent/('TonyNetStatus-'+arch+'.dylib')),
                str(ROOT/'TonyNetStatus.m')],check=True)
        image=a.output.parent/'TonyNetStatus.dylib'
        subprocess.run(['xcrun','lipo','-create',
            str(a.output.parent/'TonyNetStatus-arm64.dylib'),
            str(a.output.parent/'TonyNetStatus-arm64e.dylib'),'-output',str(image)],check=True)
        subprocess.run(['codesign','-f','-s','-',str(image)],check=True)
    a.output.write_bytes(package(image.read_bytes()))
    print(a.output)

if __name__=='__main__': main()
