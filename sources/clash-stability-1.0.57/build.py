#!/usr/bin/env python3
"""Release-only, hash-pinned 1.0.41 -> 1.0.57 binary adaptation source.

This is not the missing original C source. All original instruction changes
are listed in recipe.json. Unknown inputs stop before any output is written.
No third-party framework or jailbreak binaries are distributed here.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import tarfile

ROOT = Path(__file__).resolve().parent
RECIPE = json.loads((ROOT / 'recipe.json').read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path, key):
    data = Path(path).read_bytes()
    require(sha(data) == RECIPE[key], 'Unknown input profile: ' + key)
    return data


def text_range(data):
    require(struct.unpack_from('<I', data)[0] == 0xfeedfacf, 'Not a 64-bit Mach-O')
    offset = 32
    for _ in range(struct.unpack_from('<I', data, 16)[0]):
        command, size = struct.unpack_from('<II', data, offset)
        if command == 0x19:
            for i in range(struct.unpack_from('<I', data, offset + 64)[0]):
                section = offset + 72 + i * 80
                if data[section:section + 16].rstrip(b'\0') == b'__text':
                    start = struct.unpack_from('<I', data, section + 48)[0]
                    length = struct.unpack_from('<Q', data, section + 40)[0]
                    return start, start + length
        require(size >= 8, 'Invalid load command')
        offset += size
    raise ValueError('Missing __text')


def deb_members(path):
    data = Path(path).read_bytes()
    require(data[:8] == b'!<arch>\n', 'Not a DEB archive')
    members = {}
    pos = 8
    while pos < len(data):
        header = data[pos:pos + 60]
        require(header[58:60] == b'`\n', 'Invalid ar header')
        length = int(header[48:58])
        name = header[:16].decode().strip().rstrip('/')
        members[name] = data[pos + 60:pos + 60 + length]
        pos += 60 + length + length % 2
    return members


def release_payload(path):
    require(sha(Path(path).read_bytes()) == RECIPE['release_package_sha256'],
            'Not the verified release package')
    with tarfile.open(fileobj=io.BytesIO(deb_members(path)['data.tar.gz'])) as archive:
        for member in archive.getmembers():
            if member.name.lstrip('./') == 'var/jb/usr/lib/TweakInject/ClashTraceDiagnostic.dylib':
                data = archive.extractfile(member).read()
                require(sha(data) == RECIPE['release_payload_sha256'], 'Wrong release payload')
                return data
    raise ValueError('Missing release payload')


def adapt(baseline, dyld, systemhook_file):
    before = RECIPE['from_version'].encode()
    after = RECIPE['to_version'].encode()
    require(len(before) == len(after), 'Version string length changed')
    offsets = [i for i in range(len(baseline)) if baseline.startswith(before, i)]
    require(offsets == RECIPE['string_offsets'], 'Version string layout changed')
    adapted = bytearray(baseline.replace(before, after))
    old_uuid = bytes.fromhex('a5e8814d9cc431b9b7f857c13ff83e00')
    new_uuid = bytes.fromhex('f5db8dd883733e2eb74740a323510898')
    require(baseline.count(old_uuid) == 2, 'Systemhook UUID layout changed')
    adapted = bytearray(adapted.replace(old_uuid, new_uuid).replace(
        old_uuid.hex().encode(), new_uuid.hex().encode()))
    # Exact qualified startup namespace, UUID/export constants, full-file
    # digest words, and own-image worker complete-set checks. No global dyld
    # array edits, forced success, fatal suppression, or system-daemon hooks.
    for item in RECIPE['instruction_updates']:
        offset = item['offset']
        original = struct.unpack_from('<I', baseline, offset)[0]
        require(original == int(item['before'], 16), 'Instruction layout changed')
        struct.pack_into('<I', adapted, offset, int(item['after'], 16))
    require(struct.unpack_from('<II', dyld, 16) == (14, 0xaa8), 'Dyld header changed')
    require(struct.unpack_from('<II', dyld, 0xa70) == (0x1b, 24), 'Dyld UUID command moved')
    old_dyld_digest = bytes.fromhex('602efbe307fd3a4141436a927131c4681295478659ec57981c6b71795befc9d7')
    require(baseline[0x281c8:0x281e8] == old_dyld_digest, 'Old dyld digest changed')
    adapted[0x281c8:0x281e8] = hashlib.sha256(dyld[:0xac8]).digest()
    require(len(systemhook_file) == 0x38fc0, 'Systemhook file size changed')
    old_file_digest = bytes.fromhex('d9eea18e2e1f8d038f65753f8300331052a7a558f50ba81987bfd84a157b66f5')
    require(baseline[0x28028:0x28048] == old_file_digest, 'Old systemhook digest changed')
    adapted[0x28028:0x28048] = hashlib.sha256(systemhook_file).digest()
    # Kind 4 requires its own exact suffix; preserve root/identity checks.
    selector = struct.pack('<5I', 0x710012bf, 0x54000041, 0x10000068,
                           0xf90017e8, 0x1400341d)
    selector += b'/usr/lib/TweakInject/ClashTraceDiagnostic.dylib\0'
    require(not any(baseline[0x4000:0x4000 + len(selector)]), 'Selector padding not empty')
    adapted[0x4000:0x4000 + len(selector)] = selector
    start, end = text_range(baseline)
    expected_text = bytearray(baseline[start:end])
    for item in RECIPE['instruction_updates']:
        struct.pack_into('<I', expected_text, item['offset'] - start, int(item['after'], 16))
    require(adapted[start:end] == expected_text, 'Unlisted instruction change')
    return bytes(adapted)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default=ROOT / 'ClashTraceDiagnostic-baseline-1.0.41.dylib')
    parser.add_argument('--magicx', required=True)
    parser.add_argument('--systemhook-arm64e', required=True)
    parser.add_argument('--systemhook-file', required=True)
    parser.add_argument('--dyld', required=True)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--compare-release', type=Path)
    args = parser.parse_args()
    baseline = pinned(args.baseline, 'baseline_sha256')
    pinned(args.magicx, 'magicx_sha256')
    pinned(args.systemhook_arm64e, 'systemhook_arm64e_sha256')
    systemhook = pinned(args.systemhook_file, 'systemhook_file_sha256')
    dyld = pinned(args.dyld, 'dyld_sha256')
    adapted = adapt(baseline, dyld, systemhook)
    if args.compare_release:
        release = release_payload(args.compare_release)
        start, end = text_range(adapted)
        for begin, finish in [(start, end), (0x4000, 0x4050), (0x27200, 0x2bd48)]:
            require(adapted[begin:finish] == release[begin:finish],
                    'Adaptation differs from verified release logic/data')
        print('Verified release instructions, selector and constant-data regions match.')
    if not args.check_only:
        require(args.output is not None, 'Provide --output or --check-only')
        require(not args.output.exists(), 'Output already exists; refusing overwrite')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(adapted)
        print('Written unsigned adaptation. Original code signature is stale; sign before use.')
    print('Known binary profile matched; NOT proof of compatibility with a new app version.')


if __name__ == '__main__':
    main()
