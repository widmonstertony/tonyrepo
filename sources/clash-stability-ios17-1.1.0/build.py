#!/usr/bin/env python3
"""Isolated iOS17 fingerprint adaptation. Does not alter the working iOS16 package."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
spec=importlib.util.spec_from_file_location('gate_builder',ROOT.parent/'clash-stability-1.0.58/build.py')
gate_builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate_builder)
BASELINE_SHA='f012cd05968b9d5b47ecc03507deda28b2f46c5cbb20dccd37ac394b2a45ac2f'
CALLS=(0x18974,0x1d378,0x245bc)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists(): raise ValueError('Refusing overwrite')
    baseline=(ROOT.parent/'clash-stability-1.0.57/ClashTraceDiagnostic-baseline-1.0.41.dylib').read_bytes()
    assert hashlib.sha256(baseline).hexdigest()==BASELINE_SHA
    a.output.parent.mkdir(parents=True,exist_ok=True)
    payload=a.output.parent/'gate_payload.dylib'
    subprocess.run(['xcrun','clang','-target','arm64-apple-ios16.0','-isysroot',str(a.sdk),
        '-Os','-Wall','-Wextra','-Werror','-fno-stack-protector','-ffreestanding','-fno-builtin',
        '-fno-asynchronous-unwind-tables','-fno-unwind-tables','-nostdlib','-dynamiclib','-lSystem',
        '-Wl,-no_fixup_chains','-Wl,-no_compact_unwind','-Wl,-no_uuid','-Wl,-no_adhoc_codesign',
        '-o',str(payload),str(ROOT/'padding.S'),str(ROOT/'gate.c')],check=True)
    symbols=subprocess.check_output(['nm','-nm',str(payload)],text=True)
    assert '(undefined)' not in symbols
    assert '0000000000004100 (__TEXT,__text) external _fingerprint_gate' in symbols
    result=bytearray(baseline);allowed=set()
    for name,address,data in gate_builder.sections(payload.read_bytes()):
        assert name in ('__text','__const','__cstring')
        if address==0x4000:
            assert data[:0x100]==bytes(0x100)
            address,data=address+0x100,data[0x100:]
        assert 0x4100<=address and address+len(data)<0x7db8
        assert not any(baseline[address:address+len(data)])
        result[address:address+len(data)]=data;allowed.update(range(address,address+len(data)))
    for call in CALLS:
        assert struct.unpack_from('<I',baseline,call)[0]==gate_builder.branch_call(call,0x26c30)
        struct.pack_into('<I',result,call,gate_builder.branch_call(call,0x4100))
        allowed.update(range(call,call+4))
    # Qualified own-image kind 4: exact native header, cached UUID/path,
    # same root and full exclusion-set checks as kinds 1/5/6. Never all tweaks.
    selector=struct.pack('<5I',0x710012bf,0x54000041,0x10000068,0xf90017e8,
                         0x14000000|(((0x20320-0x4010)//4)&0x3ffffff))
    selector+=b'/usr/lib/TweakInject/ClashTraceDiagnostic.dylib\0'
    assert not any(baseline[0x4000:0x4000+len(selector)])
    result[0x4000:0x4000+len(selector)]=selector
    allowed.update(range(0x4000,0x4000+len(selector)))
    changes=((0x20108,0x52800c4d,0x52800e4d),
             (0x2031c,0xf90017e8,0x14000000|(((0x4000-0x2031c)//4)&0x3ffffff)),
             (0x2049c,0x71000d1f,0x7100111f),
             (0x204b8,0x7101891f,0x7101c91f))
    for offset,before,after in changes:
        assert struct.unpack_from('<I',baseline,offset)[0]==before, hex(offset)
        struct.pack_into('<I',result,offset,after)
        allowed.update(range(offset,offset+4))
    assert all(i in allowed for i,(x,y) in enumerate(zip(baseline,result)) if x!=y)
    # No version-string rewrite: gate admits only exact file fingerprints.
    assert result[0x7db8:0x16be0]==baseline[0x7db8:0x16be0], 'iOS16 code changed'
    assert result[0x27200:0x2c000]==baseline[0x27200:0x2c000], 'Original constants changed'
    a.output.write_bytes(result)
    subprocess.run(['codesign','-f','-s','-',str(a.output)],check=True)
    print(a.output,hashlib.sha256(a.output.read_bytes()).hexdigest())

if __name__=='__main__': main()
