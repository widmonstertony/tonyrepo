#!/usr/bin/env python3
"""Build the hardware-key adapter candidate; never install or restart."""
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

CONTROL = '''Package: com.tony.reversevolume
Name: Tony Reverse Volume Keys
Version: 1.0.1
Architecture: iphoneos-arm64
Maintainer: widmonstertony
Author: widmonstertony
Section: Tweaks
Depends: firmware (>= 17.7.11), firmware (<< 17.7.12), mobilesubstrate, preferenceloader
Description: Reverses hardware volume keys in landscape and preserves portrait on qualified iPad7,2 iPadOS17.7.11, using actual outer-display window orientation instead of embedded app orientation. SpringBoard only; no game injection, audio-session override or restart scripts.
Rootless: true
'''

def package(payload):
    members = [('debian-binary', b'2.0\n'),
        ('control.tar.gz', archive([('control', CONTROL.encode())])),
        ('data.tar.gz', archive([
            ('var/jb/usr/lib/TweakInject/TonyReverseVolume.dylib', payload),
            ('var/jb/usr/lib/TweakInject/TonyReverseVolume.plist', (ROOT/'TonyReverseVolume.plist').read_bytes()),
            ('var/jb/Library/PreferenceLoader/Preferences/TonyReverseVolume.plist', (ROOT/'Preferences.plist').read_bytes()),
            ('var/jb/Library/PreferenceLoader/Preferences/TonyReverseVolumeLandscape.plist', (ROOT/'LandscapePreferences.plist').read_bytes())]))]
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
    if image and hashlib.sha256(image.read_bytes()).hexdigest()!='84888c4fcd082d75ca798cbc16156f36707c88a130125b5c9d2d8131fa0963f4':
        raise ValueError('Not the accepted device-signed volume release payload')
    if image is None:
        if a.sdk is None: p.error('--sdk required when compiling')
        for arch in ('arm64','arm64e'):
            subprocess.run(['xcrun','clang','-target',arch+'-apple-ios16.0',
                '-isysroot',str(a.sdk),'-Os','-Wall','-Wextra','-Werror','-fobjc-arc',
                '-dynamiclib','-framework','UIKit','-framework','Foundation',
                '-framework','CoreFoundation','-framework','CoreGraphics',
                '-Wl,-install_name,/var/jb/usr/lib/TweakInject/TonyReverseVolume.dylib',
                '-o',str(a.output.parent/('TonyReverseVolume-'+arch+'.dylib')),
                str(ROOT/'TonyReverseVolume.m')],check=True)
        image=a.output.parent/'TonyReverseVolume.dylib'
        subprocess.run(['xcrun','lipo','-create',
            str(a.output.parent/'TonyReverseVolume-arm64.dylib'),
            str(a.output.parent/'TonyReverseVolume-arm64e.dylib'),'-output',str(image)],check=True)
        subprocess.run(['codesign','-f','-s','-',str(image)],check=True)
    a.output.write_bytes(package(image.read_bytes()))
    print(a.output)

if __name__=='__main__': main()
