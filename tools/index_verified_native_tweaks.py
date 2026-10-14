#!/usr/bin/env python3
"""Append only the two accepted native tweak releases; preserve other stanzas.

This deliberately does not glob debs/: historical/unlisted binaries must not
accidentally become installable. No install, signing or device commands here.
"""
import bz2
import datetime
import email.utils
import gzip
import hashlib
import io
from pathlib import Path
import sys
import tarfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'sources/native-network-speed-1.1.0'))
from test_release import deb_members

RELEASES=[
    ('com.tony.netstatus','1.1.3','e855a4b3699d666bd807178766467a44aac38e82fd68be718230f6f252b6c4fa','native-network-speed.html'),
    ('com.tony.reversevolume','1.0.1','d6aa9a928e0267da7aa007e7b27ec9012a555ad5a2a3dda6d5be0b43128c2514','reverse-volume.html')]

def main():
    stanzas=(ROOT/'Packages').read_text().strip().split('\n\n')
    for package,version,accepted,depiction in RELEASES:
        filename=f'debs/{package}_{version}_iphoneos-arm64.deb'
        data=(ROOT/filename).read_bytes()
        assert hashlib.sha256(data).hexdigest()==accepted, 'Not the accepted DEB'
        members=deb_members(data)
        with tarfile.open(fileobj=io.BytesIO(members['control.tar.gz'])) as control:
            assert [x.name for x in control]==['./control'], 'Unexpected maintainer script'
            text=control.extractfile('./control').read().decode().strip()
        fields=dict(line.split(': ',1) for line in text.splitlines())
        assert fields['Package']==package and fields['Version']==version
        stanzas=[s for s in stanzas if not
                 (f'Package: {package}\n' in s+'\n' and f'Version: {version}\n' in s+'\n')]
        extra=f'\nDepiction: https://widmonstertony.github.io/tonyrepo/depictions/{depiction}\nFilename: {filename}\nSize: {len(data)}'
        for label,algorithm in [('MD5sum','md5'),('SHA1','sha1'),('SHA256','sha256')]:
            extra+=f'\n{label}: {hashlib.new(algorithm,data).hexdigest()}'
        stanzas.append(text+extra)
    data=('\n\n'.join(stanzas)+'\n').encode()
    (ROOT/'Packages').write_bytes(data)
    (ROOT/'Packages.gz').write_bytes(gzip.compress(data,mtime=0))
    (ROOT/'Packages.bz2').write_bytes(bz2.compress(data))
    header=(ROOT/'Release').read_text().split('MD5Sum:',1)[0]
    lines=header.rstrip().splitlines()
    date=email.utils.format_datetime(datetime.datetime.now(datetime.timezone.utc),usegmt=True)
    lines=[f'Date: {date}' if line.startswith('Date:') else line for line in lines]
    for label,algorithm in [('MD5Sum','md5'),('SHA1','sha1'),('SHA256','sha256')]:
        lines.append(label+':')
        for name in ['Packages','Packages.gz','Packages.bz2']:
            content=(ROOT/name).read_bytes()
            lines.append(f' {hashlib.new(algorithm,content).hexdigest()} {len(content)} {name}')
    (ROOT/'Release').write_text('\n'.join(lines)+'\n')
    print('Indexed only the two exact accepted DEBs; other package stanzas preserved')

if __name__=='__main__':main()
