#!/usr/bin/env python3
"""Build the candidate on top of the exact verified 1.0.57 release.

No release publication or installation occurs here. Only three version-call
sites and previously empty executable padding may change before signing.
"""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OLD_SOURCE = REPO / 'sources/clash-stability-1.0.57'
spec = importlib.util.spec_from_file_location('verified_source', OLD_SOURCE / 'build.py')
verified = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verified)
GATE = 0x4100
CALLS = (0x99fc, 0xe100, 0x14c64)


def sections(data):
    offset = 32
    for _ in range(struct.unpack_from('<I', data, 16)[0]):
        command, size = struct.unpack_from('<II', data, offset)
        if command == 0x19:
            for i in range(struct.unpack_from('<I', data, offset + 64)[0]):
                item = offset + 72 + i * 80
                name = data[item:item + 16].rstrip(b'\0').decode()
                address, length = struct.unpack_from('<QQ', data, item + 32)
                file_offset = struct.unpack_from('<I', data, item + 48)[0]
                yield name, address, data[file_offset:file_offset + length]
        offset += size


def branch_call(source, target):
    assert not (source % 4 or target % 4)
    return 0x94000000 | (((target - source) // 4) & 0x3ffffff)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Output exists; refusing overwrite'
    baseline = verified.release_payload(REPO / 'debs/com.codex.clashstability_1.0.57_iphoneos-arm64.deb')
    payload = ROOT / 'gate_payload.dylib'
    subprocess.run(['xcrun', 'clang', '-target', 'arm64-apple-ios16.0',
                    '-isysroot', str(args.sdk), '-Os', '-Wall', '-Wextra', '-Werror',
                    '-fno-stack-protector', '-ffreestanding', '-fno-builtin',
                    '-fno-asynchronous-unwind-tables', '-fno-unwind-tables',
                    '-nostdlib', '-dynamiclib', '-lSystem', '-Wl,-no_fixup_chains',
                    '-Wl,-no_compact_unwind', '-Wl,-no_uuid', '-Wl,-no_adhoc_codesign',
                    '-o', str(payload), str(ROOT / 'padding.S'), str(ROOT / 'gate.c')], check=True)
    symbols = subprocess.check_output(['nm', '-nm', str(payload)], text=True)
    assert '(undefined)' not in symbols, 'Payload must not introduce external imports'
    assert '0000000000004100 (__TEXT,__text) external _fingerprint_gate' in symbols
    result = bytearray(baseline)
    allowed = set()
    for name, address, data in sections(payload.read_bytes()):
        assert name in ('__text', '__const', '__cstring'), name
        if address == 0x4000:
            assert data[:0x100] == bytes(0x100)
            address, data = address + 0x100, data[0x100:]
        assert 0x4100 <= address and address + len(data) < 0x7db8
        assert not any(baseline[address:address + len(data)]), 'Not unused padding'
        result[address:address + len(data)] = data
        allowed.update(range(address, address + len(data)))
    for call in CALLS:
        assert struct.unpack_from('<I', baseline, call)[0] == branch_call(call, 0x26c30)
        struct.pack_into('<I', result, call, branch_call(call, GATE))
        allowed.update(range(call, call + 4))
    differences = [i for i, (a, b) in enumerate(zip(baseline, result)) if a != b]
    assert all(i in allowed for i in differences), 'Unexpected mutation'
    assert len(result) == len(baseline)
    assert result[0x4000:0x4050] == baseline[0x4000:0x4050], 'Own-image selector changed'
    assert result[0x27200:0x2c000] == baseline[0x27200:0x2c000], 'Original profile changed'
    args.output.write_bytes(result)
    subprocess.run(['codesign', '-f', '-s', '-', str(args.output)], check=True)
    signed = args.output.read_bytes()
    text_start, text_end = verified.text_range(baseline)
    assert signed[text_start:text_end] == result[text_start:text_end], 'Signing changed code'
    print('Only 3 version-comparison call sites and unused padding modified.')
    print('Candidate SHA256:', hashlib.sha256(signed).hexdigest())


if __name__ == '__main__':
    main()
