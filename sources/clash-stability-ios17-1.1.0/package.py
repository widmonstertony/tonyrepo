#!/usr/bin/env python3
"""Package the isolated iPadOS17 adapter. No maintainer/restart scripts."""
import argparse
from pathlib import Path
import sys
import hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'clash-stability-1.0.57'))
from repack import archive
CONTROL='''Package: com.codex.clashstability17
Name: Clash Stability iPadOS 17
Version: 1.1.0
Architecture: iphoneos-arm64
Maintainer: widmonstertony
Author: widmonstertony
Section: Tweaks
Priority: optional
Depends: firmware (>= 17.7.11), firmware (<< 17.7.12), mobilesubstrate
Conflicts: com.codex.clashstability, com.codex.clashid16refresh
Replaces: com.codex.clashstability, com.codex.clashid16refresh
Description: Isolated fingerprint gate for iPad7,2 iPadOS17.7.11 and the known Dopamine3.0.10 file profile. No forced-success checks, system hooks or restart scripts. Unrecognized binaries fail closed.
Rootless: true
'''
def package(payload):
    if hashlib.sha256(payload).hexdigest()!='af5aa166f22195bcc362375cdd3bed3803c16c216c22db3c017557665d47a44e':
        raise ValueError('Not the verified release payload')
    members=[('debian-binary',b'2.0\n'),('control.tar.gz',archive([('control',CONTROL.encode())])),
        ('data.tar.gz',archive([
            ('var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib',payload),
            ('var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.plist',
             (ROOT.parent/'clash-stability-1.0.57/ClashTraceDiagnostic.plist').read_bytes())]))]
    result=bytearray(b'!<arch>\n')
    for name,data in members:
        result+=(name.ljust(16)+'0'.ljust(12)+'0'.ljust(6)+'0'.ljust(6)+
                 '100644'.ljust(8)+str(len(data)).ljust(10)+'`\n').encode()+data
        if len(data)%2: result+=b'\n'
    return bytes(result)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--payload',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists(): raise ValueError('Refusing overwrite')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(package(a.payload.read_bytes()))
