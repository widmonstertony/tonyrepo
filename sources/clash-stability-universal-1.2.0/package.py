#!/usr/bin/env python3
"""One installer, two exact accepted payloads; no runtime loader or new hooks."""
import argparse
import gzip
import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
spec = importlib.util.spec_from_file_location('old', ROOT.parent / 'clash-stability-1.0.57/build.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
PROFILES = {
    'ios16': ('com.codex.clashstability_1.0.58_iphoneos-arm64.deb',
              '3ad5ead8cf8b9aa0bb491e5e8509b1e65bda5ca9bfd26b42b1e2c88cf616d110',
              'd9dbc5299c92274bc6160ef1666678843d06ee24bf783a6344d97e4ec01a634f'),
    'ios17': ('com.codex.clashstability17_1.1.0_iphoneos-arm64.deb',
              'fe4712c49c21f6ef8abc23af3059dd6053b795cc588df52e196f92ef961d081b',
              'af5aa166f22195bcc362375cdd3bed3803c16c216c22db3c017557665d47a44e'),
}
CONTROL = '''Package: com.codex.clashstability
Name: Clash Stability
Version: 1.2.0
Architecture: iphoneos-arm64
Maintainer: widmonstertony
Author: widmonstertony
Section: Tweaks
Priority: optional
Depends: firmware (>= 16.0), firmware (<< 18.0), mobilesubstrate, coreutils
Conflicts: com.codex.clashstability17, com.codex.clashid16refresh
Replaces: com.codex.clashstability17, com.codex.clashid16refresh
Description: Single installer for verified iPad14,6/16.1 and iPad7,2/17.7.11 binary profiles. Selects one unchanged accepted runtime; unknown OS/device/jailbreak files refused. Close and reopen CoC; no reboot/respring actions.
Rootless: true
'''


def payloads():
    result = {}
    for profile, (filename, package_sha, payload_sha) in PROFILES.items():
        path = REPO / 'debs' / filename
        assert hashlib.sha256(path.read_bytes()).hexdigest() == package_sha
        members = old.deb_members(path)
        with tarfile.open(fileobj=io.BytesIO(members['data.tar.gz'])) as archive:
            files = {m.name.lstrip('./'): archive.extractfile(m).read()
                     for m in archive if m.isfile()}
        result[profile] = files['var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib']
        assert hashlib.sha256(result[profile]).hexdigest() == payload_sha
        assert files['var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.plist'] == (
            ROOT.parent / 'clash-stability-1.0.57/ClashTraceDiagnostic.plist').read_bytes()
    return result


def script(name):
    return b'#!/var/jb/usr/bin/sh\nset -eu\n' + (ROOT / 'profile.sh').read_bytes() + b'\n' + (ROOT / (name + '.body')).read_bytes()


def archive(files):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as out:
        directories = set()
        for name, data, mode in files:
            for parent in reversed(Path(name).parents):
                directory = parent.as_posix()
                if directory != '.' and directory not in directories:
                    entry = tarfile.TarInfo('./' + directory + '/')
                    entry.type, entry.mode = tarfile.DIRTYPE, 0o755
                    entry.uid = entry.gid = entry.mtime = 0
                    out.addfile(entry)
                    directories.add(directory)
            entry = tarfile.TarInfo('./' + name)
            entry.size, entry.mode = len(data), mode
            entry.uid = entry.gid = entry.mtime = 0
            out.addfile(entry, io.BytesIO(data))
    return gzip.compress(stream.getvalue(), mtime=0)


def package():
    profiles = payloads()
    # Own the injected path in dpkg's file list. configure atomically replaces
    # it with the selected unchanged profile. No dynamic target md5 is claimed.
    data = [('var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib', profiles['ios16'], 0o644),
            ('var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.plist',
             (ROOT.parent / 'clash-stability-1.0.57/ClashTraceDiagnostic.plist').read_bytes(), 0o644)]
    data += [(f'var/jb/usr/share/clash-stability/profiles/{name}.dylib', value, 0o644)
             for name, value in profiles.items()]
    control = [('control', CONTROL.encode(), 0o644)] + [
        (name, script(name), 0o755) for name in ('preinst', 'postinst')]
    members = [('debian-binary', b'2.0\n'), ('control.tar.gz', archive(control)), ('data.tar.gz', archive(data))]
    result = bytearray(b'!<arch>\n')
    for name, content in members:
        result += (name.ljust(16) + '0'.ljust(12) + '0'.ljust(6) + '0'.ljust(6) +
                   '100644'.ljust(8) + str(len(content)).ljust(10) + '`\n').encode() + content
        if len(content) % 2:
            result += b'\n'
    return bytes(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Refusing overwrite')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = package()
    args.output.write_bytes(result)
    print(hashlib.sha256(result).hexdigest(), args.output)
