#!/usr/bin/env python3
"""Offline archive, exact-payload and real shell-script fixture tests."""
import hashlib
import io
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
from unittest import TestCase, main
import package


class ReleaseTests(TestCase):
    def test_archive(self):
        data = package.package()
        self.assertEqual(data, package.package())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'release.deb'
            path.write_bytes(data)
            members = package.old.deb_members(path)
        with tarfile.open(fileobj=io.BytesIO(members['control.tar.gz'])) as ar:
            self.assertEqual([m.name for m in ar], ['./control', './preinst', './postinst'])
            for name in ('preinst', 'postinst'):
                self.assertEqual(ar.getmember('./' + name).mode, 0o755)
                self.assertEqual(ar.extractfile('./' + name).read(), package.script(name))
                for forbidden in (b'sbreload', b'killall', b'/reboot', b'finish:', b'launchctl', b'uicache'):
                    self.assertNotIn(forbidden, package.script(name))
        with tarfile.open(fileobj=io.BytesIO(members['data.tar.gz'])) as ar:
            injected = [m.name for m in ar if m.isfile() and '/TweakInject/' in m.name]
            self.assertEqual(len(injected), 2)  # one dylib and its original filter
            self.assertTrue(ar.getmember('./var/jb/usr/share/clash-stability/profiles').isdir())
            for name, (_, _, digest) in package.PROFILES.items():
                blob = ar.extractfile('./var/jb/usr/share/clash-stability/profiles/' + name + '.dylib').read()
                self.assertEqual(hashlib.sha256(blob).hexdigest(), digest)

    def test_maintainer_scripts(self):
        profiles = package.payloads()
        # Exercise the actual script text with only absolute filesystem/tool
        # paths and known environment fingerprints redirected to local fixtures.
        for model, build, selected in [('iPad14,6', '20B82', 'ios16'),
                                       ('iPad7,2', '21H461', 'ios17'),
                                       ('iPad7,2', '21H462', None),
                                       ('iPad99,1', '20B82', None)]:
            with self.subTest(model=model, build=build), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                sysctl = root / 'sysctl'
                sysctl.write_text(f'#!/bin/sh\ncase "$2" in hw.machine) echo {model};; kern.osversion) echo {build};; *) exit 1;; esac\n')
                sysctl.chmod(0o755)
                hook, dyld = root / 'hook', root / 'dyld'
                hook.write_bytes(b'fixture-hook')
                dyld.write_bytes(b'fixture-dyld')
                profile_dir = root / 'profiles'
                profile_dir.mkdir()
                target_dir = root / 'TweakInject'
                target_dir.mkdir()
                target = target_dir / 'ClashTraceDiagnostic.dylib'
                target.write_bytes(b'previous-installed-image')
                for name, blob in profiles.items():
                    (profile_dir / (name + '.dylib')).write_bytes(blob)

                def script(name):
                    text = package.script(name).decode().replace('#!/var/jb/usr/bin/sh\n', '#!/bin/sh\n')
                    text = text.replace('/var/jb/usr/sbin/sysctl', str(sysctl))
                    text = text.replace('/var/jb/basebin/systemhook.dylib', str(hook))
                    text = text.replace('/var/jb/basebin/gen/dyld', str(dyld))
                    for original in ('b4e9e7d352e53bf7e91ce8c56f985612f2606b993e1ef3a02a3b4e4f765285c5',
                                     'd9eea18e2e1f8d038f65753f8300331052a7a558f50ba81987bfd84a157b66f5'):
                        text = text.replace(original, hashlib.sha256(hook.read_bytes()).hexdigest())
                    for original in ('4c5df2d35feb85398d71dbdc62a8ccb5dc479af1993cac8bb555998677317f25',
                                     '7376f20cffb173ac297f030a4c6cce168b3215d00fbc8bb6d031a2b21ac2d5ad'):
                        text = text.replace(original, hashlib.sha256(b'fixture-dyld').hexdigest())
                    text = text.replace('/var/jb/usr/share/clash-stability/profiles', str(profile_dir))
                    text = text.replace('/var/jb/usr/lib/TweakInject', str(target_dir))
                    for command in ('cp', 'mv', 'chmod', 'mktemp', 'rm', 'sha256sum'):
                        resolved = shutil.which(command)
                        if command == 'sha256sum' and not resolved:
                            resolved = shutil.which('shasum') + ' -a 256'
                        text = text.replace('/var/jb/usr/bin/' + command, resolved)
                    return text

                def run(name, action):
                    result = subprocess.run(['/bin/sh', '-c', script(name), name, action],
                                            capture_output=True, text=True)
                    return result.returncode

                self.assertEqual(run('preinst', 'install'), 0 if selected else 1)
                self.assertEqual(run('postinst', 'configure'), 0 if selected else 1)
                self.assertEqual(target.read_bytes(), profiles[selected] if selected else b'previous-installed-image')
                if selected:
                    # One-byte corruption must fail before the atomic replace.
                    saved = target.read_bytes()
                    path = profile_dir / (selected + '.dylib')
                    bad = bytearray(path.read_bytes()); bad[100] ^= 1; path.write_bytes(bad)
                    self.assertNotEqual(run('postinst', 'configure'), 0)
                    self.assertEqual(target.read_bytes(), saved)
                    dyld.write_bytes(b'unknown-jailbreak')
                    self.assertNotEqual(run('preinst', 'upgrade'), 0)
                    self.assertEqual(target.read_bytes(), saved)
                    self.assertFalse(list(target_dir.glob('.clash-profile.*')))


if __name__ == '__main__':
    main()
