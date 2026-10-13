#!/usr/bin/env python3
"""Repack only the exact verified, device-signed release payload."""
import argparse
import gzip
import io
from pathlib import Path
import tarfile
from build import ROOT, RECIPE, pinned, require


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


def package(payload):
    control = (ROOT / 'control').read_bytes()
    plist = (ROOT / 'ClashTraceDiagnostic.plist').read_bytes()
    members = [('debian-binary', b'2.0\n'),
               ('control.tar.gz', archive([('control', control)])),
               ('data.tar.gz', archive([
                   ('var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib', payload),
                   ('var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.plist', plist)]))]
    result = bytearray(b'!<arch>\n')
    for name, data in members:
        header = (name.ljust(16) + '0'.ljust(12) + '0'.ljust(6) +
                  '0'.ljust(6) + '100644'.ljust(8) + str(len(data)).ljust(10) + '`\n')
        result += header.encode() + data
        if len(data) % 2:
            result += b'\n'
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--signed-payload', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    payload = pinned(args.signed_payload, 'release_payload_sha256')
    require(not args.output.exists(), 'Output exists; refusing overwrite')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(package(payload))
    print('Repacked exact verified payload; container bytes may differ, payload signature preserved.')


if __name__ == '__main__':
    main()
