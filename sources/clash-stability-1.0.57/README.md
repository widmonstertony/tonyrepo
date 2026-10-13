# Clash Stability 1.0.57 — adaptation source / 适配代码

This directory contains the **release-only binary adaptation source**, the
complete instruction-change recipe, and a pinned previously verified 1.0.41
plugin image used as the build input. It is **not** the full original C source:
that source was not recovered during this repair. The baseline is a build
dependency, not a failed test package or another release to install.
Its hash also matches the payload in the previously published 1.0.41 DEB.

The published [1.0.57 DEB](../../debs/com.codex.clashstability_1.0.57_iphoneos-arm64.deb)
contains the exact device-signed payload tested in-game. The recipe pins its
SHA-256 and the DEB SHA-256. No failed 1.0.42–1.0.56 packages, diagnostic
observers, game binaries, jailbreak binaries, raw logs or memory dumps are
published with this release.

## Verified scope

- iPad14,6, iPadOS 16.1 (20B82), Dopamine 3.0.11, CoC 18.647.2.
- Village entered, game terminated and reopened to the village again, then
  the same process observed alive at three minutes. This is not a promise of
  indefinite stability. See [verification.json](verification.json).
- No device, userspace or SpringBoard restart; no jailbreak exit or game-data
  deletion. The installed payload has no temporary fatal/signal observer.
- This update is **not** a newly verified iOS 17 release. The older 1.0.41 APT
  entry remains available for its separately verified legacy configuration.

## Repair

The game update retained the exact `magicx` binary, while the Dopamine update
changed pinned systemhook identities, export location and file/header digests.
The remaining observed failure was check ID 16: the worker module snapshot
included this plugin's own image. The repair adds its exact kind-4 suffix to
the existing qualified mapping, changing the complete set from three images
(`0x62`) to four (`0x72`). Caller, frame, native readiness, image identity,
path, UUID and snapshot consistency checks are retained. No blanket success
override, global dyld-list modification, or system-daemon hook is added.

## Reproduce and compare

Python 3, standard library only. Supply your own lawfully obtained local
profile files; they are deliberately not redistributed here.

```sh
python3 build.py \
  --magicx /path/to/magicx \
  --systemhook-arm64e /path/to/systemhook-arm64e.dylib \
  --systemhook-file /path/to/systemhook.dylib \
  --dyld /path/to/dyld \
  --check-only \
  --compare-release ../../debs/com.codex.clashstability_1.0.57_iphoneos-arm64.deb
```

Replace `--check-only` with `--output build/ClashTraceDiagnostic.unsigned.dylib`
to write the adaptation. Its old signature is invalid after modification;
it must be signed appropriately for the target jailbreak before packaging.
Signing differences mean this unsigned output is not byte-for-byte identical
to the published signed image. The comparison checks the entire original
`__text`, new selector and relevant constant-data region against the exact
verified release. Use the published DEB for installation, not an unsigned build.

`repack.py --signed-payload /path/to/signed.dylib --output build/repacked.deb`
packages only the exact hash-pinned verified payload with the release control
and filter. It refuses unknown payloads and has no install/restart scripts.
Run `python3 test_release.py -v` to check the package, payload, baseline,
compressed APT indexes and Release checksums without changing the device.

## Future CoC updates

1.0.57 **still has an exact app-version gate**. The checker does not remove it
and does not auto-enable support for new versions. A version-number-only
update with unchanged protection and jailbreak fingerprints can be adapted
without repeating the entire investigation, but it still needs a launch test.
Changed protection modules, layouts or jailbreak inputs need a new profile.
Fingerprint-based runtime compatibility is a future improvement, not a feature
already shipped here; removing every guard would not be a reliable fix.

---

## 中文

这里提供这次正式修复对应的**二进制适配源代码**、逐条修改清单以及构建所需的
已验证 1.0.41 基线插件。**不是完整原始 C 源码**；本次没有找回它，不能把适配
脚本冒充完整源码。基线仅是构建输入，不是失败测试包，也不是建议安装的新版。

正式 DEB 使用实机签名且已验收的 1.0.57 payload：进入村庄、结束游戏后重新
进入村庄、同一进程存活至三分钟。测试不需要重启设备、用户空间或 SpringBoard，
不退出越狱，不清除游戏数据。这是当前组合的验证，不是永久稳定性保证。
新版仅验证 iPad14,6 / iPadOS 16.1 / Dopamine 3.0.11 / CoC 18.647.2，
不能据此宣称新版支持所有 iOS 16 或 iOS 17 设备。

问题包含旧的越狱环境指纹和插件自身被游戏的工作线程快照重复识别。
本次按精确自身身份/路径修正已有过滤集合，保留其他一致性校验，未直接强制
游戏“检查通过”、屏蔽致命信号或修改系统守护进程。失败测试包、诊断观察器、
游戏/系统文件、设备日志和内存转储均不上传。

上面的构建命令需自行提供本地文件；指纹不匹配直接停止。生成的是未签名适配
产物，安装请使用仓库中的正式 DEB。`repack.py` 仅接受已验收 payload 的精确
哈希，重新打包不会触发重启。

以后可以减少重复修复，但不能承诺每次更新自动兼容：当前 1.0.57 **仍限定游戏
版本号**。若只变版本号且防护模块/越狱指纹不变，通常只需小范围适配再验收；
如果模块或越狱环境变了，仍需新适配。按指纹自动兼容属于后续改进，尚未实现。
