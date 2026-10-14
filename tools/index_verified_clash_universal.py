#!/usr/bin/env python3
"""Publish exactly the accepted universal CoC package; retain rollback files."""
import bz2
import datetime
import email.utils
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'sources/clash-stability-universal-1.2.0'))
import package
ACCEPTED = '9b8a13a90b0b73b7bead956500dd63373b076403a6ecc0fbc651233cca7bcd39'


def main():
    receipt = json.loads((package.ROOT / 'verification.json').read_text())
    assert receipt['package_sha256'] == ACCEPTED
    assert all(d['village_visually_verified'] and d['user_confirmed_working']
               and d['original_payload_unchanged'] for d in receipt['devices'])
    assert len(receipt['devices']) == 2 and receipt['restart_performed'] is False
    filename = 'debs/com.codex.clashstability_1.2.0_iphoneos-arm64.deb'
    data = (ROOT / filename).read_bytes()
    assert hashlib.sha256(data).hexdigest() == ACCEPTED
    assert data == package.package(), 'Release must reproduce exact accepted bytes'
    members = package.old.deb_members(ROOT / filename)
    with tarfile.open(fileobj=io.BytesIO(members['control.tar.gz'])) as ar:
        assert [m.name for m in ar] == ['./control', './preinst', './postinst']
        text = ar.extractfile('./control').read().decode().strip()
    stanzas = (ROOT / 'Packages').read_text().strip().split('\n\n')
    original_other = [s for s in stanzas if next((line[9:] for line in s.splitlines()
                      if line.startswith('Package: ')), '')
                      not in ('com.codex.clashstability', 'com.codex.clashstability17')]
    stanzas = original_other[:]
    extra = '\nDepiction: https://widmonstertony.github.io/tonyrepo/depictions/clash-stability.html'
    extra += f'\nFilename: {filename}\nSize: {len(data)}'
    for label, algo in [('MD5sum', 'md5'), ('SHA1', 'sha1'), ('SHA256', 'sha256')]:
        extra += f'\n{label}: {hashlib.new(algo, data).hexdigest()}'
    stanzas.append(text + extra)
    content = ('\n\n'.join(stanzas) + '\n').encode()
    (ROOT / 'Packages').write_bytes(content)
    (ROOT / 'Packages.gz').write_bytes(gzip.compress(content, mtime=0))
    (ROOT / 'Packages.bz2').write_bytes(bz2.compress(content))
    lines = (ROOT / 'Release').read_text().split('MD5Sum:', 1)[0].rstrip().splitlines()
    date = email.utils.format_datetime(datetime.datetime.now(datetime.timezone.utc), usegmt=True)
    lines = [f'Date: {date}' if line.startswith('Date:') else line for line in lines]
    for label, algo in [('MD5Sum', 'md5'), ('SHA1', 'sha1'), ('SHA256', 'sha256')]:
        lines.append(label + ':')
        for name in ('Packages', 'Packages.gz', 'Packages.bz2'):
            blob = (ROOT / name).read_bytes()
            lines.append(f' {hashlib.new(algo, blob).hexdigest()} {len(blob)} {name}')
    (ROOT / 'Release').write_text('\n'.join(lines) + '\n')
    print('One CoC stanza; other package stanzas unchanged; historical files retained.')


if __name__ == '__main__':
    main()
