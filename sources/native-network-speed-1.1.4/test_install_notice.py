#!/usr/bin/env python3
"""Run notice-only postinst with GUI and CLI environments; no device operations."""
import os
from pathlib import Path
import plistlib
import re
import subprocess

ROOT=Path(__file__).resolve().parent
body=(ROOT/'postinst').read_text()
for command in ['sbreload','killall','launchctl','ldrestart','finish:','eval ','exec ','>&','/proc/']:
    assert command not in body, command
assert not re.search(r'(?m)^\s*(?:/[^ ]*/)?reboot\b',body)
for extra in [{},{'SILEO':'6 1','CYDIA':'6 1'},{'SILEO':'invalid','CYDIA':'invalid'},{'SILEO':'6 1','AutoComplete':'true'}]:
    environment=os.environ.copy();environment.update(extra)
    r=subprocess.run(['/bin/sh',str(ROOT/'postinst'),'configure'],env=environment,text=True,capture_output=True,check=True)
    assert '安装完成' in r.stdout and 'manually restart SpringBoard' in r.stdout
    assert 'never restarts it automatically' in r.stdout and not r.stderr
    assert 'finish:' not in r.stdout
for arg in ['abort-upgrade','abort-remove','abort-deconfigure']:
    r=subprocess.run(['/bin/sh',str(ROOT/'postinst'),arg],text=True,capture_output=True,check=True)
    assert not r.stdout and not r.stderr
notice=plistlib.loads((ROOT/'InstallNotice.plist').read_bytes())['entry']
assert notice['cell']=='PSTitleValueCell'
assert '手动重启 SpringBoard' in notice['label']
assert set(notice)=={'cell','label'}
prior=ROOT.parent/'native-network-speed-1.1.3'
if not prior.exists():
    prior=ROOT.parent/'thermal-light-repo/sources/native-network-speed-1.1.3'
assert prior.exists()
for name in ['TonyNetStatus.m','TonyNetStatus.plist','Preferences.plist']:
    assert (ROOT/name).read_bytes()==(prior/name).read_bytes(),name
print('PASS bilingual notice, no finish action/restart command, abort no-op, static Settings row, unchanged runtime and existing switch')
